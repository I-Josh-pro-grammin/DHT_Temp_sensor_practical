# Temperature Display and MQTT Monitoring System

This repository contains the complete implementation for the **SPE (Embedded Systems Software Integration)** practical exam, completed by **IZERE Joshua**.

The system reads real-time temperature data from a DHT11 sensor using an Arduino Uno, displays the candidate's name (with smooth scrolling) and temperature value on a 16x2 LCD, transmits the telemetry via USB Serial to a PC bridge script, and publishes the data to an MQTT broker on the VPS, which is visualized on a real-time Web Dashboard.

---

## 1. System Architecture

```
[DHT11 Temp Sensor] 
       │ (Data Pin D7)
       ▼
 [Arduino Uno] ──► [16x2 I2C LCD Display] (Local Display & Name Scrolling)
       │ (USB Serial @ 9600 Baud)
       ▼
 [PC Bridge Client] (mqtt_serial.py - reads Serial, auto-port, simulation fallback)
       │ (MQTT Protocol over TCP Port 1883)
       ▼
 [MQTT Broker] (Hosted on VPS @ 157.173.101.159)
       ├──► [PC CLI Subscriber] (subscriber.py - logs data for testing)
       └──► [Web Dashboard] (index.html - Live Chart/Gauge on Port 8040)
```

---

## 2. Deployed Dashboard URL

The real-time telemetry dashboard is fully deployed and running on the VPS at:
👉 **[http://157.173.101.159:8040/index.html](http://157.173.101.159:8040/index.html)**

---

## 3. Hardware Connections

Connect your components to the Arduino Uno as follows:

### I2C LCD Display (16x2) Wiring
*   **GND** ──► Arduino **GND**
*   **VCC** ──► Arduino **5V**
*   **SDA** ──► Arduino Analog Pin **A4** (or dedicated SDA pin)
*   **SCL** ──► Arduino Analog Pin **A5** (or dedicated SCL pin)

*Note: Turn the blue potentiometer on the back of the I2C backpack module to adjust contrast.*

### DHT11 Temperature Sensor Wiring
*   **VCC** ──► Arduino **5V**
*   **DATA** ──► Arduino Digital Pin **D7**
*   **GND** ──► Arduino **GND**

---

## 4. How to Use the Application

### Prerequisites
1. Ensure Python 3 is installed on your PC.
2. Install the required libraries:
   ```bash
   py -m pip install pyserial paho-mqtt
   ```
3. Install the **LiquidCrystal I2C by Frank de Brabander** library in the Arduino IDE (Sketch -> Include Library -> Manage Libraries).

### Running the System
1. **Upload the Sketch**: Open `sketch_jun16a/sketch_jun16a.ino` in the Arduino IDE, select board **Arduino Uno**, and upload it.
2. **Start the PC Bridge**: Close the Arduino Serial Monitor and run the bridge script on your PC:
   ```bash
   py mqtt_serial.py
   ```
   *The script automatically detects the Arduino on COM6 and begins forwarding data to the VPS broker.*
3. **Open the Dashboard**: Visit **[http://157.173.101.159:8040/index.html](http://157.173.101.159:8040/index.html)** in any browser and click **Connect** to see the live gauge and line chart updates.
4. **Subscribe via CLI (Optional)**: To monitor the MQTT feed directly from the command line, run:
   ```bash
   py subscriber.py
   ```

---

## 5. Communication Specifications
*   **Serial Port Baud Rate**: `9600` (8N1)
*   **MQTT Broker IP**: `157.173.101.159`
*   **MQTT Port (TCP)**: `1883` (for Python bridge)
*   **MQTT Port (WebSockets)**: `9001` (for Web Dashboard)
*   **MQTT Topic**: `exam/izere_joshua/temperature`
