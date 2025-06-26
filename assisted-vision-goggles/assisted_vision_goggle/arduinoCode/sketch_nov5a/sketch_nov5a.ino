#include "esp_camera.h"
#include <WiFi.h>
#include <WebServer.h>

// Camera model definition-
#define CAMERA_MODEL_ESP32S3_EYE
#include "camera_pins.h"

// Wi-Fi credentials
const char* ssid = "Skill Museum";
const char* password = "skillmuseum@2024";

// Web server on port 80
WebServer server(80);

// MJPEG stream handler
void handleStream() {
    WiFiClient client = server.client();

    if (!client.connected()) return;

    client.println("HTTP/1.1 200 OK");
    client.println("Content-Type: multipart/x-mixed-replace; boundary=frame");
    client.println();

    while (client.connected()) {
        camera_fb_t *fb = esp_camera_fb_get();
        
        if (!fb) {
            Serial.println("Failed to capture frame");
            return;
        }

        // Send the captured image as JPEG
        client.printf("--frame\r\nContent-Type: image/jpeg\r\nContent-Length: %d\r\n\r\n", fb->len);
        client.write(fb->buf, fb->len);
        client.println("\r\n");

        esp_camera_fb_return(fb);

        // Reduce lag by lowering the frame rate (higher delay = lower FPS)
        delay(50);  // Adjust the frame rate (lower number = higher FPS)
    }
}

void setup() {
    // Initialize serial and Wi-Fi
    Serial.begin(115200);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("WiFi connected");

    // Camera configuration
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_sccb_sda = SIOD_GPIO_NUM;
    config.pin_sccb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    
    // Set lower resolution for faster performance
    config.frame_size = FRAMESIZE_HQVGA;  // 240x176 resolution (lower for better performance)
    
    // JPEG compression settings
    config.pixel_format = PIXFORMAT_JPEG;
    config.jpeg_quality = 10;  // Lower quality to reduce frame size (higher number = lower quality)
    config.fb_count = 1;

    if (esp_camera_init(&config) != ESP_OK) {
        Serial.println("Camera init failed");
        return;
    }

    // Get the camera sensor settings and apply custom configuration
    sensor_t *s = esp_camera_sensor_get();
    s->set_vflip(s, 1);  // Flip the image if needed
    s->set_brightness(s, 0);  // Adjust brightness
    s->set_saturation(s, 0);  // Adjust saturation

    // Start the server and stream endpoint
    server.on("/stream", HTTP_GET, handleStream);
    server.begin();

    // Print the IP address
    Serial.print("Stream ready at: http://");
    Serial.print(WiFi.localIP());
    Serial.println("/stream");
}

void loop() {
    server.handleClient();  // Handle client requests
}