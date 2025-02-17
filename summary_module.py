# summary_module.py

def generar_resumen_email(analisis_resultados):
    """
    Genera un resumen textual para enviar por correo electrónico a partir de los resultados del análisis.
    """
    resumen_texto = "Resumen del análisis de actividad del usuario:\n\n"
    if not analisis_resultados:
        resumen_texto += "No se encontraron análisis recientes."
    else:
        for filepath, resumen_ia in analisis_resultados.items():
            resumen_texto += f"- Captura de pantalla: {filepath}\n"
            resumen_texto += f"  Análisis IA: {resumen_ia}\n\n"

    resumen_texto += "\nFin del resumen."
    return resumen_texto


if __name__ == '__main__':
    # Ejemplo de uso del generador de resumen
    resultados_prueba = {
        "screenshots/screenshot_monitor1_1.png": "Usuario trabajando en un documento de texto.",
        "screenshots/screenshot_monitor2_1.png": "Usuario navegando por redes sociales en segundo monitor."
    }
    resumen_email = generar_resumen_email(resultados_prueba)
    print(resumen_email)