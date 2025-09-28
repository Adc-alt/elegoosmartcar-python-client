#!/usr/bin/env python3
"""
ESP32StreamViewer - Clase para manejar el stream del ESP32
"""

import cv2
import numpy as np
import requests

class ESP32Client:
    """Clase para manejar el stream de cámara"""
    
    def __init__(self, esp32_ip="192.168.4.1"):
        self.esp32_ip = esp32_ip
        self.stream_url = f"http://{esp32_ip}/stream"
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.frame_count = 0
        
        # Valores HSV iniciales para naranja
        self.h_min = 10
        self.h_max = 25
        self.s_min = 120
        self.s_max = 255
        self.v_min = 120
        self.v_max = 255
        
        # Crear ventana para controles HSV
        cv2.namedWindow('HSV Controls', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('HSV Controls', 400, 300)
        
        # Crear trackbars
        cv2.createTrackbar('H Min', 'HSV Controls', self.h_min, 179, self.on_h_min_change)
        cv2.createTrackbar('H Max', 'HSV Controls', self.h_max, 179, self.on_h_max_change)
        cv2.createTrackbar('S Min', 'HSV Controls', self.s_min, 255, self.on_s_min_change)
        cv2.createTrackbar('S Max', 'HSV Controls', self.s_max, 255, self.on_s_max_change)
        cv2.createTrackbar('V Min', 'HSV Controls', self.v_min, 255, self.on_v_min_change)
        cv2.createTrackbar('V Max', 'HSV Controls', self.v_max, 255, self.on_v_max_change)
    
    # Funciones callback para los trackbars
    def on_h_min_change(self, val):
        self.h_min = val
    
    def on_h_max_change(self, val):
        self.h_max = val
    
    def on_s_min_change(self, val):
        self.s_min = val
    
    def on_s_max_change(self, val):
        self.s_max = val
    
    def on_v_min_change(self, val):
        self.v_min = val
    
    def on_v_max_change(self, val):
        self.v_max = val
        
    def connect_to_stream(self):
        """Establece conexión con el stream del ESP32"""
        try:
            # print(f"Conectando a {self.stream_url}...")
            response = requests.get(self.stream_url, stream=True, timeout=15)
            return response
        except Exception as e:
            # print(f"Error conectando: {e}")
            return None
    
    def process_frame(self, img_array):
        """Procesa un frame individual"""
        # Detectar color naranja
        img_with_orange = self.detect_orange_color(img_array)
        return img_with_orange
    
    def detect_orange_color(self, img):
        """Detecta objetos de color naranja y dibuja contornos"""
        # Convertir BGR a HSV para mejor detección de color
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Usar valores de los trackbars
        lower_orange = np.array([self.h_min, self.s_min, self.v_min])
        upper_orange = np.array([self.h_max, self.s_max, self.v_max])
        
        # Crear máscara para color naranja
        mask = cv2.inRange(hsv, lower_orange, upper_orange)
        
        # Mostrar máscara en ventana separada
        cv2.imshow('Orange Mask', mask)
        
        # Mostrar valores actuales en la imagen
        cv2.putText(img, f'H: {self.h_min}-{self.h_max}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(img, f'S: {self.s_min}-{self.s_max}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(img, f'V: {self.v_min}-{self.v_max}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Dibujar contornos alrededor de objetos naranjas
        for contour in contours:
            # Filtrar contornos pequeños
            if cv2.contourArea(contour) > 500:  # Área mínima
                # Dibujar rectángulo alrededor del objeto
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 165, 255), 2)  # Naranja
                cv2.putText(img, 'Naranja', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
        
        return img
    
    # def detect_faces(self, img):
    #     """Detecta caras en la imagen y dibuja rectángulos"""
    #     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
    #     faces = self.face_cascade.detectMultiScale(
    #         gray,
    #         scaleFactor=1.1,
    #         minNeighbors=4,
    #         minSize=(30, 30),
    #         maxSize=(300, 300)
    #     )
        
    #     # Dibujar rectángulos alrededor de las caras
    #     for (x, y, w, h) in faces:
    #         cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
    #         cv2.putText(img, 'Cara', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
    #     return img
    
    def parse_mjpeg_stream(self, response):
        """Parsea el stream MJPEG y extrae frames"""
        buffer = b""
        
        for chunk in response.iter_content(chunk_size=1024):#chunk_size es el tamaño de los chunks que se van a recibir
            #chunk son trocitos de la imagen, debido a que la imagen es muy grande, se divide en chunks
            if chunk:
                buffer += chunk
                
                # Buscar marcadores JPEG
                start = buffer.find(b'\xff\xd8')#marcador de inicio de la imagen
                end = buffer.find(b'\xff\xd9')#marcador de fin de la imagen
                
                if start != -1 and end != -1 and end > start:
                    # Extraer frame completo
                    jpg_data = buffer[start:end+2]
                    buffer = buffer[end+2:]
                    
                    yield jpg_data
    
    def display_frame(self, img_array):
        """Muestra el frame en la ventana"""
        cv2.imshow('ESP32 Camera Stream', img_array)
        # self.frame_count += 1
        
        # if self.frame_count % 30 == 0:
            # print(f"Frames procesados: {self.frame_count}")