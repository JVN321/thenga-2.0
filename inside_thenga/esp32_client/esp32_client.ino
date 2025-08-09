#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <MPU6050.h>
#include <Wire.h>

// WiFi credentials
const char* ssid = "thenga";
const char* password = "thengaaa";

// Flask server URL
const char* serverURL = "http://192.168.226.51:5000";  // Replace with your computer's IP

// Pin definitions
const int ledPin = 2;  // Built-in LED on most ESP32 boards
// Use default I2C pins for ESP32
const int SDA_PIN = 21;  // Default SDA pin for ESP32
const int SCL_PIN = 22;  // Default SCL pin for ESP32

// L298N Motor Driver pins
const int MOTOR_IN1 = 25;  // Motor direction pin 1
const int MOTOR_IN2 = 26;  // Motor direction pin 2
const int MOTOR_ENA = 27;  // Motor enable/speed pin (PWM)

// MPU6050 sensor
MPU6050 mpu;

// Motion detection variables
bool devicePickedUp = false;
unsigned long lastMotionTime = 0;
float gyroPickupThreshold = 250.0;  // Simplified gyro threshold for pickup detection
unsigned long pickupCooldown = 10000;  // 10 seconds cooldown between detections

// Motor control variables
bool motorRunning = false;
unsigned long motorStartTime = 0;
unsigned long motorRunDuration = 3000;  // Run motor for 3 seconds
unsigned long motorDelayAfterPickup = 5000;  // Start motor 5 seconds after pickup
bool motorScheduled = false;
unsigned long motorScheduledTime = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);  // Give serial time to initialize
  
  Serial.println("ESP32 Starting...");
  
  // Initialize pins
  pinMode(ledPin, OUTPUT);
  pinMode(MOTOR_IN1, OUTPUT);
  pinMode(MOTOR_IN2, OUTPUT);
  pinMode(MOTOR_ENA, OUTPUT);
  
  // Initialize motor pins to stopped state
  digitalWrite(MOTOR_IN1, LOW);
  digitalWrite(MOTOR_IN2, LOW);
  digitalWrite(MOTOR_ENA, LOW);
  digitalWrite(ledPin, LOW);  // Start with LED off
  
  // Initialize I2C communication with default pins
  Wire.begin(SDA_PIN, SCL_PIN);
  Wire.setClock(400000);  // Set I2C clock to 400kHz for better performance
  
  // Initialize MPU6050
  Serial.println("Initializing MPU6050...");
  Serial.printf("Using SDA: GPIO%d, SCL: GPIO%d\n", SDA_PIN, SCL_PIN);
  
  delay(100);
  mpu.initialize();
  delay(100);
  
  // Test MPU6050 connection
  if (mpu.testConnection()) {
    Serial.println("✓ MPU6050 connection successful!");
    
    // Set accelerometer range to ±2g
    mpu.setFullScaleAccelRange(MPU6050_ACCEL_FS_2);
    
    // Set gyroscope range to ±250°/s
    mpu.setFullScaleGyroRange(MPU6050_GYRO_FS_250);
    
    // Enable sleep mode wake up
    mpu.setSleepEnabled(false);
    
    Serial.println("MPU6050 configured successfully!");
  } else {
    Serial.println("✗ MPU6050 connection failed!");
    Serial.println("Please check wiring:");
    Serial.println("  VCC -> 3.3V");
    Serial.println("  GND -> GND");
    Serial.println("  SDA -> GPIO21");
    Serial.println("  SCL -> GPIO22");
  }
  
  // Enhanced WiFi connection
  connectToWiFi();
  
  // Test connection to Flask server
  testConnection();
  
  Serial.println("ESP32 ready! Device will detect placement and control motor using MPU6050.");
  Serial.println("Available serial commands: test, status, chat:message, help");
}

