from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import cross_val_score
import pickle
import os
import re
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)

class HealthChatbot:
    def __init__(self):
        print("\n" + "="*70)
        print("🏥 INITIALIZING AI HEALTH CHATBOT")
        print("="*70)
        
        # Initialize vectorizer with optimal parameters
        self.vectorizer = TfidfVectorizer(
            max_features=2000,
            ngram_range=(1, 3),  # Unigrams, bigrams, trigrams
            min_df=1,
            max_df=0.8,
            token_pattern=r'\b\w+\b',
            stop_words=None,
            sublinear_tf=True,
            norm='l2'
        )
        
        # Initialize ensemble models
        self.knn_model = KNeighborsClassifier(
            n_neighbors=5,
            weights='distance',
            metric='cosine',
            algorithm='brute'
        )
        
        self.rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            min_samples_split=2,
            random_state=42
        )
        
        self.diseases_data = {}
        self.symptom_vectors = None
        self.disease_names = None
        
        # Load and train
        self.load_data()
        self.train_models()
        
    def preprocess_symptoms(self, text):
        """Advanced text preprocessing"""
        text = str(text).lower()
        text = ' '.join(text.split())
        text = re.sub(r'[^a-z\s]', ' ', text)
        text = ' '.join(text.split())
        return text
    
    def load_data(self):
        """Load disease data from CSV"""
        try:
            print("\n📂 Loading disease database...")
            df = pd.read_csv('data/diseases.csv')
            self.df = df
            
            # Preprocess symptoms
            self.df['symptoms_processed'] = self.df['symptoms'].apply(self.preprocess_symptoms)
            
            # Create disease information dictionary
            for _, row in df.iterrows():
                self.diseases_data[row['disease']] = {
                    'description': row['description'],
                    'symptoms': row['symptoms'],
                    'prevention': row['prevention'],
                    'treatment': row['treatment']
                }
            
            print(f"✅ Loaded {len(self.df)} diseases successfully")
            print(f"✅ Total unique symptoms: {len(set(' '.join(self.df['symptoms_processed']).split()))}")
            
        except Exception as e:
            print(f"❌ ERROR loading data: {e}")
            raise
    
    def train_models(self):
        """Train both KNN and Random Forest models"""
        try:
            print("\n🧠 Training ML models...")
            
            if not hasattr(self, 'df') or self.df is None:
                raise ValueError("No data loaded!")
            
            X = self.df['symptoms_processed']
            y = self.df['disease']
            
            # Fit vectorizer and transform data
            print("   ⚙️  Vectorizing symptoms...")
            X_vectorized = self.vectorizer.fit_transform(X)
            self.symptom_vectors = X_vectorized
            self.disease_names = y.values
            
            # Train KNN
            print("   ⚙️  Training K-Nearest Neighbors...")
            self.knn_model.fit(X_vectorized, y)
            
            # Train Random Forest
            print("   ⚙️  Training Random Forest...")
            self.rf_model.fit(X_vectorized.toarray(), y)
            
            # Evaluate models
            print("\n📊 Model Evaluation:")
            #knn_scores = cross_val_score(self.knn_model, X_vectorized, y, cv=2, scoring='accuracy')
            #rf_scores = cross_val_score(self.rf_model, X_vectorized.toarray(), y, cv=2, scoring='accuracy')
            self.knn_model.fit(X_vectorized, y)
            self.rf_model.fit(X_vectorized.toarray(), y)
            
            #print(f"   KNN Accuracy: {knn_scores.mean()*100:.2f}% (±{knn_scores.std()*100:.2f}%)")
            #print(f"   Random Forest Accuracy: {rf_scores.mean()*100:.2f}% (±{rf_scores.std()*100:.2f}%)")
            
            # Save models
            os.makedirs('models', exist_ok=True)
            with open('models/vectorizer.pkl', 'wb') as f:
                pickle.dump(self.vectorizer, f)
            with open('models/knn_model.pkl', 'wb') as f:
                pickle.dump(self.knn_model, f)
            with open('models/rf_model.pkl', 'wb') as f:
                pickle.dump(self.rf_model, f)
            
            print(f"\n✅ Models trained successfully")
            print(f"✅ Feature dimensions: {X_vectorized.shape[1]}")
            
        except Exception as e:
            print(f"❌ ERROR training models: {e}")
            raise
    
    def calculate_word_overlap(self, input_symptoms, disease_symptoms):
        """Calculate word overlap percentage"""
        input_words = set(input_symptoms.lower().split())
        disease_words = set(disease_symptoms.lower().split())
        
        if not input_words:
            return 0.0
        
        matches = len(input_words & disease_words)
        overlap = (matches / len(input_words)) * 100
        
        return overlap
    
    def predict_disease(self, symptoms_text):
        """Ensemble prediction using multiple methods"""
        try:
            # Check if models are trained
            if self.symptom_vectors is None:
                return [{
                    'disease': 'Error',
                    'confidence': 0,
                    'method': 'error',
                    'info': {
                        'description': 'Model not trained. Please restart the server.',
                        'symptoms': '',
                        'prevention': '',
                        'treatment': ''
                    }
                }]
            
            # Preprocess input
            symptoms_processed = self.preprocess_symptoms(symptoms_text)
            print(f"\n🔍 Analyzing: {symptoms_processed}")
            
            # Vectorize input
            symptoms_vectorized = self.vectorizer.transform([symptoms_processed])
            
            # Method 1: Cosine Similarity
            cosine_scores = cosine_similarity(symptoms_vectorized, self.symptom_vectors)[0]
            
            # Method 2: KNN Prediction with probabilities
            knn_distances, knn_indices = self.knn_model.kneighbors(symptoms_vectorized, n_neighbors=5)
            knn_predictions = {}
            for idx, dist in zip(knn_indices[0], knn_distances[0]):
                disease = self.disease_names[idx]
                score = 1 / (dist + 1e-5)  # Convert distance to similarity
                knn_predictions[disease] = knn_predictions.get(disease, 0) + score
            
            # Method 3: Random Forest probabilities
            rf_probs = self.rf_model.predict_proba(symptoms_vectorized.toarray())[0]
            rf_predictions = {disease: prob for disease, prob in zip(self.rf_model.classes_, rf_probs)}
            
            # Method 4: Word Overlap
            test_words = set(symptoms_processed.split())
            overlap_scores = []
            for idx in range(len(self.disease_names)):
                disease_symptoms = self.df.iloc[idx]['symptoms_processed']
                overlap = self.calculate_word_overlap(symptoms_text, disease_symptoms)
                overlap_scores.append(overlap)
            
            overlap_scores = np.array(overlap_scores)
            overlap_normalized = overlap_scores / 100.0
            
            # Ensemble: Combine all methods
            final_scores = np.zeros(len(self.disease_names))
            
            for idx, disease in enumerate(self.disease_names):
                # Weighted ensemble
                cosine_score = cosine_scores[idx]
                knn_score = knn_predictions.get(disease, 0) / max(knn_predictions.values()) if knn_predictions else 0
                rf_score = rf_predictions.get(disease, 0)
                overlap_score = overlap_normalized[idx]
                
                # Weights: 30% cosine, 25% KNN, 25% RF, 20% overlap
                final_scores[idx] = (0.30 * cosine_score + 
                                    0.25 * knn_score + 
                                    0.25 * rf_score + 
                                    0.20 * overlap_score)
            
            # Get top 3 predictions
            top_indices = np.argsort(final_scores)[::-1][:3]
            
            predictions = []
            print("\n📊 Top Predictions:")
            
            for rank, idx in enumerate(top_indices, 1):
                disease = self.disease_names[idx]
                confidence = min(100, final_scores[idx] * 100)
                
                # Determine primary method
                method_scores = {
                    'cosine': cosine_scores[idx] * 100,
                    'knn': knn_predictions.get(disease, 0) * 10,
                    'rf': rf_predictions.get(disease, 0) * 100,
                    'overlap': overlap_scores[idx]
                }
                primary_method = max(method_scores, key=method_scores.get)
                
                print(f"   {rank}. {disease}: {confidence:.1f}% "
                      f"(cosine:{method_scores['cosine']:.0f}% "
                      f"rf:{method_scores['rf']:.0f}% "
                      f"overlap:{method_scores['overlap']:.0f}%)")
                
                predictions.append({
                    'disease': disease,
                    'confidence': round(confidence, 1),
                    'method': primary_method,
                    'breakdown': {
                        'cosine': round(method_scores['cosine'], 1),
                        'knn': round(method_scores['knn'], 1),
                        'random_forest': round(method_scores['rf'], 1),
                        'word_overlap': round(method_scores['overlap'], 1)
                    },
                    'info': self.diseases_data.get(disease, {})
                })
            
            return predictions
            
        except Exception as e:
            print(f"❌ Prediction error: {e}")
            import traceback
            traceback.print_exc()
            return [{
                'disease': 'Error',
                'confidence': 0,
                'method': 'error',
                'info': {
                    'description': f'Prediction error: {str(e)}',
                    'symptoms': '',
                    'prevention': '',
                    'treatment': ''
                }
            }]

