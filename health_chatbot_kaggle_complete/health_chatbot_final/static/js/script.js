
// Enhanced AI Health Chatbot - Frontend JavaScript

let currentLanguage = 'en';
let translations = {};
let recognition = null;

// Initialize Speech Recognition
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
}

// Load translations on page load
document.addEventListener('DOMContentLoaded', function() {
    loadTranslations('en');
    loadSystemStats();
});

// Fill example symptoms
function fillExample(symptoms) {
    document.getElementById('symptoms').value = symptoms;
    document.getElementById('symptoms').focus();
}

// Change language
async function changeLanguage() {
    const langSelect = document.getElementById('language');
    currentLanguage = langSelect.value;
    await loadTranslations(currentLanguage);
    
    if (recognition) {
        const langCodes = {
            'en': 'en-US',
            'es': 'es-ES',
            'fr': 'fr-FR',
            'hi': 'hi-IN',
            'zh': 'zh-CN'
        };
        recognition.lang = langCodes[currentLanguage] || 'en-US';
    }
}

// Load translations from API
async function loadTranslations(lang) {
    try {
        const response = await fetch(`/api/translations/${lang}`);
        translations = await response.json();
        updateUIText();
    } catch (error) {
        console.error('Error loading translations:', error);
    }
}

// Update UI text with translations
function updateUIText() {
    document.getElementById('app-title').textContent = translations.title || 'AI Health Chatbot';
    document.getElementById('app-subtitle').textContent = translations.subtitle || 'Disease Prediction System';
    document.getElementById('model-info').textContent = translations.model_info || 'Ensemble AI Model';
    document.getElementById('symptoms').placeholder = translations.symptoms_placeholder || 'Describe your symptoms...';
    document.getElementById('btn-analyze').textContent = translations.analyze || 'Analyze Symptoms';
    document.getElementById('btn-clear').textContent = translations.clear || 'Clear';
    document.getElementById('voice-text').textContent = translations.speak || 'Speak';
    document.getElementById('powered-by').textContent = translations.powered_by || 'Powered by ML';
    
    const resultsTitle = document.getElementById('results-title');
    if (resultsTitle) {
        resultsTitle.innerHTML = `<i class="fas fa-chart-line"></i> ${translations.results || 'Results'}`;
    }
    
    document.getElementById('disclaimer-text').textContent = translations.disclaimer || 
        'DISCLAIMER: This is for educational purposes only.';
}

// Load system statistics
async function loadSystemStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        document.getElementById('stats-diseases').textContent = `${stats.total_diseases} Diseases`;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Start voice input
function startVoiceInput() {
    if (!recognition) {
        alert('Speech recognition not supported. Please use Chrome, Edge, or Safari.');
        return;
    }

    const voiceBtn = document.getElementById('voiceBtn');
    const voiceText = document.getElementById('voice-text');
    const symptomsInput = document.getElementById('symptoms');

    const langCodes = {
        'en': 'en-US',
        'es': 'es-ES',
        'fr': 'fr-FR',
        'hi': 'hi-IN',
        'zh': 'zh-CN'
    };
    recognition.lang = langCodes[currentLanguage] || 'en-US';

    recognition.onstart = function() {
        voiceBtn.classList.add('listening');
        voiceText.textContent = translations.listening || 'Listening...';
    };

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        symptomsInput.value = transcript;
    };

    recognition.onerror = function(event) {
        console.error('Speech recognition error:', event.error);
        voiceBtn.classList.remove('listening');
        voiceText.textContent = translations.speak || 'Speak';
        
        if (event.error === 'no-speech') {
            alert('No speech detected. Please try again.');
        } else if (event.error === 'not-allowed') {
            alert('Microphone access denied. Please enable permissions.');
        }
    };

    recognition.onend = function() {
        voiceBtn.classList.remove('listening');
        voiceText.textContent = translations.speak || 'Speak';
    };

    recognition.start();
}

// Clear input
function clearInput() {
    document.getElementById('symptoms').value = '';
    document.getElementById('results').style.display = 'none';
    document.getElementById('symptoms').focus();
}