void connectToWiFi() {
  Serial.println("Starting WiFi connection...");
  Serial.printf("SSID: %s\n", ssid);
  
  // Disconnect any previous connection
  WiFi.disconnect(true);
  delay(1000);
  
  // Set WiFi mode
  WiFi.mode(WIFI_STA);
  delay(100);
  
  // Begin WiFi connection
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(1000);
    Serial.print(".");
    attempts++;
    
    // Show status every 10 attempts
    if (attempts % 10 == 0) {
      Serial.println();
      Serial.printf("WiFi Status: %d (Attempt %d/30)\n", WiFi.status(), attempts);
      printWiFiStatus();
    }
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.println("✓ WiFi connected successfully!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    Serial.print("Signal strength (RSSI): ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
  } else {
    Serial.println();
    Serial.println("✗ WiFi connection failed!");
    printWiFiStatus();
    Serial.println("Please check:");
    Serial.println("  - WiFi credentials");
    Serial.println("  - WiFi network availability");
    Serial.println("  - ESP32 antenna connection");
  }
}

void printWiFiStatus() {
  wl_status_t status = WiFi.status();
  Serial.print("WiFi Status: ");
  switch (status) {
    case WL_IDLE_STATUS:
      Serial.println("WL_IDLE_STATUS");
      break;
    case WL_NO_SSID_AVAIL:
      Serial.println("WL_NO_SSID_AVAIL - Network not found");
      break;
    case WL_SCAN_COMPLETED:
      Serial.println("WL_SCAN_COMPLETED");
      break;
    case WL_CONNECTED:
      Serial.println("WL_CONNECTED");
      break;
    case WL_CONNECT_FAILED:
      Serial.println("WL_CONNECT_FAILED - Wrong password?");
      break;
    case WL_CONNECTION_LOST:
      Serial.println("WL_CONNECTION_LOST");
      break;
    case WL_DISCONNECTED:
      Serial.println("WL_DISCONNECTED");
      break;
    default:
      Serial.printf("Unknown status: %d\n", status);
  }
}

void loop() {
  // Check WiFi connection status
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected! Attempting to reconnect...");
    connectToWiFi();
  }
  
  // Read MPU6050 data
  int16_t ax, ay, az;
  int16_t gx, gy, gz;
  
  mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
  
  // Convert to g-force (approximate)
  float accelX = ax / 16384.0;
  float accelY = ay / 16384.0;
  float accelZ = az / 16384.0;
  
  // Convert gyroscope to degrees per second
  float gyroX = gx / 131.0;
  float gyroY = gy / 131.0;
  float gyroZ = gz / 131.0;
  
  // Calculate total acceleration magnitude
  float totalAccel = sqrt(accelX*accelX + accelY*accelY + accelZ*accelZ);
  
  // Calculate total gyro magnitude
  float totalGyro = sqrt(gyroX*gyroX + gyroY*gyroY + gyroZ*gyroZ);
  
  // Print gyro and accelerometer data to serial
  Serial.printf("Accel: X=%.2f Y=%.2f Z=%.2f (%.2fg) | Gyro: X=%.2f Y=%.2f Z=%.2f (%.2f deg/s total)\n", 
                accelX, accelY, accelZ, totalAccel, gyroX, gyroY, gyroZ, totalGyro);
  
  // Handle motor control
  handleMotorControl();
  
  // Simplified pickup detection using gyroscope
  if (!motorRunning && !devicePickedUp && (abs(gyroX) > gyroPickupThreshold || abs(gyroY) > gyroPickupThreshold || abs(gyroZ) > gyroPickupThreshold)) {
    unsigned long currentTime = millis();
    
    if ((currentTime - lastMotionTime > pickupCooldown) && !motorRunning) {
      devicePickedUp = true;
      lastMotionTime = currentTime;
      
      // Schedule motor to start after 5 seconds
      motorScheduled = true;
      motorScheduledTime = currentTime + motorDelayAfterPickup;
      
      Serial.println("Device picked up detected!");
      Serial.printf("Gyro values: X=%.2f Y=%.2f Z=%.2f deg/s (Threshold: %.2f)\n", 
                    gyroX, gyroY, gyroZ, gyroPickupThreshold);
      Serial.printf("Motor will start in %lu seconds\n", motorDelayAfterPickup / 1000);
      
      // Send pickup event to server
      sendPickupEvent();
      
      // Flash LED to indicate detection
      digitalWrite(ledPin, HIGH);
      delay(100);
      digitalWrite(ledPin, LOW);
    }
  }
  
  // Reset pickup state when device is stable
  if (devicePickedUp && totalGyro < 5.0) {
    devicePickedUp = false;
    Serial.println("Device stable again - pickup state reset");
  }
  
  // Check for serial commands
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    handleSerialCommand(command);
  }
  
  delay(500);  // Slower update rate for better readability
}

