# Smart Control, Powered by Computer Vision

A real-time, contactless hand gesture–based system for controlling mouse, keyboard, and media functions using a standard webcam.

## Architecture
Webcam → OpenCV → MediaPipe → Gesture Recognition → Action Mapping → System Control

## Supported Gestures
- Index Finger: Mouse movement
- Fist: Play / Pause
- Two Fingers: Volume control
- Open Palm: Idle

## Setup
```bash
pip install -r requirements.txt
python main.py
