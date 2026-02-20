# Live Emotion Detection (FER-2013 + CNN)

This repository contains scripts to train a Convolutional Neural Network (CNN) on the FER-2013 dataset and run real-time emotion detection using your webcam.

Files added:

- `train_emotion_model.py` - Loads FER-2013, preprocesses, builds a CNN, trains, evaluates, and saves `emotion_model.h5`.
- `live_emotion_detection.py` - Loads a saved Keras model and performs real-time detection using OpenCV and Haar cascades.
- `utils.py` - Helper functions for preprocessing and plotting.
- `requirements.txt` - Python dependencies.

Quick start (local):

1. Create a virtual environment and install dependencies:

    python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt

2. Train the model (this will download FER-2013 via `tensorflow_datasets`):

    python train_emotion_model.py

   The best model by validation accuracy will be saved to `emotion_model.h5`. Training plots are saved as `training_history.png` and `confusion_matrix.png`.

3. Run live detection (ensure webcam is available):

    python live_emotion_detection.py --model emotion_model.h5

Notes for Google Colab:

- Upload this repo files to Colab or mount Google Drive.
- Install dependencies (use pip) and run `train_emotion_model.py`. Colab provides a GPU which speeds up training.

Haar cascade:

The script uses OpenCV's bundled `haarcascade_frontalface_default.xml` which is included with OpenCV. If you need a copy, download it from OpenCV's GitHub and place it in the working directory.

Model loading/saving:

- The training script saves the best model to `emotion_model.h5` using Keras ModelCheckpoint.
- You can load it later with `tf.keras.models.load_model('emotion_model.h5')`.

License: MIT
