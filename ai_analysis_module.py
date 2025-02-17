# ai_analysis_module.py
import google.generativeai as genai
from PIL import Image
import json
import os

# **IMPORTANTE:** Configura tu API Key de Gemini aquí o como variable de entorno.
# genai.configure(api_key="YOUR_API_KEY")
# Considera usar variables de entorno para mayor seguridad:
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    print("Advertencia: No se encontró la API Key de Gemini en variables de entorno (GOOGLE_API_KEY).")
    print("Por favor, configura tu API Key en config.py o como variable de entorno.")
    # La aplicación podría no funcionar correctamente sin la API Key configurada.


def analizar_screenshot(ruta_imagen):
    """
    Analiza una captura de pantalla utilizando el modelo multimodal Gemini Pro Vision.
    Args:
        ruta_imagen (str): La ruta completa al archivo de la imagen.
    Returns:
        str: Un resumen textual del análisis generado por Gemini,
             o None si ocurre un error.
    """
    try:
        img = Image.open(ruta_imagen)
        model = genai.GenerativeModel('gemini-2.0-flash-exp', system_instruction="""
        Eres un experto en análisis de comportamiento en internet, gestion del tiempo, contenido inapropiado. Proporciona un análisis breve y preciso basado en la imagen mostrada. Vas a ser enfático en revisión de redes sociales, verás contenido, imágenes, miniaturas, lo mismo en aplicaciones como YouTube. Es necesario que siempre que haya una imagen de personas, te concentres en analizarla. En el caso de que veas información acerca de alguna cuenta bancaria o monedero virtual, no vas a hacer nada, simplemente vas a omitir esa información. En caso de que veas mensajes, solamente te vas a concentrar en el mismo si detectas conversaciones sospechosas o insanas.
        """)
        prompt = """
        Vas a usar 250 tokens para comlir tu tarea, tendras que ser claro, pero resumido.
        Tu tarea principal es ayudar al usuario a usar bien su tiempo y que sea productivo. Lo debes "proteger" de contenido inapropiado en la web, imágenes sugestivas, sensuales. Concéntrate específicamente en la vida que lleva en la web, YouTube, redes sociales, etc. Siempre que veas una imagen de una persona, analízala y describe lo que ves(haz enfasis en miniaturas de redes sociales o youtube si es que los ves). En el caso de que encuentres que la imagen corresponde a algún monedero virtual, contraseñas, claves o información bancaria, vas a omitir esa información, vas a hacer de cuenta que la imagen nunca existió. Finalmente, quiero que generes un JSON con este esquema:
        "nombre": "nombre_imagen", "analisis_imagen": "descripcion_imagen", "analisis_contexto": "descripcion_contexto", "analisis_comportamiento": "descripcion_comportamiento".
        """
        response = model.generate_content(
            contents=[prompt, img],
            generation_config=genai.GenerationConfig(max_output_tokens=300)
        )
        if hasattr(response, 'text') and response.text:
            try:
                json_response = json.loads(response.text)  # Intentamos parsear la respuesta como JSON
                # Formateamos el resumen para que sea un texto legible
                summary_text = f"Análisis de imagen '{json_response.get('nombre', 'N/A')}' con Gemini Pro Vision:\n"
                summary_text += f"- Análisis de la imagen: {json_response.get('analisis_imagen', 'N/A')}\n"
                summary_text += f"- Análisis del contexto: {json_response.get('analisis_contexto', 'N/A')}\n"
                summary_text += f"- Análisis del comportamiento: {json_response.get('analisis_comportamiento', 'N/A')}\n"
                return summary_text
            except json.JSONDecodeError:
                print(f"Advertencia: La respuesta de Gemini no fue un JSON válido para la imagen: {ruta_imagen}. Devolviendo respuesta textual sin formatear.")
                return response.text # Devolvemos el texto sin formatear si no es un JSON válido
        else:
            print(f"Error: No se recibió texto de respuesta para la imagen: {ruta_imagen}")
            return None
    except Exception as e:
        print(f"Error al analizar la imagen {ruta_imagen} con Gemini Pro Vision: {e}")
        return "Error en el análisis de IA." # Retornar un mensaje de error en caso de fallo