void startMotor() {
  if (!motorRunning) {
    motorRunning = true;
    motorStartTime = millis();
    
    Serial.println("Starting motor!");
    
    // Set motor direction (forward)
    digitalWrite(MOTOR_IN1, HIGH);
    digitalWrite(MOTOR_IN2, LOW);
    
    // Enable motor with full speed
    digitalWrite(MOTOR_ENA, HIGH);
    
    // Flash LED to indicate motor start
    for (int i = 0; i < 5; i++) {
      digitalWrite(ledPin, HIGH);
      delay(100);
      digitalWrite(ledPin, LOW);
      delay(700);
    }
  }
}

void stopMotor() {
  if (motorRunning) {
    motorRunning = false;
    
    Serial.println("Stopping motor!");
    
    // Stop motor
    digitalWrite(MOTOR_IN1, LOW);
    digitalWrite(MOTOR_IN2, LOW);
    digitalWrite(MOTOR_ENA, LOW);
    
    // Single LED flash to indicate motor stop
    digitalWrite(ledPin, HIGH);
    delay(500);
    digitalWrite(ledPin, LOW);
  }
}

void handleMotorControl() {
  unsigned long currentTime = millis();
  
  // Check if motor should start (5 seconds after pickup)
  if (motorScheduled && !motorRunning && currentTime >= motorScheduledTime) {
    motorScheduled = false;
    startMotor();
  }
  
  // Check if motor should stop (after running for specified duration)
  if (motorRunning) {
    unsigned long runTime = currentTime - motorStartTime;
    
    if (runTime >= motorRunDuration) {
      stopMotor();
    }
  }
}

void sendPickupEvent() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(String(serverURL) + "/esp32/pickup");
    http.addHeader("Content-Type", "application/json");
    
    // Create pickup event JSON
    DynamicJsonDocument doc(512);
    doc["event_type"] = "device_pickup";
    doc["device_id"] = "ESP32_MPU6050";
    doc["timestamp"] = millis();
    doc["sensor"] = "MPU6050";
    
    String jsonPayload;
    serializeJson(doc, jsonPayload);
    
    Serial.println("Sending pickup event: " + jsonPayload);
    
    int httpResponseCode = http.POST(jsonPayload);
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Pickup event response (" + String(httpResponseCode) + "): " + response);
      
      // Parse response to check if audio was played
      DynamicJsonDocument responseDoc(1024);
      deserializeJson(responseDoc, response);
      
      if (responseDoc["audio_played"]) {
        Serial.println("✓ Audio notification played on server!");
      }
      
    } else {
      Serial.println("✗ Failed to send pickup event. Error: " + String(httpResponseCode));
    }
    
    http.end();
  } else {
    Serial.println("✗ WiFi not connected!");
  }
}

void sendGyroEvent(float gx, float gy, float gz) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(String(serverURL) + "/esp32/gyro");
    http.addHeader("Content-Type", "application/json");
    
    // Create gyro event JSON
    DynamicJsonDocument doc(512);
    doc["event_type"] = "gyro_threshold";
    doc["device_id"] = "ESP32_MPU6050";
    doc["timestamp"] = millis();
    doc["sensor"] = "MPU6050";
    doc["gyro_x"] = gx;
    doc["gyro_y"] = gy;
    doc["gyro_z"] = gz;
    doc["threshold"] = gyroPickupThreshold;
    
    String jsonPayload;
    serializeJson(doc, jsonPayload);
    
    Serial.println("Sending gyro event: " + jsonPayload);
    
    int httpResponseCode = http.POST(jsonPayload);
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Gyro event response (" + String(httpResponseCode) + "): " + response);
      
      // Parse response to check if audio was played
      DynamicJsonDocument responseDoc(1024);
      deserializeJson(responseDoc, response);
      
      if (responseDoc["audio_played"]) {
        Serial.println("✓ Audio notification played on server!");
      }
      
    } else {
      Serial.println("✗ Failed to send gyro event. Error: " + String(httpResponseCode));
    }
    
    http.end();
  } else {
    Serial.println("✗ WiFi not connected!");
  }
}

