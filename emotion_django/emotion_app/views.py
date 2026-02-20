from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import cv2
import numpy as np
import base64
import json
from .emotion_utils import detect_emotion_in_image, predict_single_emotion


def index(request):
    """Home page with emotion detection interface."""
    return render(request, 'index.html')


def upload_page(request):
    """Image upload page."""
    return render(request, 'upload.html')


def webcam_page(request):
    """Live webcam detection page."""
    return render(request, 'webcam.html')


@csrf_exempt
def detect_emotion(request):
    """API endpoint to detect emotion from uploaded image."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'}, status=400)
    
    try:
        # Check if image file is uploaded
        if 'image' in request.FILES:
            image_file = request.FILES['image']
            
            # Read image file
            image_data = image_file.read()
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
        # Check if base64 image is sent
        elif 'image_data' in request.POST:
            image_data = request.POST['image_data']
            
            # Remove data URL prefix if present
            if 'base64,' in image_data:
                image_data = image_data.split('base64,')[1]
            
            # Decode base64
            image_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
        else:
            return JsonResponse({'error': 'No image provided'}, status=400)
        
        if image is None:
            return JsonResponse({'error': 'Invalid image data'}, status=400)
        
        # Detect emotions
        results = detect_emotion_in_image(image)
        
        # Draw boxes on image for visualization
        output_image = image.copy()
        for result in results:
            box = result['box']
            x, y, w, h = box['x'], box['y'], box['width'], box['height']
            
            # Draw rectangle
            cv2.rectangle(output_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Draw label
            label = f"{result['emotion']} ({result['confidence']*100:.1f}%)"
            cv2.putText(output_image, label, (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Encode result image to base64
        _, buffer = cv2.imencode('.jpg', output_image)
        result_image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return JsonResponse({
            'success': True,
            'faces_detected': len(results),
            'results': results,
            'result_image': f'data:image/jpeg;base64,{result_image_base64}'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def detect_emotion_webcam(request):
    """API endpoint for webcam frame emotion detection."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'}, status=400)
    
    try:
        data = json.loads(request.body)
        image_data = data.get('image')
        
        if not image_data:
            return JsonResponse({'error': 'No image data provided'}, status=400)
        
        # Remove data URL prefix
        if 'base64,' in image_data:
            image_data = image_data.split('base64,')[1]
        
        # Decode base64
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return JsonResponse({'error': 'Invalid image data'}, status=400)
        
        # Detect emotions
        results = detect_emotion_in_image(image)
        
        return JsonResponse({
            'success': True,
            'faces_detected': len(results),
            'results': results
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def about_page(request):
    """About page with information about the emotion detection system."""
    return render(request, 'about.html')
