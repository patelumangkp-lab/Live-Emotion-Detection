"""Run live emotion detection using webcam, OpenCV for face detection, and a saved Keras model.

Usage:
    python live_emotion_detection.py --model emotion_model.h5

Requires `haarcascade_frontalface_default.xml` available in the working directory or OpenCV data.
"""
import argparse
import cv2
import numpy as np
import tensorflow as tf
from utils import preprocess_image

EMOTION_LABELS = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']


def load_face_detector():
    # Try common locations for the Haar cascade bundled with OpenCV
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    if not cv2.os.path.exists(cascade_path):
        raise FileNotFoundError('Haar cascade XML not found in OpenCV data. Please provide haarcascade_frontalface_default.xml')
    face_cascade = cv2.CascadeClassifier(cascade_path)
    return face_cascade


def predict_on_frame(model, face_img):
    # face_img: BGR or grayscale image cropped to the face region
    gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY) if face_img.ndim == 3 else face_img
    # resize to 48x48
    gray = cv2.resize(gray, (48, 48))
    proc = preprocess_image(gray)
    proc = np.expand_dims(proc, 0)  # batch
    preds = model.predict(proc)
    idx = int(np.argmax(preds))
    prob = float(np.max(preds))
    return EMOTION_LABELS[idx], prob


def main(model_path):
    print('Loading model:', model_path)
    model = tf.keras.models.load_model(model_path)

    face_cascade = load_face_detector()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print('ERROR: Could not open webcam.')
        return

    print('Press q to quit.')
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        for (x, y, w, h) in faces:
            face_img = frame[y:y+h, x:x+w]
            try:
                label, prob = predict_on_frame(model, face_img)
            except Exception:
                label, prob = 'Error', 0.0

            # draw rectangle and label
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            text = f'{label} ({prob*100:.1f}%)'
            cv2.putText(frame, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        cv2.imshow('Emotion Detection', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default='emotion_model.h5', help='Path to trained Keras .h5 model')
    args = parser.parse_args()
    main(args.model)