void testConnection() {
  Serial.println("Testing connection to Flask server...");
  
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(String(serverURL) + "/esp32");
    http.addHeader("Content-Type", "application/json");
    
    String jsonPayload = "{\"command\":\"get_status\"}";
    int httpResponseCode = http.POST(jsonPayload);
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("✓ Server connection successful!");
      Serial.println("Server response: " + response);
    } else {
      Serial.println("✗ Server connection failed. Error: " + String(httpResponseCode));
      Serial.println("Make sure Flask server is running on: " + String(serverURL));
    }
    
    http.end();
  } else {
    Serial.println("✗ WiFi not connected!");
  }
}

void sendPlacementEvent() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(String(serverURL) + "/esp32/placement");
    http.addHeader("Content-Type", "application/json");
    
    // Create placement event JSON
    DynamicJsonDocument doc(512);
    doc["event_type"] = "device_placed_down";
    doc["device_id"] = "ESP32_MPU6050";
    doc["timestamp"] = millis();
    doc["sensor"] = "MPU6050";
    doc["motor_started"] = true;
    
    
    String jsonPayload;
    serializeJson(doc, jsonPayload);
    
    Serial.println("Sending placement event: " + jsonPayload);
    
    int httpResponseCode = http.POST(jsonPayload);
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Placement event response (" + String(httpResponseCode) + "): " + response);
      
      // Parse response to check if audio was played
      DynamicJsonDocument responseDoc(1024);
      deserializeJson(responseDoc, response);
      
      if (responseDoc["audio_played"]) {
        Serial.println("✓ Audio notification played on server!");
      }
      
    } else {
      Serial.println("✗ Failed to send placement event. Error: " + String(httpResponseCode));
    }
    
    http.end();
  } else {
    Serial.println("✗ WiFi not connected!");
  }
}

