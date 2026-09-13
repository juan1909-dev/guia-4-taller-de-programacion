import logging
import os

# Asegurar que la carpeta logs exista
os.makedirs("logs", exist_ok=True)

def setup_logger():
    logger = logging.getLogger("AppLogger")
    logger.setLevel(logging.INFO)
    
    # Evitar duplicidad de handlers si se recarga el módulo
    if logger.hasHandlers():
        logger.handlers.clear()

    # Formato del log exigido en la guía
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # Handler para archivo
    file_handler = logging.FileHandler("logs/app.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Handler para consola
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger

logger = setup_logger()