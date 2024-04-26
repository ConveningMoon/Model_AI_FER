# pip install mediapipe
# pip install -U scikit-learn

import cv2
import mediapipe as mp
import time
import datetime
import json
from utils import get_face_landmarks
import pickle
from collections import Counter
from threading import Thread
from firebase_admin import db

running = False
emotion_data = []
subject = ""


def camera_loop():
    global running, emotion_data
    # Load the emotion recognition model
    with open('./model', 'rb') as f:
        model = pickle.load(f)

    emotions = ['ANGRY', 'CONFUSED', 'FEAR', 'HAPPY', 'SAD', 'SURPRISED']

    cap = cv2.VideoCapture(0)

    emotion_data = []

    running = True
    while running:
        ret, frame = cap.read()

        if not ret:
            break

        face_landmarks = get_face_landmarks(frame, draw=True, static_image_mode=False)

        if face_landmarks:  # If face_landmarks is not empty
            output = model.predict([face_landmarks])
            emotion_data.append(emotions[int(output[0])])
            cv2.putText(frame,
                        emotions[int(output[0])],
                        (10, frame.shape[0] - 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2)

        cv2.imshow('frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("trigger break")
            break

    cap.release()
    cv2.destroyAllWindows()


def open_camera(subject_name):
    global subject
    subject = subject_name
    # Start camera in a separate thread
    Thread(target=camera_loop).start()


def close_camera():
    global running
    running = False

    time.sleep(1)  # Give a moment for the camera loop to notice the flag


def send_info(localId, refReport, averageInfo):
    global emotion_data, subject

    most_common_emotions = list(Counter(emotion_data).items())
    emotion_summary = [{"emotion": e[0], "percentage": e[1] / len(emotion_data) * 100} for e in
                       most_common_emotions]

    json_report = {
        "studentId": localId,
        "datetime": datetime.datetime.now().isoformat(),
        "emotions": emotion_summary,
        "subject": subject,
        "average": averageInfo
    }
    refReport.push(json_report)

    # Reset for the next interval
    emotion_data = []