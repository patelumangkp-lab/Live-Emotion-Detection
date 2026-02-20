// Upload Page JavaScript

let selectedFile = null;

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

// File input change handler
document.getElementById('fileInput').addEventListener('change', handleFileSelect);

// Drag and drop handlers
const uploadArea = document.getElementById('uploadArea');

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#667eea';
    uploadArea.style.background = 'rgba(102, 126, 234, 0.1)';
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.style.borderColor = '';
    uploadArea.style.background = '';
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '';
    uploadArea.style.background = '';
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

function handleFile(file) {
    if (!file.type.startsWith('image/')) {
        alert('Please select an image file');
        return;
    }
    
    selectedFile = file;
    
    // Preview image
    const reader = new FileReader();
    reader.onload = (e) => {
        document.getElementById('previewImage').src = e.target.result;
        document.getElementById('uploadArea').style.display = 'none';
        document.getElementById('previewArea').style.display = 'block';
        document.getElementById('analyzeBtn').style.display = 'block';
    };
    reader.readAsDataURL(file);
}

function resetUpload() {
    selectedFile = null;
    document.getElementById('fileInput').value = '';
    document.getElementById('uploadArea').style.display = 'block';
    document.getElementById('previewArea').style.display = 'none';
    document.getElementById('analyzeBtn').style.display = 'none';
    document.getElementById('resultsCard').style.display = 'none';
    document.getElementById('loadingSpinner').style.display = 'none';
}

async function analyzeImage() {
    if (!selectedFile) {
        alert('Please select an image first');
        return;
    }
    
    // Show loading
    document.getElementById('loadingSpinner').style.display = 'block';
    document.getElementById('analyzeBtn').style.display = 'none';
    document.getElementById('resultsCard').style.display = 'none';
    
    const formData = new FormData();
    formData.append('image', selectedFile);
    
    try {
        const response = await fetch('/api/detect/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResults(data);
        } else {
            alert('Error: ' + (data.error || 'Unknown error occurred'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to analyze image. Please try again.');
    } finally {
        document.getElementById('loadingSpinner').style.display = 'none';
    }
}

function displayResults(data) {
    // Show results card
    document.getElementById('resultsCard').style.display = 'block';
    
    // Set faces count
    document.getElementById('facesCount').textContent = data.faces_detected;
    
    // Display result image
    document.getElementById('resultImage').src = data.result_image;
    
    // Display emotion results
    const resultsContainer = document.getElementById('emotionResults');
    resultsContainer.innerHTML = '';
    
    if (data.faces_detected === 0) {
        resultsContainer.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-user-slash"></i>
                <p>No faces detected in the image</p>
            </div>
        `;
        return;
    }
    
    data.results.forEach((result, index) => {
        const emotionDiv = document.createElement('div');
        emotionDiv.className = 'emotion-result';
        
        const emotionClass = result.emotion.toLowerCase();
        const emotionIcon = getEmotionIcon(result.emotion);
        
        let allPredictionsHTML = '';
        for (const [emotion, prob] of Object.entries(result.all_predictions)) {
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
        }
        
        emotionDiv.innerHTML = `
            <h3>
                <i class="fas ${emotionIcon}"></i>
                Face ${index + 1}: ${result.emotion}
                <span style="font-size: 0.9rem; color: var(--text-secondary);">
                    (${(result.confidence * 100).toFixed(1)}% confident)
                </span>
            </h3>
            <div style="margin-top: 1rem;">
                <h4 style="margin-bottom: 0.5rem; font-size: 0.9rem; color: var(--text-secondary);">
                    All Predictions:
                </h4>
                ${allPredictionsHTML}
            </div>
        `;
        
        resultsContainer.appendChild(emotionDiv);
    });
    
    // Scroll to results
    document.getElementById('resultsCard').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
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
