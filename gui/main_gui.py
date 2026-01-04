import sys
import json
import time
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QFrame
)
import paho.mqtt.client as mqtt


# ===== MQTT CONFIG =====
BROKER_HOST = "broker.hivemq.com"
BROKER_PORT = 8884

TOPIC_SLOT = "parking/slot/+/status"
TOPIC_GATE_STATUS = "parking/gate/relay"
TOPIC_INFO = "parking/system/info"
TOPIC_WARNING = "parking/system/warning"
TOPIC_ALARM = "parking/system/alarm"

TOTAL_SLOTS = 5


# ===== MQTT → GUI BRIDGE =====
class MqttBridge(QObject):
    slot_update = pyqtSignal(int, bool)
    gate_update = pyqtSignal(str)
    alert_update = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()

        self.client = mqtt.Client(
            client_id="smartparking-gui",
            transport="websockets"
        )
        self.client.tls_set()

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(BROKER_HOST, BROKER_PORT, 60)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            client.subscribe(TOPIC_SLOT)
            client.subscribe(TOPIC_GATE_STATUS)
            client.subscribe(TOPIC_INFO)
            client.subscribe(TOPIC_WARNING)
            client.subscribe(TOPIC_ALARM)

    def on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
        except Exception:
            return

        if msg.topic.startswith("parking/slot/"):
            self.slot_update.emit(
                int(data["slot_id"]),
                bool(data["occupied"])
            )

        elif msg.topic == TOPIC_GATE_STATUS:
            self.gate_update.emit(data.get("state", "UNKNOWN"))

        elif msg.topic == TOPIC_INFO:
            self.alert_update.emit("INFO", data.get("message", ""))

        elif msg.topic == TOPIC_WARNING:
            self.alert_update.emit("WARNING", data.get("message", ""))

        elif msg.topic == TOPIC_ALARM:
            self.alert_update.emit("ALARM", data.get("message", ""))


# ===== MAIN GUI =====
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Smart Parking – User View")
        self.resize(950, 550)

        self.slots = {i: False for i in range(1, TOTAL_SLOTS + 1)}
        self.gate_state = "CLOSED"

        # ===== STATUS BANNER =====
        self.status_label = QLabel("STATUS: OK")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            padding: 10px;
            background-color: lightgreen;
        """)

        # ===== HEADER =====
        self.header_label = QLabel()
        self.header_label.setAlignment(Qt.AlignCenter)
        self.header_label.setStyleSheet("font-size: 16px;")

        self.gate_label = QLabel("Gate: CLOSED")
        self.gate_label.setAlignment(Qt.AlignCenter)

        # ===== TABLE =====
        self.table = QTableWidget(TOTAL_SLOTS, 2)
        self.table.setHorizontalHeaderLabels(["Slot ID", "Occupied"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # ===== LOG =====
        self.log = QTextEdit()
        self.log.setReadOnly(True)

        # ===== LAYOUT =====
        top = QVBoxLayout()
        top.addWidget(self.status_label)
        top.addWidget(self.header_label)
        top.addWidget(self.gate_label)

        left = QVBoxLayout()
        left.addLayout(top)
        left.addWidget(self.table)

        main = QHBoxLayout()
        main.addLayout(left, 2)
        main.addWidget(self.log, 3)

        self.setLayout(main)

        self.update_header()
        self.update_table()

        # ===== MQTT =====
        self.bridge = MqttBridge()
        self.bridge.slot_update.connect(self.on_slot_update)
        self.bridge.gate_update.connect(self.on_gate_update)
        self.bridge.alert_update.connect(self.on_alert)

    def update_header(self):
        free = sum(1 for v in self.slots.values() if not v)
        occupied = TOTAL_SLOTS - free
        self.header_label.setText(
            f"Total: {TOTAL_SLOTS} | Occupied: {occupied} | Free: {free}"
        )
        self.gate_label.setText(f"Gate: {self.gate_state}")

    def update_table(self):
        for row, slot_id in enumerate(self.slots):
            self.table.setItem(row, 0, QTableWidgetItem(str(slot_id)))
            self.table.setItem(
                row, 1,
                QTableWidgetItem("YES" if self.slots[slot_id] else "NO")
            )

    def on_slot_update(self, slot_id, occupied):
        self.slots[slot_id] = occupied
        self.update_table()
        self.update_header()

    def on_gate_update(self, state):
        self.gate_state = state
        self.update_header()

    def on_alert(self, level, message):
        ts = time.strftime("%H:%M:%S")
        self.log.append(f"[{ts}] {level}: {message}")

        if level == "INFO":
            self.status_label.setText("STATUS: OK")
            self.status_label.setStyleSheet("""
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
                background-color: lightgreen;
            """)

        elif level == "WARNING":
            self.status_label.setText(f"STATUS: {message}")
            self.status_label.setStyleSheet("""
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
                background-color: khaki;
            """)

        elif level == "ALARM":
            self.status_label.setText(f"STATUS: {message}")
            self.status_label.setStyleSheet("""
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
                background-color: lightcoral;
            """)


# ===== APP ENTRY =====
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
