import serial
import serial.tools.list_ports
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
from datetime import datetime
import time
import random
import sys

# CONFIGURATION
MQTT_BROKER = "157.173.101.159"  # Your VPS IP address
MQTT_PORT = 1883
MQTT_TOPIC = "exam/izere_joshua/temperature"
BAUD_RATE = 9600

def detect_serial_port():
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        return None
    
    # 1. Try to find Arduino or USB-to-Serial chips specifically, excluding Bluetooth
    for p in ports:
        desc = p.description.lower()
        if "bluetooth" in desc or "bt link" in desc:
            continue
        if "arduino" in desc or "ch340" in desc or "usb" in desc or "usb-to-serial" in desc:
            return p.device
            
    # 2. General fallback excluding Bluetooth
    for p in ports:
        desc = p.description.lower()
        if "bluetooth" not in desc and "bt link" not in desc:
            return p.device
            
    return ports[0].device

def main():
    print("=" * 60)
    print("   Temperature Display and MQTT Serial Bridge")
    print("=" * 60)

    # Let user override broker IP via command line if needed
    broker_ip = MQTT_BROKER
    if len(sys.argv) > 1:
        broker_ip = sys.argv[1]
    
    # Construct MQTT Client with Paho 2.x API version
    client = mqtt.Client(CallbackAPIVersion.VERSION2)
    
    try:
        print(f"[MQTT] Connecting to broker at {broker_ip}:{MQTT_PORT}...")
        client.connect(broker_ip, MQTT_PORT, 60)
        client.loop_start()
        print("[MQTT] Successfully connected to broker.")
    except Exception as e:
        print(f"[MQTT ERROR] Could not connect to broker: {e}")
        print("[MQTT] Running in local offline mode (data will only print to console).")

    # Detect Serial Port
    port = detect_serial_port()
    simulation_mode = False
    ser = None

    if port:
        print(f"[SERIAL] Detected serial port: {port}")
        try:
            ser = serial.Serial(port, BAUD_RATE, timeout=1)
            time.sleep(2)  # Wait for Arduino to initialize
            print(f"[SERIAL] Successfully connected to Arduino on {port}")
        except Exception as e:
            print(f"[SERIAL ERROR] Could not open {port}: {e}")
            simulation_mode = True
    else:
        print("[SERIAL] No physical serial ports detected.")
        simulation_mode = True

    if simulation_mode:
        print("\n" + "*" * 60)
        print("  RUNNING IN SIMULATION MODE (Mock Data Generator)")
        print("  Reason: No Arduino detected or serial connection failed.")
        print("  (Publishing random temperature data every 2 seconds)")
        print("*" * 60 + "\n")

    try:
        while True:
            if not simulation_mode and ser is not None:
                try:
                    # readline() blocks until a line is received or timeout (1s) expires
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        print(f"[SERIAL DEBUG] Raw Line: '{line}'")
                        temp = float(line)
                        publish_temp(client, temp, broker_ip)
                except ValueError:
                    print(f"[SERIAL DEBUG] Ignored non-numeric: '{line}'")
                except Exception as e:
                    print(f"[ERROR] Serial read failed: {e}")
                    time.sleep(1)  # Wait before retrying on read error
            else:
                # Simulation mode
                temp = round(random.uniform(22.0, 29.5), 2)
                publish_temp(client, temp, broker_ip)
                time.sleep(2)

    except KeyboardInterrupt:
        print("\nShutting down monitoring...")
    finally:
        if ser is not None:
            ser.close()
        client.loop_stop()
        client.disconnect()
        print("Bridge stopped.")

def publish_temp(client, temp, broker_ip):
    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"[{current_time}] Readout: {temp:.2f} °C")
    
    try:
        result = client.publish(MQTT_TOPIC, payload=str(temp))
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            print(f"[MQTT WARNING] Failed to publish message (Code {result.rc})")
    except Exception as e:
        print(f"[MQTT ERROR] Publish failed: {e}")

if __name__ == "__main__":
    main()