# Initialize chatbot
print("\n" + "="*70)
print("🚀 STARTING AI HEALTH CHATBOT SERVER")
print("="*70)
chatbot = HealthChatbot()
print("\n" + "="*70)
print("✅ SERVER READY")
print("="*70 + "\n")

# Multilingual translations
translations = {
    'en': {
        'title': 'AI Health Chatbot',
        'subtitle': 'Disease Prediction & Awareness System',
        'symptoms_placeholder': 'Describe your symptoms (e.g., fever, cough, headache)...',
        'analyze': 'Analyze Symptoms',
        'clear': 'Clear',
        'results': 'Prediction Results',
        'description': 'Description',
        'symptoms': 'Common Symptoms',
        'prevention': 'Prevention',
        'treatment': 'Treatment',
        'confidence': 'Match Confidence',
        'disclaimer': '⚠️ DISCLAIMER: This AI tool is for educational purposes only and NOT a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider for medical concerns.',
        'speak': 'Speak',
        'listening': 'Listening...',
        'powered_by': 'Powered by Machine Learning',
        'model_info': 'Ensemble AI Model (KNN + Random Forest + NLP)'
    },
    'or': {
    'title': 'ଏଆଇ ସ୍ୱାସ୍ଥ୍ୟ ଚ୍ୟାଟବଟ୍',
    'subtitle': 'ରୋଗ ପୂର୍ବାନୁମାନ ଓ ସଚେତନତା ପ୍ରଣାଳୀ',
    'symptoms_placeholder': 'ଆପଣଙ୍କ ଲକ୍ଷଣ ଲେଖନ୍ତୁ (ଯେପରିକି: ଜ୍ୱର, କାଶ, ମୁଣ୍ଡବେଦନା)...',
    'analyze': 'ଲକ୍ଷଣ ବିଶ୍ଳେଷଣ',
    'clear': 'ସଫା କରନ୍ତୁ',
    'results': 'ପୂର୍ବାନୁମାନ ଫଳାଫଳ',
    'description': 'ବର୍ଣ୍ଣନା',
    'symptoms': 'ସାଧାରଣ ଲକ୍ଷଣ',
    'prevention': 'ପ୍ରତିରୋଧ',
    'treatment': 'ଚିକିତ୍ସା',
    'confidence': 'ମେଳ ନିଶ୍ଚିତତା',
    'disclaimer': '⚠️ ସଚେତନତା: ଏହି AI ଉପକରଣ କେବଳ ଶିକ୍ଷାମୂଳକ ଉଦ୍ଦେଶ୍ୟ ପାଇଁ।',
    'speak': 'କହନ୍ତୁ',
    'listening': 'ଶୁଣୁଛି...',
    'powered_by': 'ମେସିନ୍ ଲର୍ନିଂ ଦ୍ୱାରା ଚାଳିତ',
    'model_info': 'AI ମଡେଲ୍ (KNN + Random Forest + NLP)'
},

'te': {
    'title': 'AI ఆరోగ్య చాట్‌బాట్',
    'subtitle': 'వ్యాధి అంచనా మరియు అవగాహన వ్యవస్థ',
    'symptoms_placeholder': 'మీ లక్షణాలను వివరించండి (ఉదా: జ్వరం, దగ్గు, తలనొప్పి)...',
    'analyze': 'లక్షణాలను విశ్లేషించండి',
    'clear': 'క్లియర్ చేయండి',
    'results': 'అంచనా ఫలితాలు',
    'description': 'వివరణ',
    'symptoms': 'సాధారణ లక్షణాలు',
    'prevention': 'నివారణ',
    'treatment': 'చికిత్స',
    'confidence': 'సరిపోలిక విశ్వాసం',
    'disclaimer': '⚠️ ఈ AI సాధనం విద్యాపరమైన ప్రయోజనాల కోసం మాత్రమే.',
    'speak': 'మాట్లాడు',
    'listening': 'వింటోంది...',
    'powered_by': 'మెషిన్ లెర్నింగ్ ద్వారా శక్తినిచ్చింది',
    'model_info': 'AI మోడల్ (KNN + Random Forest + NLP)'
},

'ta': {
    'title': 'AI ஆரோக்கிய சாட்பாட்',
    'subtitle': 'நோய் கணிப்பு மற்றும் விழிப்புணர்வு அமைப்பு',
    'symptoms_placeholder': 'உங்கள் அறிகுறிகளை எழுதுங்கள் (எ.கா: காய்ச்சல், இருமல், தலைவலி)...',
    'analyze': 'அறிகுறிகளை பகுப்பாய்வு செய்',
    'clear': 'அழி',
    'results': 'கணிப்பு முடிவுகள்',
    'description': 'விளக்கம்',
    'symptoms': 'பொதுவான அறிகுறிகள்',
    'prevention': 'தடுப்பு',
    'treatment': 'சிகிச்சை',
    'confidence': 'பொருந்தும் நம்பிக்கை',
    'disclaimer': '⚠️ இந்த AI கருவி கல்விக்கான பயன்பாட்டிற்கு மட்டும்.',
    'speak': 'பேசு',
    'listening': 'கேட்கிறது...',
    'powered_by': 'மெஷின் லெர்னிங் மூலம் இயக்கப்படுகிறது',
    'model_info': 'AI மாடல் (KNN + Random Forest + NLP)'
},

'kn': {
    'title': 'ಎಐ ಆರೋಗ್ಯ ಚಾಟ್‌ಬಾಟ್',
    'subtitle': 'ರೋಗ ಭವಿಷ್ಯವಾಣಿ ಮತ್ತು ಜಾಗೃತಿ ವ್ಯವಸ್ಥೆ',
    'symptoms_placeholder': 'ನಿಮ್ಮ ಲಕ್ಷಣಗಳನ್ನು ವಿವರಿಸಿ (ಉದಾ: ಜ್ವರ, ಕೆಮ್ಮು, ತಲೆನೋವು)...',
    'analyze': 'ಲಕ್ಷಣಗಳನ್ನು ವಿಶ್ಲೇಷಿಸಿ',
    'clear': 'ಅಳಿಸಿ',
    'results': 'ಭವಿಷ್ಯವಾಣಿ ಫಲಿತಾಂಶಗಳು',
    'description': 'ವಿವರಣೆ',
    'symptoms': 'ಸಾಮಾನ್ಯ ಲಕ್ಷಣಗಳು',
    'prevention': 'ತಡೆಗಟ್ಟುವಿಕೆ',
    'treatment': 'ಚಿಕಿತ್ಸೆ',
    'confidence': 'ಹೊಂದಾಣಿಕೆ ವಿಶ್ವಾಸ',
    'disclaimer': '⚠️ ಈ AI ಸಾಧನವು ಶಿಕ್ಷಣ ಉದ್ದೇಶಕ್ಕಾಗಿ ಮಾತ್ರ.',
    'speak': 'ಮಾತನಾಡಿ',
    'listening': 'ಕೇಳುತ್ತಿದೆ...',
    'powered_by': 'ಮೆಷಿನ್ ಲರ್ನಿಂಗ್ ಮೂಲಕ ಚಾಲಿತ',
    'model_info': 'AI ಮಾದರಿ (KNN + Random Forest + NLP)'
},
    'es': {
        'title': 'Chatbot de Salud IA',
        'subtitle': 'Sistema de Predicción y Concienciación de Enfermedades',
        'symptoms_placeholder': 'Describe tus síntomas (ej: fiebre, tos, dolor de cabeza)...',
        'analyze': 'Analizar Síntomas',
        'clear': 'Limpiar',
        'results': 'Resultados de Predicción',
        'description': 'Descripción',
        'symptoms': 'Síntomas Comunes',
        'prevention': 'Prevención',
        'treatment': 'Tratamiento',
        'confidence': 'Confianza de Coincidencia',
        'disclaimer': '⚠️ DESCARGO: Esta herramienta de IA es solo para fines educativos y NO sustituye el consejo, diagnóstico o tratamiento médico profesional.',
        'speak': 'Hablar',
        'listening': 'Escuchando...',
        'powered_by': 'Impulsado por Aprendizaje Automático',
        'model_info': 'Modelo IA Ensemble (KNN + Random Forest + NLP)'
    },
    'fr': {
        'title': 'Chatbot Santé IA',
        'subtitle': 'Système de Prédiction et Sensibilisation aux Maladies',
        'symptoms_placeholder': 'Décrivez vos symptômes (ex: fièvre, toux, mal de tête)...',
        'analyze': 'Analyser les Symptômes',
        'clear': 'Effacer',
        'results': 'Résultats de Prédiction',
        'description': 'Description',
        'symptoms': 'Symptômes Courants',
        'prevention': 'Prévention',
        'treatment': 'Traitement',
        'confidence': 'Confiance de Correspondance',
        'disclaimer': '⚠️ AVERTISSEMENT: Cet outil IA est à des fins éducatives uniquement et NE remplace PAS les conseils, diagnostics ou traitements médicaux professionnels.',
        'speak': 'Parler',
        'listening': 'Écoute...',
        'powered_by': 'Propulsé par Apprentissage Automatique',
        'model_info': 'Modèle IA Ensemble (KNN + Random Forest + NLP)'
    },
    'hi': {
        'title': 'एआई स्वास्थ्य चैटबॉट',
        'subtitle': 'रोग भविष्यवाणी और जागरूकता प्रणाली',
        'symptoms_placeholder': 'अपने लक्षणों का वर्णन करें (जैसे: बुखार, खांसी, सिरदर्द)...',
        'analyze': 'लक्षणों का विश्लेषण करें',
        'clear': 'साफ़ करें',
        'results': 'भविष्यवाणी परिणाम',
        'description': 'विवरण',
        'symptoms': 'सामान्य लक्षण',
        'prevention': 'रोकथाम',
        'treatment': 'इलाज',
        'confidence': 'मिलान विश्वास',
        'disclaimer': '⚠️ अस्वीकरण: यह एआई उपकरण केवल शैक्षिक उद्देश्यों के लिए है और पेशेवर चिकित्सा सलाह का विकल्प नहीं है।',
        'speak': 'बोलें',
        'listening': 'सुन रहा है...',
        'powered_by': 'मशीन लर्निंग द्वारा संचालित',
        'model_info': 'एन्सेम्बल एआई मॉडल (KNN + Random Forest + NLP)'
    },
    'zh': {
        'title': 'AI健康聊天机器人',
        'subtitle': '疾病预测与意识系统',
        'symptoms_placeholder': '描述您的症状（例如：发烧、咳嗽、头痛）...',
        'analyze': '分析症状',
        'clear': '清除',
        'results': '预测结果',
        'description': '描述',
        'symptoms': '常见症状',
        'prevention': '预防',
        'treatment': '治疗',
        'confidence': '匹配置信度',
        'disclaimer': '⚠️ 免责声明：此AI工具仅用于教育目的，不能替代专业医疗建议、诊断或治疗。',
        'speak': '说话',
        'listening': '正在聆听...',
        'powered_by': '由机器学习驱动',
        'model_info': '集成AI模型 (KNN + Random Forest + NLP)'
    }
}

