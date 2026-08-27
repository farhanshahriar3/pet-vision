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
