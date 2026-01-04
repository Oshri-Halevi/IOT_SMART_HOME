import json
import time
import threading
import paho.mqtt.client as mqtt
from db_manager import DBManager

BROKER_HOST = "broker.hivemq.com"
BROKER_PORT = 8884

TOTAL_SLOTS = 5

TOPIC_SLOT = "parking/slot/+/status"
TOPIC_BUTTON = "parking/entry/button"
TOPIC_GATE_CMD = "parking/gate/command"
TOPIC_GATE_STATUS = "parking/gate/relay"

TOPIC_INFO = "parking/system/info"
TOPIC_WARNING = "parking/system/warning"
TOPIC_ALARM = "parking/system/alarm"


class DataManager:
    def __init__(self):
        self.db = DBManager()
        self.slots = {i: False for i in range(1, TOTAL_SLOTS + 1)}
        self.gate_state = "CLOSED"

        self.client = mqtt.Client(
            client_id="smartparking-data-manager",
            transport="websockets"
        )
        self.client.tls_set()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def connect(self):
        print("Connecting to HiveMQ (WSS 8884)...")
        self.client.connect(BROKER_HOST, BROKER_PORT, 60)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print("Connected, rc =", rc)
        client.subscribe(TOPIC_SLOT)
        client.subscribe(TOPIC_BUTTON)
        client.subscribe(TOPIC_GATE_STATUS)

    def free_slots(self):
        return sum(1 for v in self.slots.values() if not v)

    def publish(self, topic, msg, retain=True):
        self.client.publish(topic, json.dumps(msg), retain=retain)

    def on_message(self, client, userdata, msg):
        data = json.loads(msg.payload.decode())

        if msg.topic.startswith("parking/slot/"):
            slot_id = data["slot_id"]
            occupied = data["occupied"]

            self.slots[slot_id] = occupied
            self.db.update_slot(slot_id, occupied)

            free = self.free_slots()
            if free == 0:
                self.publish(TOPIC_ALARM, {"message": "Parking FULL"})
                self.publish(TOPIC_GATE_CMD, {"action": "CLOSE"}, retain=False)
            elif free == 1:
                self.publish(TOPIC_WARNING, {"message": "Only 1 free slot"})
            else:
                self.publish(TOPIC_INFO, {"message": f"Free slots: {free}"})

        elif msg.topic == TOPIC_BUTTON:
            if self.free_slots() > 0:
                self.publish(TOPIC_GATE_CMD, {"action": "OPEN"}, retain=False)
                threading.Timer(
                    3,
                    lambda: self.publish(
                        TOPIC_GATE_CMD,
                        {"action": "CLOSE"},
                        retain=False
                    )
                ).start()
            else:
                self.publish(
                    TOPIC_ALARM,
                    {"message": "Entry denied – parking full"}
                )

        elif msg.topic == TOPIC_GATE_STATUS:
            self.gate_state = data["state"]


if __name__ == "__main__":
    dm = DataManager()
    dm.connect()
    while True:
        time.sleep(1)
