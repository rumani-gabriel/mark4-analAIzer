# main.py
import time
import schedule
from config import ANALYSIS_INTERVAL_SECONDS, SCREENSHOTS_DIR
from screenshot_module import capturar_pantallas
from ai_analysis_module import analizar_conjunto_screenshots, analizar_screenshot
from summary_module import generar_resumen_email
from email_module import enviar_email
from database_module import crear_tablas, guardar_screenshot_db, guardar_resumen_analisis_db

ANALYSIS_INTERVAL_SECONDS = int(ANALYSIS_INTERVAL_SECONDS)

def ejecutar_analisis_completo():
    """Ejecuta el proceso: MÚLTIPLES capturas, análisis CONJUNTO, resumen, BD, email.""" # Descripción actualizada
    print("Ejecutando análisis completo con MÚLTIPLES capturas...") # Mensaje actualizado

    screenshot_filepaths_intervalo = [] # Lista para guardar las rutas de las capturas de ESTE intervalo

    num_capturas_por_intervalo = 3 # <---  Define el número de capturas por intervalo (puedes configurarlo en config.py si quieres)
    intervalo_captura_segundos = ANALYSIS_INTERVAL_SECONDS / num_capturas_por_intervalo # Intervalo entre capturas

    print(f"Tomando {num_capturas_por_intervalo} capturas durante {ANALYSIS_INTERVAL_SECONDS} segundos (intervalo entre capturas: {intervalo_captura_segundos:.2f} segundos)...") # Mensaje informativo

    for i in range(num_capturas_por_intervalo):
        print(f"Captura {i+1} de {num_capturas_por_intervalo}...")
        filepaths = capturar_pantallas() # Captura las pantallas en este momento
        if filepaths: # Verifica si se obtuvieron rutas de archivo
            screenshot_filepaths_intervalo.extend(filepaths) # Añade las rutas a la lista del intervalo
            print(f"Capturas guardadas: {filepaths}")
        else:
            print("Error al capturar screenshots en esta iteración.")

        if i < num_capturas_por_intervalo - 1: # No esperar después de la última captura
            time.sleep(intervalo_captura_segundos) # Espera un poco antes de la siguiente captura

    if not screenshot_filepaths_intervalo: # Si no se capturó ninguna screenshot en todo el intervalo
        print("No se obtuvieron screenshots en este intervalo para analizar.")
        return

    # *** ANÁLISIS DEL CONJUNTO DE CAPTURAS DEL INTERVALO ***
    print("Analizando el conjunto de capturas del intervalo...")
    resumen_global_ia = analizar_conjunto_screenshots(screenshot_filepaths_intervalo)

    if resumen_global_ia is None:
        print("Error al obtener el resumen global del análisis del conjunto de imágenes.")
        return

    # --- Guardar en Base de Datos --- (Sin cambios importantes aquí)
    screenshot_ids = []
    for filepath in screenshot_filepaths_intervalo: # Usar las rutas de archivo del INTERVALO
        screenshot_id = guardar_screenshot_db(filepath)
        if screenshot_id:
            screenshot_ids.append(screenshot_id)
        else:
            print(f"Error al guardar screenshot {filepath} en BD.  Continuando con el siguiente...")

    if screenshot_ids:
        primer_screenshot_id = screenshot_ids[0] # Asociar el resumen global al primer screenshot del intervalo
        guardar_resumen_analisis_db(primer_screenshot_id, resumen_global_ia)
        print("Resumen GLOBAL de análisis guardado en BD, asociado al primer screenshot del intervalo.")

    # --- Generar y Enviar Email --- (Sin cambios importantes aquí)
    resumen_email_texto = generar_resumen_email({"conjunto_pantallas": resumen_global_ia})
    enviar_email(resumen_email_texto)

    print("Análisis completo con MÚLTIPLES capturas finalizado.") # Mensaje actualizado


def main():
    print("Iniciando la aplicación de análisis de pantalla (con capturas múltiples)...") # Mensaje actualizado
    crear_tablas()

    schedule.every(ANALYSIS_INTERVAL_SECONDS).seconds.do(ejecutar_analisis_completo)

    print(f"Análisis programado para ejecutarse cada {ANALYSIS_INTERVAL_SECONDS} segundos (con capturas múltiples dentro del intervalo).") # Mensaje actualizado
    print("La aplicación se está ejecutando en segundo plano. Presiona Ctrl+C para detener.")

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()