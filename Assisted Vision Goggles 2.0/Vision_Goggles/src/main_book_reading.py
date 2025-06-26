""" Book Text Extraction with Text-to-Speech Functionality 
    @SMaRC-2024
    Project: Assisted Vision Goggles 
"""

# Necessary Imports
import cv2
import numpy as np
import pyttsx3  # Text-to-speech library
import easyocr  # For text extraction from images
import time  # For timing intervals
import threading  # For asynchronous speech

# Initialize the pyttsx3 engine for text-to-speech
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Set the speed of speech (words per minute)
engine.setProperty('volume', 1)  # Set the volume (0.0 to 1.0)

# Initialize the EasyOCR Reader
reader = easyocr.Reader(['en'])  # Language for OCR detection (English)

# ESP32-CAM stream URL
esp32_cam_url = 'http://192.168.53.166/stream'  # Modify this URL with your ESP32-CAM's IP address

# Open the MJPEG stream from the ESP32
cap = cv2.VideoCapture(esp32_cam_url)
if not cap.isOpened():
    print("Error: Could not open video stream. Check the ESP32-CAM URL and ensure it is streaming.")
    exit()

# Time tracking for OCR processing intervals
last_ocr_time = time.time()
ocr_interval = 5  # Time in seconds between each OCR attempt
ocr_results = []  # Store the results of the OCR

def speak_text(text):
    """Function to speak the text asynchronously."""
    engine.say(text)
    engine.runAndWait()

try:
    print("Stream opened successfully. Processing frames...")

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame from stream.")
            break

        # Rotate the frame 90 degrees clockwise
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

        # Get current time
        current_time = time.time()

        # Perform OCR at defined intervals
        if current_time - last_ocr_time >= ocr_interval:
            # Update the last OCR time
            last_ocr_time = current_time

            try:
                # Perform OCR on the current frame
                ocr_results = reader.readtext(frame)

                # Accumulate the detected text into a full sentence
                sentence = " ".join([text for (_, text, confidence) in ocr_results])

                if sentence:  # Check if the detected sentence is not empty
                    print(f"Detected text: {sentence}")
                    # Speak the text asynchronously
                    threading.Thread(target=speak_text, args=(sentence,)).start()

            except Exception as e:
                print(f"Error during OCR processing: {e}")

        # Draw bounding boxes and detected text on the frame
        for (bbox, text, confidence) in ocr_results:
            # Extract bounding box coordinates
            (top_left, top_right, bottom_right, bottom_left) = bbox
            top_left = tuple(map(int, top_left))
            bottom_right = tuple(map(int, bottom_right))

            # Draw the bounding box
            cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)

            # Display the detected text
            cv2.putText(frame, text, (top_left[0], top_left[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        # Display the resulting frame
        cv2.imshow("Live OCR with Text-to-Speech", frame)

        # Exit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Release resources and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()
    print("Resources released. Program terminated.")
