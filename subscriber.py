import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
from datetime import datetime
import sys

BROKER_IP = "157.173.101.159"  # Your VPS IP address
PORT = 1883
TOPIC = "exam/izere_joshua/temperature"

def on_connect(client, userdata, flags, rc, properties=None):
    # rc is the connection result code
    # In Paho MQTT v2, rc is a ReasonCode object or integer. 0 represents success.
    if rc == 0 or (repr(rc) == "Success" or getattr(rc, "is_failure", lambda: False)() == False):
        print(f"[MQTT] Connected successfully. Subscribing to topic: {TOPIC}")
        client.subscribe(TOPIC)
    else:
        print(f"[MQTT ERROR] Connection failed with code {rc}")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode('utf-8')
        temp = float(payload)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] Topic: {msg.topic} | Temperature: {temp:.2f} °C")
    except Exception as e:
        print(f"[ERROR] Failed to parse message: {e}")

def main():
    print("=" * 60)
    print("           MQTT Temperature Subscriber Client")
    print("=" * 60)

    broker_ip = BROKER_IP
    if len(sys.argv) > 1:
        broker_ip = sys.argv[1]

    # Create client with Paho 2.x API version
    client = mqtt.Client(CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        print(f"[MQTT] Connecting to broker at {broker_ip}:{PORT}...")
        client.connect(broker_ip, PORT, 60)
    except Exception as e:
        print(f"[MQTT ERROR] Failed to connect: {e}")
        print("Please check your broker IP and configuration.")
        sys.exit(1)

    print("Listening for messages... Press Ctrl+C to exit.")
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nDisconnecting subscriber...")
    finally:
        client.disconnect()
        print("Subscriber stopped.")

if __name__ == "__main__":
    main()