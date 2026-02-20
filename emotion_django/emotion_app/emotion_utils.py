"""Utility functions for emotion detection in Django app."""
import cv2
import numpy as np
import tensorflow as tf
from django.conf import settings
import os

EMOTION_LABELS = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

# Global model variable
_model = None


def get_model():
    """Load and cache the emotion detection model."""
    global _model
    if _model is None:
        model_path = settings.EMOTION_MODEL_PATH
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}")
        _model = tf.keras.models.load_model(model_path)
        print(f"Loaded emotion model from {model_path}")
    return _model


def preprocess_image(image):
    """Ensure image is float32 normalized to [0,1] and resized to (48,48).
    
    Args:
        image: numpy array (grayscale or RGB)
        
    Returns:
        Preprocessed image array with shape (48, 48, 1)
    """
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        if image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        elif image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
    
    # Resize to 48x48
    image = cv2.resize(image, (48, 48))
    
    # Normalize
    image = image.astype('float32') / 255.0
    
    # Add channel dimension
    image = np.expand_dims(image, -1)
    
    return image


def load_face_detector():
    """Load Haar Cascade face detector."""
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    if not os.path.exists(cascade_path):
        raise FileNotFoundError('Haar cascade XML not found in OpenCV data')
    face_cascade = cv2.CascadeClassifier(cascade_path)
    return face_cascade


def detect_emotion_in_image(image_array):
    """Detect emotions in an image.
    
    Args:
        image_array: numpy array of the image
        
    Returns:
        List of dictionaries containing face locations and emotion predictions
    """
    model = get_model()
    face_cascade = load_face_detector()
    
    # Convert to grayscale for face detection
    if len(image_array.shape) == 3:
        gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
    else:
        gray = image_array
    
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
    
    results = []
    for (x, y, w, h) in faces:
        # Extract face region
        face_img = image_array[y:y+h, x:x+w]
        
        # Preprocess
        processed = preprocess_image(face_img)
        processed = np.expand_dims(processed, 0)  # Add batch dimension
        
        # Predict
        predictions = model.predict(processed, verbose=0)
        emotion_idx = int(np.argmax(predictions))
        confidence = float(np.max(predictions))
        
        results.append({
            'box': {'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)},
            'emotion': EMOTION_LABELS[emotion_idx],
            'confidence': confidence,
            'all_predictions': {
                label: float(predictions[0][i]) 
                for i, label in enumerate(EMOTION_LABELS)
            }
        })
    
    return results


def predict_single_emotion(image_array):
    """Predict emotion for a single preprocessed face image.
    
    Args:
        image_array: numpy array of face image
        
    Returns:
        Dictionary with emotion and confidence
    """
    model = get_model()
    
    # Preprocess
    processed = preprocess_image(image_array)
    processed = np.expand_dims(processed, 0)
    
    # Predict
    predictions = model.predict(processed, verbose=0)
    emotion_idx = int(np.argmax(predictions))
    confidence = float(np.max(predictions))
    
    return {
        'emotion': EMOTION_LABELS[emotion_idx],
        'confidence': confidence,
        'all_predictions': {
            label: float(predictions[0][i]) 
            for i, label in enumerate(EMOTION_LABELS)
        }
    }
