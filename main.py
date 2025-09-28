#!/usr/bin/env python3
"""
Main - Programa principal para el ESP32 Stream Viewer
"""

import cv2
import numpy as np
from ESP32Client import ESP32Client

def main():
    """Función principal del programa"""
    print("ESP32 Stream Viewer")
    print("=" * 30)
    
    # Crear instancia del stream
    camera = ESP32Client()
    
    # Conectar al stream
    response = camera.connect_to_stream()
    if not response or response.status_code != 200:
        print("Error: No se pudo conectar al stream")
        return
    
    print("Stream conectado - Presiona 'q' para salir")
    
    try:
        # Procesar stream
        for jpg_data in camera.parse_mjpeg_stream(response):
            try:
                # Convertir bytes a imagen directamente con OpenCV
                img_array = cv2.imdecode(np.frombuffer(jpg_data, dtype=np.uint8), cv2.IMREmAD_COLOR)
                
                # Procesar frame
                processed_frame = camera.process_frame(img_array)
                
                # Mostrar frame
                camera.display_frame(processed_frame)
                
                # Verificar tecla de salida
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("Saliendo...")
                    break
                    
            except Exception as e:
                print(f"Error procesando frame: {e}")
                continue
                
    except KeyboardInterrupt:
        print("Interrumpido por el usuario")
    except Exception as e:
        print(f"Error en el stream: {e}")
    finally:
        cv2.destroyAllWindows()
        print("Stream finalizado")

if __name__ == "__main__":
    main()