def analizar_conjunto_screenshots(lista_rutas_imagenes):
    """
    Analiza un conjunto de capturas de pantalla con Gemini Pro Vision para generar un resumen global.
    (Versión modificada para retornar texto plano, sin parsear JSON)
    Args:
        lista_rutas_imagenes (list): Lista de rutas completas a los archivos de imagen de las capturas.
    Returns:
        str: Un resumen textual global del análisis generado por Gemini para el conjunto de imágenes,
             o None si ocurre un error.
    """
    try:
        imagenes = [Image.open(ruta_imagen) for ruta_imagen in lista_rutas_imagenes] # Carga TODAS las imágenes

        model = genai.GenerativeModel('gemini-2.0-flash-exp', system_instruction="""
        Eres un experto en análisis de comportamiento en internet, gestion del tiempo, contenido inapropiado. Proporciona un análisis breve y preciso basado en el CONJUNTO de imágenes mostradas. Vas a ser enfático en revisión de redes sociales, contenido, imágenes, miniaturas en todas las pantallas. Es necesario que siempre que haya una imagen de personas, te concentres en analizarla en el contexto global de todas las pantallas. En el caso de que veas información acerca de alguna cuenta bancaria o monedero virtual, no vas a hacer nada, simplemente vas a omitir esa información. En caso de que veas mensajes, solamente te vas a concentrar en los mismos si detectas conversaciones sospechosas o insanas, considerando el contexto de todas las pantallas.
        """)
        prompt = """
        No quiero que me respondas aun, limitate a leer todo el prompt y a ajustar tu respuesta a mi solicitud.
        Vas a usar 300 tokens para comlir tu tarea, tendras que ser claro, pero resumido.
        Tu tarea principal es ayudar al usuario a usar bien su tiempo y que sea productivo, analizando el CONJUNTO de pantallas mostradas. Lo debes "proteger" de contenido inapropiado en la web, imágenes sugestivas, sensuales, en todas las pantallas. Concéntrate específicamente en la vida que lleva en la web, YouTube, redes sociales, etc., en el contexto de TODAS las pantallas. Siempre que veas una imagen de una persona en CUALQUIER pantalla, analízala y describe lo que ves, considerando el contexto de las otras pantallas (haz énfasis en miniaturas de redes sociales o youtube si es que los ves). En el caso de que encuentres que la imagen corresponde a algún monedero virtual, contraseñas, claves o información bancaria en CUALQUIER pantalla, vas a omitir esa información. Finalmente, quiero que generes un resumen con este esquema:

        ```json
        {
            "analisis_conjunto": "descripcion_global_conjunto_imagenes",
            "comportamiento_global": "descripcion_comportamiento_global",
            "uso_tiempo_global": "descripcion_uso_tiempo_global"
        }
        ```

        Por favor, asegúrate de que tu respuesta sea FORMATEADA COMO JSON, pero NO valides el formato JSON estrictamente. Solo necesito que la respuesta se vea como un JSON para poder mostrarla en el email.
        """
        response = model.generate_content(
            contents=[prompt] + imagenes, # Importante: Pasa el PROMPT PRIMERO, seguido de la LISTA DE IMAGENES
            generation_config=genai.GenerationConfig(max_output_tokens=300)
        )
        if hasattr(response, 'text') and response.text:
            # ---  MODIFICADO: Retornar response.text directamente, SIN parsear JSON ---
            summary_text = response.text
            return summary_text
        else:
            print(f"Error: No se recibió texto de respuesta para el análisis del conjunto de imágenes.")
            return None
    except Exception as e:
        print(f"Error DETALLADO al analizar el conjunto de imágenes con Gemini Pro Vision: {e}") # Imprimir excepción completa
        return "Error en el análisis de IA del conjunto de imágenes."
    
if __name__ == '__main__':
    analizar_screenshot()
    analizar_conjunto_screenshots()
    