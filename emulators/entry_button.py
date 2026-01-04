import json
import paho.mqtt.client as mqtt

BROKER_HOST = "broker.hivemq.com"
BROKER_PORT = 8884

client = mqtt.Client(
    client_id="entry-button",
    transport="websockets"
)
client.tls_set()
client.connect(BROKER_HOST, BROKER_PORT, 60)
client.loop_start()

print("Press ENTER to simulate entry request")
while True:
    input()
    client.publish(
        "parking/entry/button",
        json.dumps({"pressed": True}),
        retain=False
    )
