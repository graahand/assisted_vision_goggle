""" Object Detection with Text-to-Speech Functionality 
    @SMaRC-2024
    Project: Assisted Vision Goggles 
"""

# Essential Imports
import cv2
import numpy as np
import pyttsx3
import time
import requests
from PIL import Image
from io import BytesIO
import os
from ultralytics import YOLO

# Text-to-Speech Initialization
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)  # Set TTS speed for clarity

# Load YOLOv11 Nano model directly
model = YOLO('yolo11s.pt')  # Using YOLOv8 Nano (pretrained) as YOLOv11 is hypothetical

# ESP32-CAM URL
webcam_url = 'http://192.168.136.122/stream'

# Initialize global frame variable and object tracking
global_frame = None
last_announced_object = None
last_detection_time = time.time()
min_tts_interval = 5  # Minimum interval between TTS announcements (seconds)

# Web-Cam stream Initialization
try:
    stream = requests.get(webcam_url, stream=True, timeout=10)
    if stream.status_code != 200:
        raise ValueError(f"Failed to open stream. Status code: {stream.status_code}")
except Exception as e:
    print(f"Error opening stream: {e}")
    exit()

buffer = b""
frame_count = 0

print("Stream opened successfully. Press 'q' to exit.")
for chunk in stream.iter_content(chunk_size=1024):
    buffer += chunk

    while b'\xff\xd8' in buffer and b'\xff\xd9' in buffer:
        start = buffer.find(b'\xff\xd8')
        end = buffer.find(b'\xff\xd9') + 2

        jpg_data = buffer[start:end]
        buffer = buffer[end:]  

        try:
            img = Image.open(BytesIO(jpg_data))
            frame = np.array(img)
            
            # Rotate the frame 90 degrees counterclockwise
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            frame_count += 1

            # Perform YOLO object detection
            results = model(frame)
            detections = results[0].boxes.data.cpu().numpy()

            current_time = time.time()
            for det in detections:
                x1, y1, x2, y2, conf, cls = det.tolist()
                label = model.names[int(cls)]
                
                if conf >= 0.5:  # Confidence threshold
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    cv2.putText(frame, f"{label} ({int(conf * 100)}%)", (int(x1), int(y1) - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    
                    # Speak out object name if interval has passed and it's a new object
                    if (current_time - last_detection_time >= min_tts_interval) and (label != last_announced_object):
                        tts_engine.say(f"{label} detected")
                        tts_engine.runAndWait()
                        last_detection_time = current_time
                        last_announced_object = label
                    break  

            global_frame = frame  

            if global_frame is not None:
                cv2.imshow('ESP32-CAM Object Detection', global_frame)
            else:
                cv2.imshow('ESP32-CAM Object Detection', frame)

        except Exception as e:
            print(f"Error processing frame: {e}")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()