// Analyze symptoms
async function analyzeSymptoms() {
    const symptomsInput = document.getElementById('symptoms').value.trim();
    
    if (!symptomsInput) {
        alert('Please describe your symptoms.');
        return;
    }

    document.getElementById('loading').style.display = 'block';
    document.getElementById('results').style.display = 'none';

    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                symptoms: symptomsInput
            })
        });

        const data = await response.json();

        if (data.success) {
            displayResults(data.predictions);
        } else {
            alert('Error: ' + (data.error || 'Something went wrong'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to analyze symptoms. Please try again.');
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
}

// Display results
function displayResults(predictions) {
    const resultsDiv = document.getElementById('results');
    const container = document.getElementById('predictions-container');
    
    container.innerHTML = '';

    if (!predictions || predictions.length === 0) {
        container.innerHTML = `
            <div class="disease-card">
                <p>No matching diseases found. Please try different symptoms.</p>
            </div>
        `;
    } else {
        predictions.forEach((pred, index) => {
            const card = createDiseaseCard(pred, index);
            container.appendChild(card);
        });
    }

    resultsDiv.style.display = 'block';
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Get confidence color
function getConfidenceColor(confidence) {
    if (confidence >= 70) return 'var(--success)';
    if (confidence >= 50) return 'var(--warning)';
    return 'var(--danger)';
}

// Create disease card
function createDiseaseCard(prediction, index) {
    const card = document.createElement('div');
    card.className = 'disease-card';
    card.style.animationDelay = `${index * 0.1}s`;
    
    const info = prediction.info || {};
    const confidence = prediction.confidence || 0;
    const confidenceColor = getConfidenceColor(confidence);
    const method = prediction.method || 'ensemble';
    
    const icons = ['fa-virus', 'fa-notes-medical', 'fa-stethoscope'];
    const icon = icons[index % icons.length];

    card.innerHTML = `
        <div class="disease-header">
            <div class="disease-icon">
                <i class="fas ${icon}"></i>
            </div>
            <div class="disease-info">
                <h3 class="disease-title">${prediction.disease}</h3>
                <div class="confidence-container">
                    <div class="confidence-bar-wrapper">
                        <div class="confidence-bar" style="width: ${confidence}%; background: ${confidenceColor}"></div>
                    </div>
                    <div class="confidence-text">
                        <span style="color: ${confidenceColor}">
                            ${translations.confidence || 'Confidence'}: ${confidence}%
                        </span>
                        <span class="method-badge">AI ${method.toUpperCase()}</span>
                    </div>
                </div>
            </div>
        </div>
        
        ${info.description ? `
        <div class="disease-section">
            <h4><i class="fas fa-info-circle"></i> ${translations.description || 'Description'}</h4>
            <p>${info.description}</p>
        </div>
        ` : ''}
        
        ${info.symptoms ? `
        <div class="disease-section">
            <h4><i class="fas fa-thermometer-half"></i> ${translations.symptoms || 'Symptoms'}</h4>
            <p>${info.symptoms}</p>
        </div>
        ` : ''}
        
        ${info.prevention ? `
        <div class="disease-section">
            <h4><i class="fas fa-shield-alt"></i> ${translations.prevention || 'Prevention'}</h4>
            <p>${info.prevention}</p>
        </div>
        ` : ''}
        
        ${info.treatment ? `
        <div class="disease-section">
            <h4><i class="fas fa-pills"></i> ${translations.treatment || 'Treatment'}</h4>
            <p>${info.treatment}</p>
        </div>
        ` : ''}
    `;
    
    return card;
}

// Modal functions
function showInfo(type) {
    const modal = document.getElementById('infoModal');
    const modalBody = document.getElementById('modalBody');
    
    let content = '';
    if (type === 'about') {
        content = `
            <h2>About AI Health Chatbot</h2>
            <p>AI-powered disease prediction using ensemble machine learning.</p>
            <ul>
                <li>41 diseases in database</li>
                <li>Ensemble AI (KNN + Random Forest + NLP)</li>
                <li>5 languages supported</li>
                <li>Voice input enabled</li>
            </ul>
        `;
    } else if (type === 'privacy') {
        content = `
            <h2>Privacy Policy</h2>
            <p>We respect your privacy:</p>
            <ul>
                <li>No data stored permanently</li>
                <li>Real-time analysis only</li>
                <li>No personal information collected</li>
                <li>No tracking or cookies</li>
            </ul>
        `;
    } else if (type === 'contact') {
        content = `
            <h2>Contact</h2>
            <p>For questions or feedback about this AI health chatbot.</p>
        `;
    }
    
    modalBody.innerHTML = content;
    modal.style.display = 'flex';
}

function closeModal() {
    document.getElementById('infoModal').style.display = 'none';
}

// Enter key to submit
document.addEventListener('DOMContentLoaded', function() {
    const symptomsInput = document.getElementById('symptoms');
    
    symptomsInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            analyzeSymptoms();
        }
    });
});

// Touch feedback for mobile
document.addEventListener('DOMContentLoaded', function() {
    const buttons = document.querySelectorAll('.btn, .voice-btn, .example-btn');
    
    buttons.forEach(button => {
        button.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.95)';
        });
        
        button.addEventListener('touchend', function() {
            this.style.transform = '';
        });
    });
});
