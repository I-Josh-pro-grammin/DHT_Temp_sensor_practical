# Temperature Display and MQTT Monitoring System

This repository contains the complete implementation for the **SPE (Embedded Systems Software Integration)** practical exam, completed by **IZERE Joshua**.

The system reads real-time temperature data from a DHT11 sensor using an Arduino Uno, displays the candidate's name (with smooth scrolling) and temperature value on a 16x2 I2C LCD, transmits the telemetry via USB Serial to a PC bridge script, and publishes the data to an MQTT broker on the VPS, which is visualized on a real-time Web Dashboard.

---

## 1. System Architecture

### Data Flow Diagram
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

## 3. How the System Was Developed ("How I Did It")

This section explains the design and development decisions made across the four main layers of the IoT stack:

### A. Firmware Development (Arduino Uno)
*   **Non-Blocking Execution (`millis()`)**: To prevent the LCD name scrolling from lagging, I replaced traditional `delay()` statements with `millis()` counters. This allows two independent tasks to run concurrently:
    *   **Scrolling Thread**: Row 1 shifts the candidate's name (e.g. `IZERE JOSHUA - SPE CANDIDATE`) horizontally every `350ms` for smooth text movement.
    *   **Sensor Thread**: The DHT11 temperature sensor is read and printed to Serial every `2000ms`.
*   **Board-Level Simulation Fallback**: If the DHT11 sensor is missing or disconnected (returning `NaN`), the board automatically generates simulated sinusoidal temperature telemetry (around 24.5°C). This allows end-to-end hardware testing without needing the sensor physically attached.

### B. PC Bridge Client (Python)
*   **Auto-Port Detection**: The bridge script scans all available system COM ports and identifies the Arduino Uno (connecting to `COM6` on our test environment).
*   **Bluetooth Filter**: It explicitly ignores virtual Bluetooth serial ports (which cause blocking timeouts) and targets true USB serial chips.
*   **Communication Bridge**: It parses incoming Serial ASCII data, converts it to float values, prints them locally, and uses `paho-mqtt` (upgraded for Paho 2.x API) to publish to the VPS.

### C. Server-Side MQTT Broker (VPS)
*   **Dual Protocol Setup**: I configured the **Mosquitto** broker on the VPS (`157.173.101.159`) to handle both protocol channels:
    *   **TCP (Port 1883)**: Handles incoming data from the Python serial bridge and subscribes CLI clients.
    *   **WebSockets (Port 9001)**: Allows browser-based dashboards to subscribe to data directly.

### D. Real-Time Telemetry Dashboard (Frontend)
*   **Glassmorphism UI**: Designed a premium dashboard using Vanilla CSS. It features glowing, color-coded temperature cards (Emerald for Comfortable, Red for Hot, Teal for Cold).
*   **Dynamic Visualizations**: Integrates `Chart.js` via CDN to plot a rolling line chart of the last 20 temperature samples, and standard `mqtt.js` to handle WebSockets connections.
*   **VPS Deployment**: The file `index.html` was uploaded via `ssh` to the VPS directory `/var/www/html/emg40/` and is served continuously in the background using Python's http server on port `8040`.

---

## 4. Hardware Connections & Wiring Diagram

Wire the physical components to the Arduino Uno according to the following layout:

### I2C LCD Display (16x2) Wiring
| I2C Pin | Arduino Uno Pin | Description |
| :--- | :--- | :--- |
| **GND** | GND | Ground reference |
| **VCC** | 5V | Power supply (5V) |
| **SDA** | A4 | I2C Data Line (Serial Data) |
| **SCL** | A5 | I2C Clock Line (Serial Clock) |

*Note: The blue potentiometer on the back of the I2C module adjusts contrast. Turn it with a small screwdriver until characters appear.*

### DHT11 Temperature Sensor Wiring
| DHT11 Pin | Arduino Uno Pin | Description |
| :--- | :--- | :--- |
| **VCC** | 5V | Power supply (5V) |
| **DATA** | D7 | Digital Signal Pin |
| **GND** | GND | Ground reference |

---

## 5. VPS MQTT Broker Installation (From Scratch)

If you are cloning this repository and need to set up a new MQTT broker on a Linux VPS, run the following commands:

```bash
# 1. Install Mosquitto Broker and Clients
sudo apt update && sudo apt install -y mosquitto mosquitto-clients

# 2. Configure listeners for standard TCP and WebSockets
sudo tee /etc/mosquitto/conf.d/default.conf <<EOF
listener 1883
allow_anonymous true

listener 9001
protocol websockets
allow_anonymous true
EOF

# 3. Open ports in the firewall
sudo ufw allow 1883/tcp
sudo ufw allow 9001/tcp

# 4. Restart and enable the service
sudo systemctl restart mosquitto
sudo systemctl enable mosquitto
```

---

## 6. How to Install & Use the Application

### A. Local PC Installation
1. Install **Python 3** on your PC.
2. Install the necessary Python packages:
   ```bash
   py -m pip install pyserial paho-mqtt
   ```
3. Install the **LiquidCrystal I2C by Frank de Brabander** library in the Arduino IDE:
   * Go to **Sketch** ──► **Include Library** ──► **Manage Libraries...**
   * Search for: `LiquidCrystal I2C` and install it.

### B. Running the Firmware
1. Open `sketch_jun16a/sketch_jun16a.ino` in the Arduino IDE.
2. Under `tools`, select Board: **Arduino Uno** and select your active COM Port.
3. Verify and **Upload** the sketch to your board.

### C. Running the PC Bridge
1. **Close the Arduino Serial Monitor** (to release the COM port).
2. Start the serial-to-MQTT bridge on your local PC:
   ```bash
   py mqtt_serial.py
   ```
   *The script will connect to the Arduino and begin forwarding data to the VPS broker.*

### D. Launching the Web Dashboard
Open the deployed link in your browser:
👉 **[http://157.173.101.159:8040/index.html](http://157.173.101.159:8040/index.html)**
*(Click **Connect** to start receiving live readings).*

---

## 7. Communication Specifications
*   **Serial Port Baud Rate**: `9600` (8N1)
*   **MQTT Broker IP**: `157.173.101.159`
*   **MQTT Port (TCP)**: `1883` (for Python bridge)
*   **MQTT Port (WebSockets)**: `9001` (for Web Dashboard)
*   **MQTT Topic**: `exam/izere_joshua/temperature`
