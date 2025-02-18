# main.py
import time
import schedule
from datetime import datetime
import logging
import os
import platform

# Modulos propios
import screenshot_module # CORREGIDO: Importar screenshot_module en lugar de screenshot
import ai_analysis_module # Asegúrate de tener este modulo (aunque sea un placeholder)
import database_module
import email_module
import summary_module # NUEVO: Importar summary_module
from config import ANALYSIS_INTERVAL_SECONDS, DISPOSITIVO,SCREENSHOTS_DIR # Importar DISPOSITIVO desde config

# --- Configuración de logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def ejecutar_analisis_completo():
    """
    Ejecuta el proceso completo de análisis:
    1. Captura screenshots.
    2. Realiza análisis con IA (módulo ai_analysis_module).
    3. Guarda resultados en base de datos SQLite y Firebase.
    4. Genera resumen y envia email (opcional).
    """
    inicio_captura = datetime.now()
    logger.info(f"[{DISPOSITIVO}] Iniciando análisis completo a las {inicio_captura.strftime('%Y-%m-%d %H:%M:%S')}") # Incluir DISPOSITIVO en logs

    # 1. Captura de screenshots (multiples capturas en un intervalo)
    tiempo_inicio_intervalo = time.time()
    rutas_screenshots = []
    while time.time() - tiempo_inicio_intervalo < int(ANALYSIS_INTERVAL_SECONDS):
        filepath_screenshot = capturar_pantalla()
        if filepath_screenshot:
            rutas_screenshots.append(filepath_screenshot)
        time.sleep(2) # Pausa breve entre capturas individuales

    if not rutas_screenshots:
        logger.warning(f"[{DISPOSITIVO}] No se pudieron capturar screenshots. Abortando análisis.") # Incluir DISPOSITIVO en logs
        return

    logger.info(f"[{DISPOSITIVO}] Captura de {len(rutas_screenshots)} screenshots realizada.") # Incluir DISPOSITIVO en logs

    # 2. Análisis de las screenshots con IA (usando ai_analysis_module)
    try:
        resumen_global_ia = ai_analysis_module.analizar_conjunto_screenshots(rutas_screenshots) # Analizar el conjunto de rutas
        logger.info(f"[{DISPOSITIVO}] Análisis de IA completado. Resumen: {resumen_global_ia}") # Incluir DISPOSITIVO en logs
    except Exception as e:
        logger.error(f"[{DISPOSITIVO}] Error durante el análisis de IA: {e}", exc_info=True) # Incluir DISPOSITIVO en logs
        resumen_global_ia = "Error en el análisis de IA." # Resumen de error en caso de fallo

    # 3. Guardar resultados en base de datos (SQLite y Firebase)
    screenshot_ids_sqlite = [] # Para guardar los IDs de SQLite y relacionar con Firebase si es necesario

    for filepath in rutas_screenshots:
        screenshot_id_sqlite = database_module.guardar_screenshot_db(filepath) # Guardar en SQLite y obtener ID
        if screenshot_id_sqlite:
            screenshot_ids_sqlite.append(screenshot_id_sqlite)
             # --- Guardar DESCRIPCIÓN (individual por screenshot) en Firebase (OPCIONAL - por ahora no tenemos descripciones individuales) ---
             # Por ahora no tenemos descripciones individuales generadas por la IA para cada screenshot
             # Si ai_analysis_module devolviera descripciones individuales, aquí las guardaríamos en Firebase
             # Ejemplo (hipotético):
             # descripcion_ia_screenshot = ai_analysis_module.analizar_screenshot_individual(filepath)
             # if descripcion_ia_screenshot:
             #     database_module.guardar_descripcion_firebase(screenshot_id_sqlite, descripcion_ia_screenshot)

    # Guardar RESUMEN GLOBAL (del conjunto de screenshots) en SQLite y Firebase
    if screenshot_ids_sqlite: # Solo guardar resumen si hay screenshots asociadas
        # --- Guardar RESUMEN GLOBAL en SQLite ---
        # NOTA IMPORTANTE:  En la version anterior, guardabas un resumen POR CADA screenshot en SQLite
        #                   Ahora, parece que quieres guardar UN RESUMEN GLOBAL por cada ejecución de `ejecutar_analisis_completo`
        #                   He comentado la linea antigua y he dejado la linea para guardar el resumen global.
        #                   Si querias el comportamiento antiguo (resumen por screenshot),  habria que ajustarlo.
        # resumen_guardado_sqlite = database_module.guardar_resumen_analisis_db(screenshot_id_sqlite, resumen_global_ia) # ANTERIOR:  Asociado a la ULTIMA screenshot (incorrecto)
        # --- Guardar RESUMEN GLOBAL en SQLite (NUEVO -  Asociado a TODAS las screenshots del intervalo, usando el ID de la primera screenshot) ---
        resumen_guardado_sqlite = database_module.guardar_resumen_analisis_db(screenshot_ids_sqlite[0] if screenshot_ids_sqlite else None, resumen_global_ia) # NUEVO: Asociado al PRIMER screenshot del lote (o None si no hay screenshots)


        if resumen_guardado_sqlite:
            logger.info(f"[{DISPOSITIVO}] Resumen global guardado en SQLite para screenshots con IDs (primer ID): {screenshot_ids_sqlite[0] if screenshot_ids_sqlite else 'Ninguno'}") # Incluir DISPOSITIVO en logs
        else:
            logger.warning(f"[{DISPOSITIVO}] Error al guardar resumen global en SQLite.") # Incluir DISPOSITIVO en logs

        # --- Guardar RESUMEN GLOBAL en Firebase ---
        resumen_guardado_firebase = database_module.guardar_resumen_firebase(resumen_global_ia)
        if resumen_guardado_firebase:
            logger.info(f"[{DISPOSITIVO}] Resumen global guardado en Firebase exitosamente.") # Incluir DISPOSITIVO en logs
        else:
            logger.warning(f"[{DISPOSITIVO}] Error al guardar resumen global en Firebase.") # Incluir DISPOSITIVO en logs
    else:
        logger.warning(f"[{DISPOSITIVO}] No hay screenshot_ids de SQLite disponibles para guardar el resumen.") # Incluir DISPOSITIVO en logs


    # 4. Generar resumen de email y enviar (opcional)
    # --- Generar resumen de email (NUEVO - usando summary_module) ---
    resumen_email_texto = summary_module.generar_resumen_email({"conjunto_pantallas": resumen_global_ia}) # NUEVO: Usar summary_module
    if resumen_email_texto:
        logger.info(f"[{DISPOSITIVO}] Resumen de email generado:\n{resumen_email_texto}") # Incluir DISPOSITIVO en logs
        email_module.enviar_email(resumen_email_texto)
        logger.info(f"[{DISPOSITIVO}] Email enviado exitosamente.") # Incluir DISPOSITIVO en logs
    else:
        logger.warning(f"[{DISPOSITIVO}] No se pudo generar el resumen de email.") # Incluir DISPOSITIVO en logs


    fin_analisis = datetime.now()
    duracion_analisis_segundos = (fin_analisis - inicio_captura).total_seconds()
    logger.info(f"[{DISPOSITIVO}] Análisis completo finalizado a las {fin_analisis.strftime('%Y-%m-%d %H:%M:%S')}. Duración: {duracion_analisis_segundos:.2f} segundos") # Incluir DISPOSITIVO en logs
    logger.info("-" * 50) # Separador para logs


