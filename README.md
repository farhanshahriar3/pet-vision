# Pet Vision

A local real-time computer-vision system for detecting dogs and cats through a webcam.

The project uses:

- Python
- OpenCV
- Ultralytics YOLO
- FastAPI
- JavaScript
- HTML/CSS

## Architecture

Webcam
   ↓
OpenCV
   ↓
YOLO
   ↓
Dog/Cat Filtering
   ↓
Confidence Filtering
   ↓
Temporal Confirmation
   ↓
State Machine
   ↓
Virtual Trigger
   ↓
Dashboard / Event Log

## Safety

This project contains only a software virtual trigger.

It does NOT contain:

- GPIO control
- motor control
- solenoid control
- projectile-launching control
- water-pump control
- physical firing logic

The virtual trigger exists so the computer-vision pipeline can be tested independently.

---

# Installation

## 1. Install Python

Use Python 3.11 or newer.

Check:

python --version

---

# 2. Create virtual environment

Windows:

python -m venv .venv

Activate:

.venv\Scripts\activate

Linux/macOS:

python3 -m venv .venv

source .venv/bin/activate

---

# 3. Install dependencies

pip install -r requirements.txt

---

# 4. Start the application

python run.py

The first startup may download the YOLO model.

After startup open:

http://127.0.0.1:8000

---

# Command line options

Default:

python run.py

Different camera:

python run.py --camera 1

Debug:

python run.py --debug

Software test:

python run.py --test

Disable web dashboard:

python run.py --no-web

Custom configuration:

python run.py --config config.yaml

---

# Camera

The default camera is:

index: 0

If the webcam is not detected, try:

python run.py --camera 1

or:

python run.py --camera 2

---

# Configuration

Edit config.yaml.

Example:

detection:
  confidence_threshold: 0.60

A higher value means fewer but more confident detections.

Example:

trigger:
  confirmation_time: 0.75
  cooldown: 5.0

The animal must remain detected for approximately 0.75 seconds before a virtual trigger is generated.

After a trigger, the system waits 5 seconds before another trigger.

---

# Dashboard

The dashboard displays:

- live webcam
- dog detections
- cat detections
- confidence
- FPS
- system state
- confirmation progress
- cooldown
- detection statistics
- virtual trigger count
- last trigger

---

# State Machine

The system uses:

IDLE

No animal detected.

↓

DETECTED

An animal has appeared.

↓

CONFIRMING

The animal remains visible long enough to confirm the detection.

↓

TRIGGERED

A virtual trigger event is created.

↓

COOLDOWN

The system waits before another event can occur.

↓

IDLE

---

# Testing

Run:

pytest

---

# Test the virtual trigger

Run:

python run.py --test

This does not activate any physical mechanism.

It only tests the software trigger.

---

# Performance

For better CPU performance reduce:

model:
  inference_size: 640

to:

model:
  inference_size: 512

or:

model:
  inference_size: 416

Lower values generally increase speed at the cost of some detection accuracy.

---

# GPU

The project defaults to CPU for maximum compatibility.

If you have a properly configured CUDA environment, you can change:

device: "auto"

to an appropriate device supported by your Ultralytics installation.

---

# Privacy

The dashboard is bound to:

127.0.0.1

The camera feed is not intentionally exposed to the public internet.

No cloud upload is implemented.

---

# Troubleshooting

## Camera does not open

Try:

python run.py --camera 1

or:

python run.py --camera 2

Make sure another application is not currently using the webcam.

## Model does not load

Make sure the internet connection is available during the initial model download.

Then try:

pip install --upgrade ultralytics

## Low FPS

Reduce camera resolution in config.yaml.

For example:

camera:
  width: 640
  height: 480

Reduce inference size:

model:
  inference_size: 416

## Too many false detections

Increase:

detection:
  confidence_threshold: 0.70

## Detection is too slow to trigger

Decrease:

trigger:
  confirmation_time: 0.5

Only do this after confirming that the detector itself is stable.

---

# Development philosophy

The vision system and physical mechanism should remain separate.

The computer-vision system generates a software event:

VIRTUAL_TRIGGER

A separate harmless physical experiment can consume an abstract event later, without putting animal targeting or physical firing logic into the vision software.
