#!/usr/bin/env python3
"""
ESP32StreamViewer - Clase para manejar el stream del ESP32
"""

import cv2
import numpy as np
import requests
from PIL import Image
import io

class CameraStream:
    """Clase para manejar el stream de cámara"""
    
    def __init__(self, esp32_ip="192.168.4.1"):
        self.esp32_ip = esp32_ip
        self.stream_url = f"http://{esp32_ip}/stream"
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.frame_count = 0
        
    def connect_to_stream(self):
        """Establece conexión con el stream del ESP32"""
        try:
            print(f"Conectando a {self.stream_url}...")
            response = requests.get(self.stream_url, stream=True, timeout=15)
            return response
        except Exception as e:
            print(f"Error conectando: {e}")
            return None
    
    def process_frame(self, img_array):
        """Procesa un frame individual"""
        # Convertir RGB a BGR para OpenCV
        if len(img_array.shape) == 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Sin detección de caras - solo retornar la imagen original
        return img_array
    
    def detect_faces(self, img):
        """Detecta caras en la imagen y dibuja rectángulos"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=4,
            minSize=(30, 30),
            maxSize=(300, 300)
        )
        
        # Dibujar rectángulos alrededor de las caras
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(img, 'Cara', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return img
    
    def parse_mjpeg_stream(self, response):
        """Parsea el stream MJPEG y extrae frames"""
        buffer = b""
        
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                buffer += chunk
                
                # Buscar marcadores JPEG
                start = buffer.find(b'\xff\xd8')
                end = buffer.find(b'\xff\xd9')
                
                if start != -1 and end != -1 and end > start:
                    # Extraer frame completo
                    jpg_data = buffer[start:end+2]
                    buffer = buffer[end+2:]
                    
                    yield jpg_data
    
    def display_frame(self, img_array):
        """Muestra el frame en la ventana"""
        cv2.imshow('ESP32 Camera Stream', img_array)
        self.frame_count += 1
        
        if self.frame_count % 30 == 0:
            print(f"Frames procesados: {self.frame_count}")