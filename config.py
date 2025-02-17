# config.py
import os
from dotenv import load_dotenv

load_dotenv()
# Configuración de la base de datos SQLite3
DATABASE_NAME = os.getenv("DATABASE_NAME") # Nombre de la base de datos
DATABASE_PATH = os.path.join(os.getcwd(), DATABASE_NAME)

# Configuración del intervalo de análisis (en segundos)
ANALYSIS_INTERVAL_SECONDS = os.getenv("ANALYSIS_INTERVAL_SECONDS") # Intervalo de análisis

# Configuración del correo electrónico (reemplaza con tus datos)
EMAIL_SENDER = os.getenv("EMAIL_FROM") # Correo electrónico del remitente
EMAIL_RECEIVER = os.getenv("EMAIL_TO") # Correo electrónico del destinatario
EMAIL_SMTP_SERVER = os.getenv("SMTP_SERVER") # Servidor SMTP
EMAIL_SMTP_PORT = os.getenv("SMTP_PORT") # Puerto SMTP
EMAIL_SMTP_USERNAME = os.getenv("SMTP_USERNAME") # Usuario SMTP
EMAIL_SMTP_PASSWORD = os.getenv("SMTP_PASSWORD") # Contraseña SMTP

# Directorio para guardar las capturas de pantalla (opcional)
SCREENSHOTS_DIR = 'screenshots'
if not os.path.exists(SCREENSHOTS_DIR):
    os.makedirs(SCREENSHOTS_DIR)