# database_module.py
import sqlite3
from config import DATABASE_PATH

def crear_conexion():
    """Crea una conexión a la base de datos SQLite3."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

def crear_tablas():
    """Crea las tablas necesarias si no existen."""
    conn = crear_conexion()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS screenshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    filepath TEXT NOT NULL
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    screenshot_id INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    summary TEXT,
                    FOREIGN KEY (screenshot_id) REFERENCES screenshots(id)
                );
            """)
            conn.commit()
            print("Tablas creadas o ya existentes.")
        except sqlite3.Error as e:
            print(f"Error al crear tablas: {e}")
        finally:
            conn.close()

def guardar_screenshot_db(filepath):
    """Guarda la información de una captura de pantalla en la base de datos."""
    conn = crear_conexion()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO screenshots (filepath) VALUES (?)", (filepath,))
            screenshot_id = cursor.lastrowid # Obtiene el ID de la captura recién insertada
            conn.commit()
            print(f"Screenshot guardada en BD con ID: {screenshot_id}, filepath: {filepath}")
            return screenshot_id
        except sqlite3.Error as e:
            print(f"Error al guardar screenshot en BD: {e}")
            return None
        finally:
            conn.close()

def guardar_resumen_analisis_db(screenshot_id, summary):
    """Guarda el resumen del análisis en la base de datos."""
    conn = crear_conexion()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO analysis_summaries (screenshot_id, summary) VALUES (?, ?)", (screenshot_id, summary))
            conn.commit()
            print(f"Resumen de análisis guardado para screenshot ID: {screenshot_id}")
        except sqlite3.Error as e:
            print(f"Error al guardar resumen de análisis en BD: {e}")
        finally:
            conn.close()


if __name__ == '__main__':
    crear_tablas() # Para probar la creación de tablas directamente