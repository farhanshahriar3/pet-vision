# 🐾 Pet Vision

A computer vision project for detecting **dogs and cats** using YOLO and OpenCV.

The system supports image, video, and webcam input and uses a strict dog/cat allow-list before generating a software-only virtual trigger event.

> **Safety:** The current project uses a software-only virtual trigger for development and testing. Keep any physical launcher or projectile mechanism disconnected during testing. Do not use an automated system to target or fire at animals or people.

---

## ✨ Features

- 🐕 Dog detection
- 🐈 Cat detection
- 🤖 YOLO object detection
- 🎯 Strict dog/cat filtering
- 📊 Confidence filtering
- ⏱️ Detection confirmation
- 🔄 Trigger cooldown
- 🖼️ Image input
- 🎥 Video input
- 📷 Webcam input
- 🖥️ Web dashboard
- 📈 Detection metrics
- 🧪 Software-only virtual trigger
- 📝 Logging
- ⚙️ YAML configuration

---

# 🧠 How It Works

The vision pipeline works like this:

```text
Camera / Image / Video
        |
        v
       YOLO
        |
        v
 Object Detection
        |
        v
Is it a dog or cat?
     /       \
   YES        NO
    |          |
    v          v
Confidence    IGNORE
   Check
    |
    v
Confirmation
    |
    v
Cooldown
    |
    v
Virtual Trigger Event 

📁 Project Structure

pet_vision/
│
├── app/
│   ├── __init__.py
│   ├── camera.py
│   ├── config.py
│   ├── detector.py
│   ├── logger.py
│   ├── metrics.py
│   ├── state.py
│   ├── trigger.py
│   └── video_source.py
│
├── web/
│   ├── __init__.py
│   ├── server.py
│   ├── templates/
│   │   └── index.html
│   └── static/
│       ├── app.js
│       └── style.css
│
├── tests/
│   ├── test_config.py
│   ├── test_detector.py
│   ├── test_state.py
│   └── test_trigger.py
│
├── models/
├── logs/
│
├── run.py
├── config.yaml
├── requirements.txt
├── README.md
└── .gitignore 

🚀 Installation
1. Clone the repository
-- git clone https://github.com/farhanshahriar3/pet-vision.git
Enter the project directory:
cd pet-vision

Create a virtual environment
python -m venv .venv

Activate the virtual environment
.venv\Scripts\Activate.ps1
If PowerShell reports:
---running scripts is disabled on this system
run: 
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

Then activate again:
.venv\Scripts\Activate.ps1

Install dependencies
pip install -r requirements.txt



**📊 Metrics**
The application can track:

Frames processed
FPS
Total detections
Dog detections
Cat detections
Virtual trigger count
Last trigger event



