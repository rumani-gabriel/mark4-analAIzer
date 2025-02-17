# screenshot_module.py
import mss
import mss.tools
import os
from datetime import datetime
from config import SCREENSHOTS_DIR

def capturar_pantallas():
    """Captura screenshots de todos los monitores activos."""
    with mss.mss() as sct:
        monitores = sct.monitors[1:]  # Ignora el monitor combinado (índice 0) si existe, y captura el resto. Si solo tienes uno, ajusta esto.
        filepaths = []
        for monitor_number, monitor in enumerate(monitores):
            # Formato de nombre de archivo: screenshot_YYYYMMDD_HHMMSS_monitorN.png
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp_str}_monitor{monitor_number+1}.png"
            filepath = os.path.join(SCREENSHOTS_DIR, filename)

            sct_img = sct.grab(monitor) # Captura el monitor actual
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=filepath) # Guarda como PNG
            filepaths.append(filepath)
            print(f"Screenshot guardado: {filepath}")
        return filepaths


if __name__ == '__main__':
    paths = capturar_pantallas() # Para probar la captura directamente
    print("Rutas de screenshots capturadas:", paths)