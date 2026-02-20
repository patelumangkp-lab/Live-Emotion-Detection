# Quick Start Guide for Emotion Detection Django App

## Step 1: Navigate to the Django project
cd "d:\BIA\Sem - 3\capstone\aaa\aaa\emotion_django"

## Step 2: Create virtual environment (recommended)
python -m venv venv
.\venv\Scripts\activate

## Step 3: Install dependencies
pip install -r requirements.txt

## Step 4: Run migrations
python manage.py migrate

## Step 5: Start the server
python manage.py runserver

## Step 6: Open in browser
# Navigate to: http://127.0.0.1:8000/

## Troubleshooting

# If you get "Module not found" errors:
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall

# If the model is not found:
# Make sure emotion_model_final.h5 is in the parent directory
# Path should be: d:\BIA\Sem - 3\capstone\aaa\aaa\emotion_model_final.h5

# If camera doesn't work:
# Allow camera permissions in your browser
# Make sure no other app is using the camera

## Features to Try

1. Home Page - Overview and quick navigation
2. Upload Page - Upload an image to detect emotions
3. Webcam Page - Real-time emotion detection
4. About Page - Learn about the technology

Enjoy your emotion detection app! 🎉
