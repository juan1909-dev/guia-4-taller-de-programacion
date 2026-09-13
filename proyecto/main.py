from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
import time
from logger_config import logger

app = FastAPI(title="API Gestión de Productos - DevOps & Observabilidad", version="1.0.0")

# Estructura de datos en memoria para los productos
class Producto(BaseModel):
    id: int
    nombre: str
    precio: float
    stock: int

# Base de datos simulada inicial
db_productos = [
    joven for joven in [
        {"id": 1, "nombre": "Laptop Gamer", "precio": 3500.0, "stock": 5},
        {"id": 2, "nombre": "Mouse Inalámbrico", "precio": 75.0, "stock": 25},
        {"id": 3, "nombre": "Teclado Mecánico", "precio": 120.0, "stock": 10}
    ]
]

# Diccionario para almacenar métricas básicas de la aplicación
metricas = {
    "total_peticiones": 0,
    "consultas_exitosas": 0,
    "productos_registrados": 0,
    "productos_eliminados": 0,
    "errores_servidor": 0
}

@app.middleware("http")
async def medir_tiempo_y_registrar(request: Request, call_next):
    metricas["total_peticiones"] += 1
    inicio = time.time()
    response = await call_next(request)
    duracion = time.time() - inicio
    
    # Ejemplo de traza/métrica por petición en consola
    logger.info(f"METRICA Ruta: {request.url.path} | Metodo: {request.method} | Duracion: {duracion:.4f}s | Status: {response.status_code}")
    return response

# FUNCIONALIDAD 1: Consultar productos (o uno en específico)
@app.get("/productos", response_model=List[Producto])
def consultar_productos():
    logger.info("GET /productos - Consulta exitosa de todos los productos")
    metricas["consultas_exitosas"] += 1
    return db_productos

@app.get("/productos/{producto_id}", response_model=Producto)
def consultar_producto_por_id(producto_id: int):
    # Situación de prueba 1: Consultar un registro inexistente
    producto = next((p for p in db_productos if p["id"] == producto_id), None)
    if not producto:
        logger.error(f"GET /productos/{producto_id} - Producto no encontrado")
        metricas["errores_servidor"] += 1
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    logger.info(f"GET /productos/{producto_id} - Consulta exitosa")
    metricas["consultas_exitosas"] += 1
    return producto

# FUNCIONALIDAD 2: Registrar producto
@app.post("/productos", status_code=201)
def registrar_producto(producto: Producto):
    # Situación de prueba 2: Validar información duplicada o incompleta (manejada automáticamente por Pydantic, pero la reforzamos)
    if any(p["id"] == producto.id for p in db_productos):
        logger.error(f"POST /productos - El ID {producto.id} ya existe")
        metricas["errores_servidor"] += 1
        raise HTTPException(status_code=400, detail="El ID del producto ya existe")
    
    db_productos.append(producto.model_dump())
    logger.info(f"POST /productos - Producto registrado exitosamente ID: {producto.id}")
    metricas["productos_registrados"] += 1
    return {"mensaje": "Producto registrado exitosamente", "producto": producto}

# FUNCIONALIDAD 3: Eliminar producto
@app.delete("/productos/{producto_id}")
def eliminar_producto(producto_id: int):
    global db_productos
    producto = next((p for p in db_productos if p["id"] == producto_id), None)
    
    if not producto:
        logger.error(f"DELETE /productos/{producto_id} - Intento de eliminar producto inexistente")
        metricas["errores_servidor"] += 1
        raise HTTPException(status_code=404, detail="Producto no encontrado para eliminar")
    
    db_productos = [p for p in db_productos if p["id"] != producto_id]
    logger.info(f"DELETE /productos/{producto_id} - Producto eliminado exitosamente")
    metricas["productos_eliminados"] += 1
    return {"mensaje": f"Producto con ID {producto_id} eliminado correctamente"}

# Endpoint extra para consultar las métricas requeridas en el Paso 4
@app.get("/metrics")
def obtener_metricas():
    logger.info("GET /metrics - Consulta de métricas del sistema")
    return {
        "metricas_sistema": metricas,
        "descripcion": "Métricas orientadas a evaluar disponibilidad, rendimiento y uso de recursos de la API."
    }