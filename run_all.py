import subprocess
import sys
import time

# Helper to run a process in a new terminal window (Windows)
def run(cmd, title):
    subprocess.Popen(
        ['cmd', '/c', 'start', title] + cmd,
        shell=True
    )

if __name__ == "__main__":
    python = sys.executable

    print("Starting Smart Parking system...")

    # 1. Gate Relay
    run([python, "emulators/gate_relay.py"], "Gate Relay")
    time.sleep(1)

    # 2. Data Manager
    run([python, "data_manager/data_manager.py"], "Data Manager")
    time.sleep(1)

    # 3. Parking Slot Sensors
    for slot_id in range(1, 6):
        run(
            [python, "emulators/parking_slot_sensor.py", "--slot-id", str(slot_id)],
            f"Slot Sensor {slot_id}"
        )
        time.sleep(0.5)

    # 4. Entry Button
    run([python, "emulators/entry_button.py"], "Entry Button")
    time.sleep(1)

    # 5. GUI
    run([python, "gui/main_gui.py"], "Main GUI")

    print("All components started.")
