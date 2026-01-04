import json
import time
import paho.mqtt.client as mqtt

BROKER_HOST = "broker.hivemq.com"
BROKER_PORT = 8884

state = "CLOSED"

def on_message(client, userdata, msg):
    global state
    data = json.loads(msg.payload.decode())
    state = data["action"]
    print("Gate:", state)
    client.publish(
        "parking/gate/relay",
        json.dumps({"state": state}),
        retain=True
    )

client = mqtt.Client(
    client_id="gate-relay",
    transport="websockets"
)
client.tls_set()
client.on_message = on_message
client.connect(BROKER_HOST, BROKER_PORT, 60)
client.subscribe("parking/gate/command")
client.loop_start()

client.publish(
    "parking/gate/relay",
    json.dumps({"state": state}),
    retain=True
)

while True:
    time.sleep(1)