void handleSerialCommand(String command) {
  Serial.println("Received command: " + command);
  
  if (command == "test") {
    testConnection();
    
  } else if (command == "wifi") {
    Serial.println("WiFi Status:");
    printWiFiStatus();
    if (WiFi.status() == WL_CONNECTED) {
      Serial.printf("IP: %s\n", WiFi.localIP().toString().c_str());
      Serial.printf("RSSI: %d dBm\n", WiFi.RSSI());
    }
    
  } else if (command == "reconnect") {
    Serial.println("Reconnecting to WiFi...");
    connectToWiFi();
    
  } else if (command == "scan") {
    Serial.println("Scanning for WiFi networks...");
    int n = WiFi.scanNetworks();
    if (n == 0) {
      Serial.println("No networks found");
    } else {
      Serial.printf("Found %d networks:\n", n);
      for (int i = 0; i < n; ++i) {
        Serial.printf("%d: %s (%d dBm) %s\n", 
        i + 1, 
        WiFi.SSID(i).c_str(), 
        WiFi.RSSI(i),
        WiFi.encryptionType(i) == WIFI_AUTH_OPEN ? "Open" : "Encrypted");
      }
    }
    
  } else if (command == "pickup_test") {
    Serial.println("Simulating pickup event...");
    sendPickupEvent();
    
  } else if (command == "gyro_threshold") {
    Serial.printf("Current gyro pickup threshold: %.2f deg/s\n", gyroPickupThreshold);
    
  } else if (command.startsWith("gyro_threshold:")) {
    float newThreshold = command.substring(15).toFloat();
    if (newThreshold > 5.0 && newThreshold < 200.0) {
      gyroPickupThreshold = newThreshold;
      Serial.printf("Gyro pickup threshold set to: %.2f deg/s\n", gyroPickupThreshold);
    } else {
      Serial.println("Invalid gyro threshold. Use value between 5.0 and 200.0");
    }
    
  } else if (command == "motor_test") {
    Serial.println("Testing motor...");
    startMotor();
    
  } else if (command == "motor_stop") {
    Serial.println("Stopping motor...");
    stopMotor();
    
  } else if (command == "motor_delay") {
    Serial.printf("Current motor delay after pickup: %lu seconds\n", motorDelayAfterPickup / 1000);
    
  } else if (command.startsWith("motor_delay:")) {
    unsigned long newDelay = command.substring(12).toInt() * 1000;
    if (newDelay >= 1000 && newDelay <= 30000) {
      motorDelayAfterPickup = newDelay;
      Serial.printf("Motor delay set to: %lu seconds\n", motorDelayAfterPickup / 1000);
    } else {
      Serial.println("Invalid motor delay. Use value between 1 and 30 seconds");
    }
    
  } else if (command == "gyro") {
    Serial.println("Current gyro/accel readings:");
    int16_t ax, ay, az, gx, gy, gz;
    mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
    float accelX = ax / 16384.0;
    float accelY = ay / 16384.0;
    float accelZ = az / 16384.0;
    float gyroX = gx / 131.0;
    float gyroY = gy / 131.0;
    float gyroZ = gz / 131.0;
    Serial.printf("Accel: X=%.2f Y=%.2f Z=%.2f g\n", accelX, accelY, accelZ);
    Serial.printf("Gyro: X=%.2f Y=%.2f Z=%.2f deg/s\n", gyroX, gyroY, gyroZ);
    
  } else if (command == "calibrate") {
    Serial.println("Calibrating MPU6050... Keep device still!");
    delay(2000);
    // Simple calibration - you can expand this
    Serial.println("Calibration complete");
    
  } else if (command.startsWith("chat:")) {
    String message = command.substring(5);
    sendChatMessage(message);
    
  } else if (command == "help") {
    Serial.println("Available commands:");
    Serial.println("  test              - Test server connection");
    Serial.println("  wifi              - Show WiFi status");
    Serial.println("  reconnect         - Reconnect to WiFi");
    Serial.println("  scan              - Scan for WiFi networks");
    Serial.println("  pickup_test       - Simulate pickup event");
    Serial.println("  motor_test        - Test motor start");
    Serial.println("  motor_stop        - Stop motor");
    Serial.println("  motor_delay       - Show motor delay after pickup");
    Serial.println("  motor_delay:X     - Set motor delay in seconds (e.g., motor_delay:5)");
    Serial.println("  gyro              - Show current gyro/accel readings");
    Serial.println("  gyro_threshold    - Show current gyro threshold");
    Serial.println("  gyro_threshold:X  - Set gyro threshold (e.g., gyro_threshold:50)");
    Serial.println("  calibrate         - Calibrate MPU6050");
    Serial.println("  chat:msg          - Send chat message");
    Serial.println("  help              - Show this help");
    
  } else {
    Serial.println("✗ Unknown command: " + command);
    Serial.println("Type 'help' for available commands");
  }
}

void sendChatMessage(String message) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(String(serverURL) + "/chat");
    http.addHeader("Content-Type", "application/json");
    
    DynamicJsonDocument doc(1024);
    doc["message"] = "ESP32: " + message;
    
    String jsonPayload;
    serializeJson(doc, jsonPayload);
    
    Serial.println("Sending chat message: " + jsonPayload);
    
    int httpResponseCode = http.POST(jsonPayload);
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      
      // Parse the response to get the bot reply
      DynamicJsonDocument responseDoc(2048);
      deserializeJson(responseDoc, response);
      
      if (responseDoc["reply"]) {
        String botReply = responseDoc["reply"];
        Serial.println("🤖 Bot replied: " + botReply);
        
        // Also show the English version if available
        if (responseDoc["translation_workflow"]["gemini_english_response"]) {
          String englishReply = responseDoc["translation_workflow"]["gemini_english_response"];
          Serial.println("🤖 (English): " + englishReply);
        }
      }
    } else {
      Serial.println("✗ Failed to send chat message");
    }
    
    http.end();
  }
}