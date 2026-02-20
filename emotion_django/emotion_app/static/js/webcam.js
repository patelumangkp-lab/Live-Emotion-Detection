// Webcam Page JavaScript

let stream = null;
let video = null;
let canvas = null;
let ctx = null;
let isDetecting = false;
let detectionInterval = null;

// Get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

async function startWebcam() {
    try {
        video = document.getElementById('webcam');
        canvas = document.getElementById('overlay');
        ctx = canvas.getContext('2d');
        
        // Request webcam access
        stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                width: { ideal: 1280 },
                height: { ideal: 720 }
            } 
        });
        
        video.srcObject = stream;
        
        // Wait for video to load
        video.onloadedmetadata = () => {
            // Set canvas size to match video
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            
            // Hide placeholder
            document.getElementById('cameraPlaceholder').style.display = 'none';
            
            // Update UI
            document.getElementById('startBtn').style.display = 'none';
            document.getElementById('stopBtn').style.display = 'inline-flex';
            document.getElementById('captureBtn').style.display = 'inline-flex';
            
            // Update status
            document.getElementById('statusDot').classList.add('active');
            document.getElementById('statusText').textContent = 'Camera is active';
            
            // Start continuous detection
            isDetecting = true;
            startContinuousDetection();
        };
        
    } catch (error) {
        console.error('Error accessing webcam:', error);
        alert('Could not access webcam. Please ensure you have granted camera permissions.');
    }
}

function stopWebcam() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
    
    // Stop detection
    isDetecting = false;
    if (detectionInterval) {
        clearInterval(detectionInterval);
        detectionInterval = null;
    }
    
    // Clear canvas
    if (ctx) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
    
    // Update UI
    document.getElementById('startBtn').style.display = 'inline-flex';
    document.getElementById('stopBtn').style.display = 'none';
    document.getElementById('captureBtn').style.display = 'none';
    document.getElementById('cameraPlaceholder').style.display = 'flex';
    
    // Update status
    document.getElementById('statusDot').classList.remove('active');
    document.getElementById('statusText').textContent = 'Camera is off';
    
    // Clear results
    document.getElementById('liveEmotionResults').innerHTML = `
        <div class="empty-state">
            <i class="fas fa-eye-slash"></i>
            <p>Start the camera to see live results</p>
        </div>
    `;
    document.getElementById('liveCount').textContent = '0';
    document.getElementById('dominantEmotion').textContent = '-';
}

function startContinuousDetection() {
    // Detect every 1 second
    detectionInterval = setInterval(() => {
        if (isDetecting) {
            captureFrame();
        }
    }, 1000);
}

async function captureFrame() {
    if (!video || !canvas) return;
    
    // Create temporary canvas to capture frame
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = video.videoWidth;
    tempCanvas.height = video.videoHeight;
    const tempCtx = tempCanvas.getContext('2d');
    
    // Draw current video frame
    tempCtx.drawImage(video, 0, 0);
    
    // Convert to base64
    const imageData = tempCanvas.toDataURL('image/jpeg', 0.8);
    
    // Send to server
    try {
        const response = await fetch('/api/detect-webcam/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ image: imageData })
        });
        
        const data = await response.json();
        
        if (data.success) {
            drawResults(data.results);
            displayLiveResults(data.results);
        }
    } catch (error) {
        console.error('Detection error:', error);
    }
}

function drawResults(results) {
    // Clear previous drawings
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw boxes and labels
    results.forEach(result => {
        const box = result.box;
        
        // Draw rectangle
        ctx.strokeStyle = '#00ff00';
        ctx.lineWidth = 3;
        ctx.strokeRect(box.x, box.y, box.width, box.height);
        
        // Draw label background
        const label = `${result.emotion} ${(result.confidence * 100).toFixed(0)}%`;
        ctx.font = 'bold 16px Arial';
        const textWidth = ctx.measureText(label).width;
        
        ctx.fillStyle = 'rgba(0, 255, 0, 0.8)';
        ctx.fillRect(box.x, box.y - 30, textWidth + 10, 25);
        
        // Draw label text
        ctx.fillStyle = '#000';
        ctx.fillText(label, box.x + 5, box.y - 10);
    });
}

function displayLiveResults(results) {
    // Update face count
    document.getElementById('liveCount').textContent = results.length;
    
    const resultsContainer = document.getElementById('liveEmotionResults');
    
    if (results.length === 0) {
        resultsContainer.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-user-slash"></i>
                <p>No faces detected</p>
            </div>
        `;
        document.getElementById('dominantEmotion').textContent = '-';
        return;
    }
    
    // Get dominant emotion (highest confidence)
    let dominantEmotion = results[0].emotion;
    let maxConfidence = results[0].confidence;
    
    results.forEach(result => {
        if (result.confidence > maxConfidence) {
            maxConfidence = result.confidence;
            dominantEmotion = result.emotion;
        }
    });
    
    document.getElementById('dominantEmotion').textContent = dominantEmotion;
    
    // Display all faces
    resultsContainer.innerHTML = '';
    
    results.forEach((result, index) => {
        const emotionDiv = document.createElement('div');
        emotionDiv.className = 'emotion-result';
        
        const emotionClass = result.emotion.toLowerCase();
        const emotionIcon = getEmotionIcon(result.emotion);
        
        let allPredictionsHTML = '';
        // Sort predictions by value
        const sortedPredictions = Object.entries(result.all_predictions)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 3); // Show top 3
        
        sortedPredictions.forEach(([emotion, prob]) => {
            const percentage = (prob * 100).toFixed(1);
            const emotionLower = emotion.toLowerCase();
            allPredictionsHTML += `
                <div class="emotion-bar">
                    <div class="emotion-bar-inner ${emotionLower}" style="width: ${percentage}%">
                        <span>${emotion}</span>
                        <span>${percentage}%</span>
                    </div>
                </div>
            `;
        });
        
        emotionDiv.innerHTML = `
            <h3>
                <i class="fas ${emotionIcon}"></i>
                Face ${index + 1}: ${result.emotion}
            </h3>
            <div style="margin-top: 0.8rem;">
                ${allPredictionsHTML}
            </div>
        `;
        
        resultsContainer.appendChild(emotionDiv);
    });
}

function getEmotionIcon(emotion) {
    const icons = {
        'Angry': 'fa-angry',
        'Disgust': 'fa-grimace',
        'Fear': 'fa-flushed',
        'Happy': 'fa-smile',
        'Sad': 'fa-sad-tear',
        'Surprise': 'fa-surprise',
        'Neutral': 'fa-meh'
    };
    return icons[emotion] || 'fa-meh';
}

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    stopWebcam();
});
