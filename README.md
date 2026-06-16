# Temperature Display and MQTT Monitoring System

This project is a complete solution for the **SPE (Embedded Systems Software Integration)** practical exam. It implements a temperature monitoring system that reads sensor data from an Arduino Uno, displays it locally on a 16x2 LCD (with horizontal scrolling for long names), transmits it over USB Serial to a PC-side bridge, publishes it to an MQTT Broker on a VPS, and visualizes it in real time on a premium Web Dashboard.

---

## 1. System Architecture

### Data Flow Diagram
```
[DHT11 Temp Sensor] 
       │ (Data Pin D7)
       ▼
 [Arduino Uno] ──► [16x2 LCD Display] (Local Display & Name Scrolling)
       │ (USB Serial @ 9600 Baud)
       ▼
 [PC Bridge Client] (mqtt_serial.py - reads Serial, auto-port, simulation fallback)
       │ (MQTT Protocol over TCP Port 1883)
       ▼
 [MQTT Broker] (Hosted on VPS - e.g., Mosquitto)
       ├──► [PC CLI Subscriber] (subscriber.py - logs data for testing)
       └──► [Web Dashboard] (index.html - Live Chart/Gauge over WebSockets Port 9001)
```

---

## 2. Hardware Wiring Instructions

Connect the **DHT11 Sensor** and the **16x2 I2C LCD Display** to the **Arduino Uno** according to the following pin map:

### I2C LCD Display (16x2) Wiring
| LCD I2C Pin | Arduino Uno Pin | Description |
| :--- | :--- | :--- |
| **GND** | GND | Ground |
| **VCC** | 5V | Power (5V) |
| **SDA** | A4 (or dedicated SDA pin) | I2C Data Line |
| **SCL** | A5 (or dedicated SCL pin) | I2C Clock Line |

*Note: The blue potentiometer on the back of the I2C LCD module board adjusts the screen contrast. Turn it with a small screwdriver if the screen shows white blocks or nothing.*

### DHT11 Temperature Sensor Wiring
| DHT11 Pin | Arduino Uno Pin | Description |
| :--- | :--- | :--- |
| **VCC** | 5V | Power (5V) |
| **DATA** | D7 | Digital Signal Pin |
| **GND** | GND | Ground |

---

## 3. VPS MQTT Broker Setup (From Scratch)

To host your own MQTT broker on your VPS (typically running Ubuntu/Debian), follow these steps:

### Step 1: Install Mosquitto Broker
Log into your VPS via SSH and run the following commands:
```bash
sudo apt update
sudo apt install -y mosquitto mosquitto-clients
```

### Step 2: Configure Mosquitto for Web & TCP Clients
By default, Mosquitto does not allow anonymous external connections and doesn't enable WebSockets. We must configure both.
Create or edit a custom configuration file:
```bash
sudo nano /etc/mosquitto/conf.d/default.conf
```
Paste the following configuration:
```ini
# Enable standard MQTT over TCP port 1883 (for the Python PC bridge)
listener 1883
allow_anonymous true

# Enable MQTT over WebSockets port 9001 (for the Web Dashboard)
listener 9001
protocol websockets
allow_anonymous true
```
Save and exit (`Ctrl+O`, `Enter`, then `Ctrl+X`).

### Step 3: Configure the Firewall
Allow incoming traffic on both ports (1883 and 9001):
```bash
sudo ufw allow 1883/tcp
sudo ufw allow 9001/tcp
```

### Step 4: Restart Mosquitto Service
Restart Mosquitto to apply the changes:
```bash
sudo systemctl restart mosquitto
sudo systemctl enable mosquitto
```
Verify it is running:
```bash
sudo systemctl status mosquitto
```

---

## 4. Software Setup & Run Guide

### Prerequisite: Install Python Packages
Open a terminal on your PC and run:
```bash
py -m pip install pyserial paho-mqtt
```

### Option A: Local Simulation Mode (Testing Without Hardware)
If your Arduino is not connected yet, you can test the entire pipeline using **Simulation Mode**:

1. **Start the PC Bridge**:
   Edit [mqtt_serial.py](file:///d:/CODES/Embedded%20Exam/mqtt_serial.py) and change `MQTT_BROKER = "localhost"` to your **VPS IP address**.
   Then, run:
   ```bash
   py mqtt_serial.py
   ```
   *Note: Because no Arduino is detected, the script will automatically switch to **Simulation Mode** and generate mock temperature readings every 2 seconds.*

2. **Verify with Subscriber Client**:
   Edit [subscriber.py](file:///d:/CODES/Embedded%20Exam/subscriber.py) and change `BROKER_IP = "localhost"` to your **VPS IP address**.
   Run:
   ```bash
   py subscriber.py
   ```
   *You will see the subscriber log the readings in real-time.*

3. **Open the Web Dashboard**:
   Open [index.html](file:///d:/CODES/Embedded%20Exam/index.html) in your browser.
   - Enter your **VPS IP** as the Host.
   - Enter `9001` as the WebSocket Port.
   - Click **Connect**. The dashboard will display a live glowing gauge and line chart plotting the readings.

### Option B: Hardware Mode (Running on Physical Arduino)
1. Open [sketch_jun16a.ino](file:///d:/CODES/Embedded%20Exam/sketch_jun16a/sketch_jun16a.ino) in the Arduino IDE.
2. Edit `candidateName` on line 11 to your own name.
3. Wire the circuit as shown in Section 2.
4. Select board **Arduino Uno**, select your COM port, compile and upload the sketch.
5. Make sure the Arduino Serial Monitor is closed (to free the serial port).
6. Run `py mqtt_serial.py` on your PC. It will automatically detect your Arduino, establish a connection, and start forwarding data to your VPS broker!

---

## 5. Communication Specifications

*   **Serial Communication Port (PC to Arduino)**:
    *   **Baud Rate**: 9600
    *   **Data Format**: 8 Data bits, No parity, 1 Stop bit (8N1)
    *   **Connection**: USB-to-Serial
*   **MQTT Configuration**:
    *   **Topic used for publishing**: `temperature/monitoring`
    *   **TCP Port (Python Scripts)**: `1883`
    *   **WebSocket Port (Web Dashboard)**: `9001`

---

## 6. How to Deploy the Dashboard on GitHub Pages

You can host the dashboard directly from your GitHub repository for free:
1. Push your repository to GitHub.
2. Go to your repository settings on GitHub.
3. Click on **Pages** in the left sidebar.
4. Under **Build and deployment**, set the Source to **Deploy from a branch**.
5. Select the **main** (or **master**) branch and folder `/ (root)`.
6. Click **Save**.
7. Within a couple of minutes, your dashboard will be live at: `https://<your-username>.github.io/<your-repo-name>/`
8. This is the link you can paste into the Google Form submission under "dashboard link"!
