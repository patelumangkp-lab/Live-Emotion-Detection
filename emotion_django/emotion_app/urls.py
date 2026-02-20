from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_page, name='upload'),
    path('webcam/', views.webcam_page, name='webcam'),
    path('about/', views.about_page, name='about'),
    path('api/detect/', views.detect_emotion, name='detect_emotion'),
    path('api/detect-webcam/', views.detect_emotion_webcam, name='detect_emotion_webcam'),
]
