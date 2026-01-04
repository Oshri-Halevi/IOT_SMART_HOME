# Smart Parking IoT Project

This project implements a Smart Parking system using Python and MQTT.
The system simulates multiple IoT devices (parking sensors, entry button and gate relay),
a central Data Manager, and a Main GUI application.

All components communicate via the HiveMQ public MQTT broker using
MQTT over WebSockets Secure (WSS).

---

## System Overview

The system is composed of independent components, each running as a separate process,
simulating a real IoT-based smart parking environment.

**Architecture flow:**

Parking Sensors → MQTT Broker (HiveMQ) → Data Manager → GUI / Gate Relay

---

## System Components

### 1. Parking Slot Sensors (Emulators)
- Simulate parking slot occupancy (occupied / free)
- Each parking slot runs as a separate process
- Publish slot status updates via MQTT

### 2. Entry Button Emulator
- Simulates a vehicle entry request
- Sends an MQTT message when the button is pressed

### 3. Gate Relay Emulator
- Simulates the parking gate (OPEN / CLOSED)
- Receives commands from the Data Manager
- Publishes gate state updates

### 4. Data Manager
- Central logic component
- Subscribes to all MQTT topics
- Collects and processes parking data
- Stores data in a local SQLite database
- Generates INFO / WARNING / ALARM messages
- Controls the gate based on parking availability

### 5. Main GUI Application
- Displays live parking slot status
- Shows number of free and occupied slots
- Displays gate state
- Shows system alerts (INFO / WARNING / ALARM)
- Includes a dedicated alert status area for the user

---

## Database

- Local SQLite database (`parking.db`)
- Created automatically on first run
- Stores parking slot states and system alerts

---

## MQTT Configuration

- Broker: `broker.hivemq.com`
- Port: `8884`
- Protocol: MQTT over WebSockets Secure (WSS)
- Authentication: Not required (public broker)

---

## Installation

1. Install Python 3.9 or higher
2. Clone the repository
3. (Recommended) Create and activate a virtual environment
4. Install dependencies:

```bash
pip install -r requirements.txt
