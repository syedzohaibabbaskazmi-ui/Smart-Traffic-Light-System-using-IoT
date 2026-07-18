# Smart Traffic Light System using IoT

An adaptive, sensor-driven 4-way intersection traffic management system built with Arduino. This system moves beyond traditional fixed-timer traffic lights by dynamically adjusting green phases based on real-time vehicle presence, reducing congestion, wait times, and fuel consumption.

## 📌 Project Overview
Traditional traffic control systems rely on static time intervals, leading to inefficient cycles where empty lanes receive green lights while crowded lanes face unnecessary delays. This project implements a responsive IoT-based architecture that:
- Monitored 4 independent lanes using Passive Infrared (PIR) sensors to detect real-time vehicle/traffic presence.
- Uses a centralized deterministic control loop to safely re-allocate green phases to lanes with active traffic.
- Employs multi-stage transition logic (Warning, All-Red Safety Buffer, and Execution) along with audio-visual signaling (12-LED array and a Piezo buzzer) to ensure pedestrian and vehicular safety.

---

## 🛠️ System Architecture & Component Mapping

The system architecture is broken down into three main functional segments: **Input (Sensors)**, **Processing (Microcontroller)**, and **Output (Visual & Audible Indicators)**.

### Hardware Components
1. **Microcontroller:** Arduino Uno R3 (Central Processing Unit)
2. **Sensors:** 4 × PIR Motion Sensors (One positioned per lane)
3. **Visual Outputs:** 12 × LEDs grouped into Red, Yellow, and Green arrays for 4 lanes.
4. **Current Limiters:** 12 × 220Ω–330Ω Resistors (To protect the LED configurations)
5. **Audible Output:** 1 × Piezo Buzzer (For pedestrian and transition alerts)
6. **Prototyping:** 1 × Full-Sized Breadboard & solid-core jumper wires

### Hardware Wiring Breakdown & Pin Mappings

| Component | Pin Type | Arduino Pin | Description |
| :--- | :--- | :--- | :--- |
| **PIR Sensor 1** | Digital Input | `Pin 2` | Lane 1 Vehicle Presence Detector |
| **PIR Sensor 2** | Digital Input | `Pin 3` | Lane 2 Vehicle Presence Detector |
| **PIR Sensor 3** | Digital Input | `Pin 4` | Lane 3 Vehicle Presence Detector |
| **PIR Sensor 4** | Digital Input | `Pin 5` | Lane 4 Vehicle Presence Detector |
| **Lane 1 Red LED** | Digital Output | `Pin 6` | Lane 1 Stop Signal |
| **Lane 1 Yellow LED**| Digital Output | `Pin 7` | Lane 1 Transition Warning Signal |
| **Lane 1 Green LED** | Digital Output | `Pin 8` | Lane 1 Go Signal |
| **Lane 2 Red LED** | Digital Output | `Pin 9` | Lane 2 Stop Signal |
| **Lane 2 Yellow LED**| Digital Output | `Pin 10` | Lane 2 Transition Warning Signal |
| **Lane 2 Green LED** | Digital Output | `Pin 11` | Lane 2 Go Signal |
| **Lane 3 Red LED** | Digital/Analog | `Pin A0` | Lane 3 Stop Signal |
| **Lane 3 Yellow LED**| Digital/Analog | `Pin A1` | Lane 3 Transition Warning Signal |
| **Lane 3 Green LED** | Digital/Analog | `Pin A2` | Lane 3 Go Signal |
| **Lane 4 Red LED** | Digital/Analog | `Pin A3` | Lane 4 Stop Signal |
| **Lane 4 Yellow LED**| Digital/Analog | `Pin A4` | Lane 4 Transition Warning Signal |
| **Lane 4 Green LED** | Digital/Analog | `Pin A5` | Lane 4 Go Signal |
| **Piezo Buzzer** | Digital Output | `Pin 12` | Audible Transition Sequence Warning |

---

## 🔄 State Machine & Intersection Shift Logic

The intersection shifts priority deterministically using a secure 3-stage transition pipeline to prevent cross-lane collisions:

1. **Warning Phase (2.0s Total):** The active lane's Green LED turns `LOW`, and its Yellow LED turns `HIGH`. Concurrently, the Piezo buzzer executes 3 distinct pulses (200ms tone at 1kHz, 400ms delay) over a 1.2s window to alert drivers and pedestrians.
2. **Buffer Phase (1.0s Total):** The active lane's Yellow LED turns `LOW`, and its Red LED turns `HIGH`. For a safety window of exactly 1 second, **all 4 lanes are held at Red** to allow clearing of the intersection center.
3. **Execution Phase:** The target lane's Red LED drops to `LOW`, and its Green LED goes `HIGH`. The global tracking variable updates to the new lane index, and a minimum **4-second hold time** is enforced to prevent rapid, erratic shifting.

---

## 💻 Firmware Code (`smart_traffic_light.ino`)

Below is the structured, modular code ready to be loaded into your Arduino IDE:

```cpp
/**
 * Smart Traffic Light Management System
 * Adaptive 4-Lane IoT Traffic Intersection Controller
 */

// --- Pin Allocations ---
const int sensorPins[4] = {2, 3, 4, 5};     // PIR Inputs for Lanes 1-4
const int redPins[4]    = {6, 9, A0, A3};   // Red LED Outputs
const int yellowPins[4] = {7, 10, A1, A4};  // Yellow LED Outputs
const int greenPins[4]  = {8, 11, A2, A5};  // Green LED Outputs

const int buzzerPin = 12; // Piezo Buzzer Pin

// --- State Variables ---
int activeLane = 0; // Starts with Lane 1 active (Index 0)
const unsigned long minGreenTime = 4000; // 4-second mandatory hold time

void setup() {
  // Initialize Serial Monitor for debugging
  Serial.begin(9600);
  Serial.println("--- Smart Traffic Light System Initialized ---");

  // Configure Pin Modes using clean loop structures
  for (int i = 0; i < 4; i++) {
    pinMode(sensorPins[i], INPUT);
    pinMode(redPins[i], OUTPUT);
    pinMode(yellowPins[i], OUTPUT);
    pinMode(greenPins[i], OUTPUT);
    
    // Set baseline state: All lanes Red initially
    digitalWrite(redPins[i], HIGH);
    digitalWrite(yellowPins[i], LOW);
    digitalWrite(greenPins[i], LOW);
  }
  
  pinMode(buzzerPin, OUTPUT);

  // Set initial state: Open Lane 1 explicitly
  digitalWrite(redPins[activeLane], LOW);
  digitalWrite(greenPins[activeLane], HIGH);
  Serial.println("Lane 1 is initially ACTIVE.");
}

void loop() {
  // Continuously poll sensors for all inactive lanes
  for (int i = 0; i < 4; i++) {
    // Skip checking the lane that currently has the green light
    if (i == activeLane) {
      continue;
    }

    // Read vehicle presence sensor
    int vehicleDetected = digitalRead(sensorPins[i]);

    if (vehicleDetected == HIGH) {
      Serial.print("Vehicle detected on inactive Lane ");
      Serial.println(i + 1);
      
      // Execute safe transition sequence
      switchLanes(activeLane, i);
      
      // Enforce post-transition hold time before allowing another switch
      delay(minGreenTime);
      break; // Exit poll loop to reset monitoring state
    }
  }
}

/**
 * Safely transitions traffic priority from the current active lane to the next requested lane.
 */
void switchLanes(int current, int next) {
  Serial.print("Transitioning priority from Lane ");
  Serial.print(current + 1);
  Serial.print(" to Lane ");
  Serial.println(next + 1);

  // --- 1. WARNING PHASE ---
  digitalWrite(greenPins[current], LOW);
  digitalWrite(yellowPins[current], HIGH);

  // Pulse buzzer 3 times for pedestrian awareness
  for (int b = 0; b < 3; b++) {
    tone(buzzerPin, 1000, 200); // Beep at 1kHz for 200ms
    delay(400);                // Clear window between beeps
  }
  delay(800); // Complete remainder of the 2-second yellow window

  // --- 2. BUFFER PHASE (All-Red Safety Window) ---
  digitalWrite(yellowPins[current], LOW);
  digitalWrite(redPins[current], HIGH);
  delay(1000); // Hold all intersections red for 1.0 second

  // --- 3. EXECUTION PHASE ---
  digitalWrite(redPins[next], LOW);
  digitalWrite(greenPins[next], HIGH);

  // Update tracking state
  activeLane = next;
  Serial.print("Lane ");
  Serial.print(next + 1);
  Serial.println(" is now ACTIVE.");
}
```

---

## 🚀 How to Run the Project

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/smart-traffic-light-iot.git
   cd smart-traffic-light-iot
   ```
2. **Setup Hardware:** Assemble the components according to the [Hardware Wiring Breakdown](#hardware-wiring-breakdown--pin-mappings) table on a breadboard.
3. **Flash Firmware:** Open `smart_traffic_light.ino` inside the Arduino IDE, connect your Arduino Uno via USB, select the correct COM port, and click **Upload**.
4. **Monitor Outputs:** Open the Serial Monitor at `9600 baud` to view real-time transition logs as sensors trigger state shifts.

## 📈 Scalability & Future Work
- **Non-blocking Code Framework:** Migrate from standard `delay()` calls to a `millis()` timer-driven structure to enable asynchronous multitasking.
- **Advanced Sensor Integration:** Introduce Ultrasonic or Radar sensors to measure exact vehicular queue lengths instead of binary presence.
- **Cloud Analytics:** Connect an ESP8266/ESP32 Wi-Fi module to stream intersection throughput data to an IoT cloud dashboard (e.g., Blynk, ThingsPeak) for smart city telemetry.

## 👥 Contributors
- **Muhamad Sohaib Nisar**
- **Agha Zulkifal Nadeem**
- **Syed Zohaib Kazmi**