def capturar_pantalla():
    """
    Captura una screenshot de la pantalla dependiendo del sistema operativo.
    Guarda la screenshot en un archivo y retorna la ruta del archivo.
    """
    sistema_operativo = platform.system()
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"screenshot_{DISPOSITIVO}_{timestamp_str}.png" # Incluir DISPOSITIVO en el nombre del archivo
    ruta_completa = os.path.join(SCREENSHOTS_DIR, nombre_archivo)

    if sistema_operativo == "Linux":
        try:
            screenshot_module.capturar_pantalla_linux(ruta_completa) # CORREGIDO: Llamar a screenshot_module.capturar_pantalla_linux
            logger.info(f"[{DISPOSITIVO}] Screenshot guardada en: {ruta_completa} (Linux)") # Incluir DISPOSITIVO en logs
            return ruta_completa
        except Exception as e:
            logger.error(f"[{DISPOSITIVO}] Error al capturar screenshot en Linux: {e}") # Incluir DISPOSITIVO en logs
            return None
    elif sistema_operativo == "Windows":
        try:
            from PIL import ImageGrab # Importar solo en Windows
            screenshot_pil = ImageGrab.grab()
            screenshot_pil.save(ruta_completa)
            logger.info(f"[{DISPOSITIVO}] Screenshot guardada en: {ruta_completa} (Windows)") # Incluir DISPOSITIVO en logs
            return ruta_completa
        except Exception as e:
            logger.error(f"[{DISPOSITIVO}] Error al capturar screenshot en Windows: {e}") # Incluir DISPOSITIVO en logs
            return None
    else:
        logger.error(f"[{DISPOSITIVO}] Sistema operativo no soportado para captura de pantalla: {sistema_operativo}") # Incluir DISPOSITIVO en logs
        return None


def main():
    """Función principal para configurar y ejecutar el programa."""
    database_module.crear_tablas() # Asegurar que las tablas SQLite existen al inicio

    logger.info(f"[{DISPOSITIVO}] Iniciando el programa de análisis de actividad del usuario del usuario.") # Incluir DISPOSITIVO en logs
    schedule.every(int(ANALYSIS_INTERVAL_SECONDS)).seconds.do(ejecutar_analisis_completo) # Programar la tarea principal

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()