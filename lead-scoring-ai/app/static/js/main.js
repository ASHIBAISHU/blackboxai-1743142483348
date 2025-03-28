// Voice Feedback System
const voiceModal = document.getElementById('voiceModal');
const startRecordingBtn = document.getElementById('startRecording');
const playRecordingBtn = document.getElementById('playRecording');
const voiceStatus = document.getElementById('voiceStatus');
const cancelVoiceBtn = document.getElementById('cancelVoice');
const submitVoiceBtn = document.getElementById('submitVoice');

let mediaRecorder;
let audioChunks = [];
let audioBlob;

// Initialize voice feedback buttons
if (startRecordingBtn) {
    startRecordingBtn.addEventListener('click', startRecording);
    playRecordingBtn.addEventListener('click', playRecording);
    cancelVoiceBtn.addEventListener('click', cancelRecording);
    submitVoiceBtn.addEventListener('click', submitRecording);
}

function startRecording() {
    if (!navigator.mediaDevices || !window.MediaRecorder) {
        showNotification('Voice recording not supported in this browser', 'error');
        return;
    }

    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            
            mediaRecorder.ondataavailable = e => {
                if (e.data.size > 0) audioChunks.push(e.data);
            };
            
            mediaRecorder.onstop = () => {
                audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                playRecordingBtn.disabled = false;
                voiceStatus.textContent = 'Recording complete. Click play to review.';
            };
            
            mediaRecorder.start();
            startRecordingBtn.textContent = 'Stop Recording';
            voiceStatus.textContent = 'Recording... Click stop when finished.';
            
            // Change button to stop recording
            startRecordingBtn.onclick = stopRecording;
        })
        .catch(err => {
            console.error('Error accessing microphone:', err);
            showNotification('Microphone access denied', 'error');
        });
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
        startRecordingBtn.textContent = 'Start Recording';
        startRecordingBtn.onclick = startRecording;
    }
}

function playRecording() {
    if (!audioBlob) return;
    
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);
    audio.play();
}

function cancelRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
    }
    voiceModal.classList.add('hidden');
    audioBlob = null;
    playRecordingBtn.disabled = true;
}

async function submitRecording() {
    if (!audioBlob) {
        showNotification('Please record feedback first', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('audio', audioBlob, 'feedback.wav');
    formData.append('prediction_id', document.querySelector('select[name="prediction_id"]').value);

    try {
        const response = await fetch('/api/feedback/voice', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: formData
        });

        if (response.ok) {
            showNotification('Voice feedback submitted successfully');
            voiceModal.classList.add('hidden');
            if (window.loadRecentPredictions) loadRecentPredictions();
        } else {
            throw new Error(await response.text());
        }
    } catch (error) {
        console.error('Error submitting voice feedback:', error);
        showNotification('Failed to submit voice feedback', 'error');
    }
}

// Voice toggle for general voice control
let isVoiceEnabled = false;
const voiceToggle = document.getElementById('voiceToggle');

if (voiceToggle) {
    voiceToggle.addEventListener('click', toggleVoiceControl);
}

function toggleVoiceControl() {
    isVoiceEnabled = !isVoiceEnabled;
    
    if (isVoiceEnabled) {
        voiceToggle.innerHTML = '<i class="fas fa-microphone-slash"></i>';
        showNotification('Voice control enabled');
    } else {
        voiceToggle.innerHTML = '<i class="fas fa-microphone"></i>';
        showNotification('Voice control disabled');
    }
}

// Notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg text-white ${
        type === 'error' ? 'bg-red-500' : 'bg-blue-500'
    }`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('opacity-0', 'transition-opacity', 'duration-500');
        setTimeout(() => notification.remove(), 500);
    }, 3000);
}

// Authentication helper
function checkAuth() {
    if (!localStorage.getItem('token')) {
        window.location.href = '/login';
    }
}

// Initialize tooltips
function initTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(el => {
        const tooltip = document.createElement('div');
        tooltip.className = 'hidden absolute z-10 p-2 text-sm text-white bg-gray-800 rounded';
        tooltip.textContent = el.dataset.tooltip;
        el.appendChild(tooltip);
        
        el.addEventListener('mouseenter', () => {
            tooltip.classList.remove('hidden');
        });
        
        el.addEventListener('mouseleave', () => {
            tooltip.classList.add('hidden');
        });
    });
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    initTooltips();
    
    // Check for voice API support
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        if (voiceToggle) {
            voiceToggle.disabled = true;
            voiceToggle.title = 'Voice control not supported in your browser';
        }
    }
});

// Error handling for API calls
async function handleApiCall(promise) {
    try {
        const response = await promise;
        if (!response.ok) {
            throw new Error(response.statusText);
        }
        return await response.json();
    } catch (error) {
        showNotification(`Error: ${error.message}`, 'error');
        console.error('API Error:', error);
        throw error;
    }
}

// Utility function for formatting numbers
function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

// Export functions for use in other modules
window.appUtils = {
    showNotification,
    handleApiCall,
    formatNumber
};