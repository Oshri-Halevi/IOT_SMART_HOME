import argparse
import json
import random
import time
import paho.mqtt.client as mqtt

BROKER_HOST = "broker.hivemq.com"
BROKER_PORT = 8884

parser = argparse.ArgumentParser()
parser.add_argument("--slot-id", type=int, required=True)
args = parser.parse_args()

client = mqtt.Client(
    client_id=f"slot-sensor-{args.slot_id}",
    transport="websockets"
)
client.tls_set()
client.connect(BROKER_HOST, BROKER_PORT, 60)
client.loop_start()

occupied = False
topic = f"parking/slot/{args.slot_id}/status"

while True:
    if random.random() < 0.4:
        occupied = not occupied

    client.publish(
        topic,
        json.dumps({
            "slot_id": args.slot_id,
            "occupied": occupied
        }),
        retain=True
    )
    time.sleep(5)