# API Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        symptoms = data.get('symptoms', '')
        
        if not symptoms:
            return jsonify({'error': 'No symptoms provided'}), 400
        
        predictions = chatbot.predict_disease(symptoms)
        
        return jsonify({
            'success': True,
            'predictions': predictions,
            'model_info': 'Ensemble AI (KNN + Random Forest + NLP)'
        })
    
    except Exception as e:
        print(f"❌ API Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/translations/<lang>')
def get_translations(lang):
    return jsonify(translations.get(lang, translations['en']))

@app.route('/api/diseases')
def get_all_diseases():
    return jsonify({
        'diseases': list(chatbot.diseases_data.keys()),
        'total': len(chatbot.diseases_data)
    })

@app.route('/api/disease/<disease_name>')
def get_disease_info(disease_name):
    info = chatbot.diseases_data.get(disease_name)
    if info:
        return jsonify({
            'success': True,
            'disease': disease_name,
            'info': info
        })
    else:
        return jsonify({'error': 'Disease not found'}), 404

@app.route('/api/stats')
def get_stats():
    """Get system statistics"""
    return jsonify({
        'total_diseases': len(chatbot.diseases_data),
        'total_symptoms': len(set(' '.join(chatbot.df['symptoms_processed']).split())),
        'model_features': chatbot.symptom_vectors.shape[1],
        'languages_supported': len(translations),
        'models_used': ['KNN', 'Random Forest', 'TF-IDF', 'Cosine Similarity']
    })

if __name__ == '__main__':
    print("🌐 Server starting on http://localhost:5000")
    print("📱 Mobile-friendly interface ready")
    print("🎤 Voice input supported")
    print("🌍 5 languages available")
    print("\n" + "="*70 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
