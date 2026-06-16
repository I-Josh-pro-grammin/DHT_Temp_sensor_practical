import serial
import serial.tools.list_ports
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
from datetime import datetime
import time
import random
import sys

# CONFIGURATION
MQTT_BROKER = "localhost"  # Change to your VPS IP when ready!
MQTT_PORT = 1883
MQTT_TOPIC = "temperature/monitoring"
BAUD_RATE = 9600

def detect_serial_port():
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        return None
    
    # Try to find Arduino or common USB-to-Serial chips
    for p in ports:
        desc = p.description.lower()
        if "arduino" in desc or "ch340" in desc or "usb" in desc or "serial" in desc:
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
            time.sleep(2)  # Wait for Arduino to reset
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
                if ser.in_waiting:
                    try:
                        line = ser.readline().decode('utf-8', errors='ignore').strip()
                        if line:
                            # Validate if we received a numerical temperature reading
                            temp = float(line)
                            publish_temp(client, temp, broker_ip)
                    except ValueError:
                        # Raw startup text or noise from Arduino serial port
                        pass
                    except Exception as e:
                        print(f"[ERROR] Serial read failed: {e}")
                time.sleep(0.1) # Prevent CPU throttling
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