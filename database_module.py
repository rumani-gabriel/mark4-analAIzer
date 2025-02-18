# database_module.py
import sqlite3
import os
from config import DATABASE_PATH, FIREBASE_CREDENTIALS_PATH, DISPOSITIVO # Importar DISPOSITIVO desde config
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import logging
from datetime import datetime


logger = logging.getLogger(__name__) # Logger para este módulo

# --- Configuración de la Base de Datos SQLite ---
def crear_conexion():
    """Crea y retorna una conexión a la base de datos SQLite."""
    conexion = None
    try:
        conexion = sqlite3.connect(DATABASE_PATH)
        logger.info(f"Conexión a la base de datos SQLite creada exitosamente en: {DATABASE_PATH}")
    except sqlite3.Error as e:
        logger.error(f"Error al conectar a la base de datos SQLite: {e}")
    return conexion

def crear_tablas():
    """Crea las tablas 'screenshots' y 'analysis_summaries' en la base de datos SQLite si no existen."""
    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS screenshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    filepath TEXT UNIQUE NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    screenshot_id INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    summary TEXT,
                    dispositivo TEXT,  -- NUEVA COLUMNA 'dispositivo'
                    FOREIGN KEY (screenshot_id) REFERENCES screenshots(id)
                )
            """)
            conexion.commit()
            logger.info("Tablas 'screenshots' y 'analysis_summaries' creadas o verificadas en SQLite.")
        except sqlite3.Error as e:
            logger.error(f"Error al crear tablas en la base de datos SQLite: {e}")
        finally:
            conexion.close()

def guardar_screenshot_db(filepath):
    """Guarda la información de una screenshot en la base de datos SQLite y retorna su ID."""
    conexion = crear_conexion()
    screenshot_id = None
    if conexion:
        cursor = conexion.cursor()
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO screenshots (timestamp, filepath) VALUES (?, ?)", (timestamp, filepath))
            screenshot_id = cursor.lastrowid # Obtener el ID asignado automáticamente
            conexion.commit()
            logger.info(f"Screenshot guardada en SQLite: {filepath}, ID: {screenshot_id}")
        except sqlite3.Error as e:
            logger.error(f"Error al guardar screenshot en SQLite: {e}")
        finally:
            conexion.close()
    return screenshot_id

def guardar_resumen_analisis_db(screenshot_id, summary):
    """Guarda el resumen del análisis de una screenshot en la base de datos SQLite."""
    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO analysis_summaries (screenshot_id, timestamp, summary, dispositivo)
                VALUES (?, ?, ?, ?)  -- Incluir 'dispositivo' en la inserción
            """, (screenshot_id, timestamp, summary, DISPOSITIVO)) # Usar la variable DISPOSITIVO de config
            conexion.commit()
            logger.info(f"Resumen de análisis guardado en SQLite para screenshot ID {screenshot_id}, dispositivo: {DISPOSITIVO}")
        except sqlite3.Error as e:
            logger.error(f"Error al guardar resumen de análisis en SQLite: {e}")
        finally:
            conexion.close()

# --- Configuración e Interacción con Firebase Realtime Database ---
firebase_app = None # Variable global para la app de Firebase inicializada

def inicializar_firebase_db():
    """Inicializa la conexión con Firebase Realtime Database usando las credenciales."""
    global firebase_app # Usa la variable global
    if firebase_app: # Si ya está inicializada, no hacer nada
        return firebase_app

    cred = None
    if FIREBASE_CREDENTIALS_PATH:
        try:
            cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
        except Exception as e:
            logger.error(f"Error al cargar las credenciales de Firebase desde la ruta: {FIREBASE_CREDENTIALS_PATH}. Asegúrate de que la ruta sea correcta y el archivo exista. Error: {e}", exc_info=True)
            return None # No se pudo inicializar Firebase si las credenciales fallan
    else:
        logger.error("Ruta al archivo de credenciales de Firebase no configurada. Define FIREBASE_CREDENTIALS_PATH en .env o variables de entorno.")
        return None # No se pudo inicializar Firebase si no hay ruta de credenciales

    try:
        firebase_app = firebase_admin.initialize_app(cred, {
            'databaseURL': 'URL_DE_TU_BASE_DE_DATOS_FIREBASE'  # *** ¡REEMPLAZAR CON TU URL DE FIREBASE! ***
        })
        logger.info("Conexión a Firebase Realtime Database inicializada exitosamente.")
        return firebase_app
    except Exception as e:
        logger.error(f"Error al inicializar la aplicación de Firebase Admin: {e}", exc_info=True)
        return None

def guardar_descripcion_firebase(screenshot_id, descripcion):
    """Guarda la descripción de una screenshot en Firebase Realtime Database."""
    firebase_app = inicializar_firebase_db() # Intenta inicializar Firebase si no lo está
    if not firebase_app:
        logger.error("No se pudo guardar la descripción en Firebase porque la inicialización falló.")
        return False

    try:
        ref = db.reference(f'/screenshots_analisis/{DISPOSITIVO}/{screenshot_id}') # Ruta en Firebase incluyendo DISPOSITIVO
        ref.child('descripcion_ia').set(descripcion) # Guarda la descripción bajo el nodo 'descripcion_ia'
        ref.child('dispositivo').set(DISPOSITIVO) # Guarda el nombre del dispositivo
        logger.info(f"Descripción de análisis para screenshot ID {screenshot_id}, dispositivo: {DISPOSITIVO} guardada en Firebase.")
        return True
    except Exception as e:
        logger.error(f"Error al guardar descripción en Firebase para screenshot ID {screenshot_id}: {e}", exc_info=True)
        return False

def guardar_resumen_firebase(resumen_global_ia):
    """Guarda el resumen global del análisis en Firebase Realtime Database."""
    firebase_app = inicializar_firebase_db() # Intenta inicializar Firebase si no lo está
    if not firebase_app:
        logger.error("No se pudo guardar el resumen global en Firebase porque la inicialización falló.")
        return False

    try:
        timestamp_str_firebase = datetime.now().strftime("%Y-%m-%d_%H:%M:%S") # Formato para Firebase (compatible con nodos)
        ref = db.reference(f'/resumenes_globales/{DISPOSITIVO}/{timestamp_str_firebase}') # Ruta para resúmenes globales, incluyendo DISPOSITIVO y timestamp
        ref.set({
            'dispositivo': DISPOSITIVO, # Guarda el nombre del dispositivo en el resumen global
            'resumen': resumen_global_ia  # Guarda el resumen global IA bajo el nodo 'resumen'
        })
        logger.info(f"Resumen global de análisis guardado en Firebase para dispositivo: {DISPOSITIVO}.")
        return True
    except Exception as e:
        logger.error(f"Error al guardar resumen global en Firebase: {e}", exc_info=True)
        return False


if __name__ == '__main__':
    # --- Configuración básica de logging para pruebas ---
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    crear_tablas() # Asegurar que las tablas SQLite existen

   