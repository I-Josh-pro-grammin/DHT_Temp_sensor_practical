import serial
import paho.mqtt.client as mqtt
from datetime import datetime
import time

SERIAL_PORT = "COM3"
BAUD_RATE = 9600

BROKER_IP = "192.168.1.100"
BROKER_PORT = 1883

TOPIC = "temperature/monitoring"

client = mqtt.Client()

client.connect(BROKER_IP, BROKER_PORT, 60)

ser = serial.Serial(
    SERIAL_PORT,
    BAUD_RATE,
    timeout=1
)

time.sleep(2)

print("Monitoring Started...\n")

while True:

    try:

        if ser.in_waiting:

            temp = (
                ser.readline()
                .decode()
                .strip()
            )

            current_time = (
                datetime.now()
                .strftime("%H:%M:%S")
            )

            print(
                f"[{current_time}] "
                f"Temperature = {temp} °C"
            )

            client.publish(
                TOPIC,
                temp
            )

    except KeyboardInterrupt:
        break

ser.close()
client.disconnect()