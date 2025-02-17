# email_module.py
import smtplib
from email.mime.text import MIMEText
from config import EMAIL_SENDER, EMAIL_RECEIVER, EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT, EMAIL_SMTP_USERNAME, EMAIL_SMTP_PASSWORD

def enviar_email(resumen_texto):
    """Envía un correo electrónico con el resumen del análisis."""
    msg = MIMEText(resumen_texto, 'plain')
    msg['Subject'] = 'Resumen de Actividad del Usuario - Análisis de Pantalla'
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    server = None  # Inicializar server fuera del bloque try
    try:
        server = smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SMTP_USERNAME, EMAIL_SMTP_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print("Correo electrónico enviado correctamente!")
    except Exception as e:
        print(f"Error al enviar correo electrónico: {e}")
    finally:
        try: # Añadimos un try-except al intentar cerrar la conexión
            if server: # Verificamos si el servidor se inicializó antes de intentar cerrarlo
                server.quit()
        except Exception as e_quit:
            print(f"Error al cerrar la conexión SMTP (quit): {e_quit}")

if __name__ == '__main__':
    enviar_email()