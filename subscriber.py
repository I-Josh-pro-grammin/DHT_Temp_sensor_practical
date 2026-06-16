import paho.mqtt.client as mqtt

BROKER_IP = "YOUR_VPS_IP"
PORT = 1883

TOPIC = "temperature/monitoring"

def on_message(client, userdata, msg):

    print(
        f"Received: "
        f"{msg.payload.decode()}"
    )

client = mqtt.Client()

client.on_message = on_message

client.connect(
    BROKER_IP,
    PORT,
    60
)

client.subscribe(TOPIC)

print("Listening...")

client.loop_forever()