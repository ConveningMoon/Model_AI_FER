import cv2
import mediapipe as mp
import time
import datetime
import json
from utils import get_face_landmarks
import pickle
from collections import Counter

# Load the emotion recognition model
with open('./model', 'rb') as f:
    model = pickle.load(f)

emotions = ['ANGRY', 'CONFUSED', 'FEAR', 'HAPPY', 'SAD', 'SURPRISED']

cap = cv2.VideoCapture(0)

emotion_data = []
start_time = time.time()

while True:
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

    # Store emotion data in a JSON file every 5 seconds
    if time.time() - start_time >= 5:
        most_common_emotions = Counter(emotion_data).most_common(3)
        emotion_summary = [{"emotion": e[0], "percentage": e[1] / len(emotion_data) * 100} for e in
                           most_common_emotions]

        json_data = {
            "datetime": datetime.datetime.now().isoformat(),
            "emotions": emotion_summary
        }

        with open('emotion_data.json', 'a') as file:
            json.dump(json_data, file, indent=4)
            file.write(",\n")  # Separate entries by a comma and new line for readability

        # Reset for the next interval
        emotion_data = []
        start_time = time.time()

    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
