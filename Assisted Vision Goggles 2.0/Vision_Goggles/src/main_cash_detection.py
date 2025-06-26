""" Nepalese Cash Detection with Text-to-Speech Functionality 
    @SMaRC-2024
    Project: Assisted Vision Goggles 
"""

# Necessary Imports
import cv2
import numpy as np
from ultralytics import YOLO
import requests
from PIL import Image
from io import BytesIO
import pyttsx3  # Text-to-speech library
import time  # For timing the detection
import os  # For constructing dynamic file paths

# Text-to-Speech Initialization
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)  # Set TTS speed for clarity

# Resolve the model path dynamically
current_dir = os.path.dirname(os.path.abspath(__file__))  # Current script directory
model_path = os.path.join(current_dir, '..', 'model', 'best.pt')  # Adjust for the new relative location

# Check if the model file exists
if not os.path.exists(model_path):
    print(f"Error: Model file not found at {model_path}")
    exit()

print(f"Model file found at {model_path}")

# Load the YOLO model
model = YOLO(model_path)

# ESP32-CAM URL
esp32_cam_url = 'http://192.168.136.122/stream'# Open the MJPEG stream
try:
    stream = requests.get(esp32_cam_url, stream=True, timeout=10)
    if stream.status_code != 200:
        raise ValueError(f"Failed to open stream. Status code: {stream.status_code}")
except Exception as e:
    print(f"Error opening stream: {e}")
    exit()

# Buffer for storing MJPEG frame data
buffer = b""

# Variables for TTS functionality
last_announced_cash = None
last_detection_time = time.time()
tts_interval = 10  # Minimum interval between TTS announcements (in seconds)
confidence_threshold = 0.7  # Minimum confidence for cash detection

print("Stream opened successfully. Press 'q' to exit.")

# Process the MJPEG stream
for chunk in stream.iter_content(chunk_size=1024):
    buffer += chunk

    # Process a full JPEG frame
    while b'\xff\xd8' in buffer and b'\xff\xd9' in buffer:
        start = buffer.find(b'\xff\xd8')
        end = buffer.find(b'\xff\xd9') + 2

        jpg_data = buffer[start:end]
        buffer = buffer[end:]  # Remove processed frame from the buffer

        try:
            # Convert JPEG data to numpy array
            img = Image.open(BytesIO(jpg_data))
            frame = np.array(img)

            # Rotate the frame 90 degrees counterclockwise
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

            # Convert the frame from RGB to BGR (for OpenCV compatibility)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # Run YOLO inference on the frame
            results = model.predict(frame, conf=confidence_threshold)

            current_time = time.time()

            # Process each detection
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])  # Get bounding box coordinates
                    label = result.names[box.cls[0].item()]  # Get detected label
                    confidence = box.conf[0].item()  # Get confidence score

                    # Ignore 'fake' labels
                    if label.lower().strip() == 'fake':
                        continue  # Skip further processing for this detection

                    # Draw bounding box and label on the frame
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f"{label} ({int(confidence * 100)}%)", 
                                (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                    # Check if the detected object is cash and above confidence threshold
                    if confidence >= confidence_threshold:
                        # Speak out detected cash denomination if the interval has passed
                        if current_time - last_detection_time >= tts_interval:
                            tts_engine.say(f"{label} rupees is detected")
                            tts_engine.runAndWait()
                            last_detection_time = current_time  # Update the last detection time
                            last_announced_cash = label

            # Show the frame with annotations
            cv2.imshow("ESP32-CAM Cash Detection", frame)

        except Exception as e:
            print(f"Error processing frame: {e}")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
