# Emotion Detection Django Web Application

A modern, AI-powered emotion detection web application built with Django and TensorFlow. Features real-time webcam detection and image upload capabilities with a beautiful, unique UI.

## Features

- 🎯 **Real-time Emotion Detection** - Live webcam feed with instant emotion recognition
- 📸 **Image Upload** - Upload images for emotion analysis
- 🧠 **7 Emotions** - Detects Angry, Disgust, Fear, Happy, Sad, Surprise, and Neutral
- 🎨 **Modern UI** - Glassmorphism design with animated gradients
- 📊 **Detailed Results** - Shows confidence scores for all emotions
- 🚀 **High Performance** - Fast inference using TensorFlow

## Technology Stack

- **Backend**: Django 4.2
- **ML Framework**: TensorFlow 2.x
- **Computer Vision**: OpenCV
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLite (default)

## Prerequisites

- Python 3.8 or higher
- Webcam (for live detection feature)
- The trained emotion detection model: `emotion_model_final.h5`

## Installation

1. **Navigate to the Django project directory**:
   ```bash
   cd emotion_django
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On Linux/Mac
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser** (optional, for admin access):
   ```bash
   python manage.py createsuperuser
   ```

## Running the Application

1. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

2. **Open your browser** and navigate to:
   ```
   http://127.0.0.1:8000/
   ```

## Project Structure

```
emotion_django/
├── manage.py
├── requirements.txt
├── emotion_project/          # Django project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── emotion_app/              # Main application
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py              # View functions
│   ├── urls.py               # URL routing
│   ├── emotion_utils.py      # ML utilities
│   ├── templates/            # HTML templates
│   │   ├── index.html
│   │   ├── upload.html
│   │   ├── webcam.html
│   │   └── about.html
│   └── static/               # Static files
│       ├── css/
│       │   └── style.css
│       └── js/
│           ├── main.js
│           ├── upload.js
│           └── webcam.js
└── media/                    # User uploads
    └── uploads/
```

## Usage

### Home Page
- Overview of the emotion detection system
- Quick access to all features

### Upload Image
1. Click "Upload" in the navigation
2. Drag & drop or select an image
3. Click "Analyze Emotion"
4. View detected faces and their emotions

### Live Detection
1. Click "Live Detection" in the navigation
2. Click "Start Camera" and allow camera access
3. The system will automatically detect emotions in real-time
4. View live results on the right panel

### About Page
- Information about the technology
- Details about detected emotions
- Technology stack overview

## API Endpoints

- `POST /api/detect/` - Upload image for emotion detection
- `POST /api/detect-webcam/` - Send webcam frame for detection

## Model Configuration

The model path is configured in `emotion_project/settings.py`:

```python
EMOTION_MODEL_PATH = os.path.join(BASE_DIR.parent, 'emotion_model_final.h5')
```

Make sure the `emotion_model_final.h5` file exists in the parent directory of the Django project.

## Troubleshooting

### Model not found
- Ensure `emotion_model_final.h5` is in the correct location
- Check the `EMOTION_MODEL_PATH` in settings.py

### Camera not working
- Allow camera permissions in your browser
- Ensure no other application is using the camera
- Use HTTPS in production (required for camera access)

### Import errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify Python version is 3.8 or higher

## Production Deployment

For production deployment:

1. Set `DEBUG = False` in settings.py
2. Configure `ALLOWED_HOSTS`
3. Use a production database (PostgreSQL recommended)
4. Collect static files: `python manage.py collectstatic`
5. Use a production server like Gunicorn with Nginx

## License

This project is for educational purposes.

## Credits

- TensorFlow for the deep learning framework
- OpenCV for computer vision capabilities
- Django for the web framework
- Font Awesome for icons
