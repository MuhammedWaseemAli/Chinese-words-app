import streamlit as st
import pandas as pd
from gtts import gTTS
import base64
from io import BytesIO
import random
import time

# 📂 Path to your Excel file (⚠️ Use raw string for Windows path)
EXCEL_FILE = r"C:\er5FILES\chinese_learning_streamlit (1).xlsx"

# Load Excel
df = pd.read_excel(EXCEL_FILE)

# Initialize session state for quiz
if 'quiz_active' not in st.session_state:
    st.session_state.quiz_active = False
if 'speech_active' not in st.session_state:
    st.session_state.speech_active = False
if 'current_question' not in st.session_state:
    st.session_state.current_question = None
if 'quiz_options' not in st.session_state:
    st.session_state.quiz_options = []
if 'correct_answer' not in st.session_state:
    st.session_state.correct_answer = ""
if 'quiz_score' not in st.session_state:
    st.session_state.quiz_score = 0
if 'quiz_total' not in st.session_state:
    st.session_state.quiz_total = 0
if 'quiz_answered' not in st.session_state:
    st.session_state.quiz_answered = False
if 'quiz_category' not in st.session_state:
    st.session_state.quiz_category = "All"
if 'quiz_difficulty' not in st.session_state:
    st.session_state.quiz_difficulty = "Easy"
if 'current_speech' not in st.session_state:
    st.session_state.current_speech = []
if 'speech_settings' not in st.session_state:
    st.session_state.speech_settings = {'sentences': 5, 'speed': 'normal', 'include_pinyin': True}

# 🎨 Enhanced Custom CSS with beautiful aesthetics
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Main app styling */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        min-height: 100vh;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Floating Chinese characters with enhanced animation */
    .floating-text {
        position: fixed;
        font-size: 32px;
        font-weight: 700;
        color: rgba(255,255,255,0.15);
        animation: float 20s infinite linear;
        z-index: -1;
        font-family: 'Noto Sans TC', sans-serif;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        pointer-events: none;
    }
    
    @keyframes float {
        0% { 
            transform: translateY(100vh) translateX(0) rotate(0deg); 
            opacity: 0; 
            filter: blur(2px);
        }
        10% { opacity: 0.8; filter: blur(0px); }
        90% { opacity: 0.8; filter: blur(0px); }
        100% { 
            transform: translateY(-20vh) translateX(100px) rotate(360deg); 
            opacity: 0; 
            filter: blur(2px);
        }
    }
    
    /* Custom title styling */
    .main-title {
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #f9ca24, #6c5ce7);
        background-size: 300% 300%;
        animation: gradientShift 8s ease infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        margin: 2rem 0;
        font-family: 'Inter', sans-serif;
        text-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* Container styling */
    .main-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 25px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* Word card styling */
    .word-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.7) 100%);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.3);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .word-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.8) 100%);
    }
    
    .word-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        transition: left 0.5s ease;
    }
    
    .word-card:hover::before {
        left: 100%;
    }
    
    /* Speech card styling */
    .speech-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.85) 100%);
        backdrop-filter: blur(15px);
        border-radius: 25px;
        padding: 2.5rem;
        margin: 2rem 0;
        box-shadow: 0 25px 50px rgba(0,0,0,0.15);
        border: 2px solid rgba(255,255,255,0.3);
        position: relative;
        overflow: hidden;
    }
    
    .speech-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1, #f9ca24, #6c5ce7);
        background-size: 300% 300%;
        animation: gradientShift 3s ease infinite;
    }
    
    /* Quiz card styling */
    .quiz-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.85) 100%);
        backdrop-filter: blur(15px);
        border-radius: 25px;
        padding: 2.5rem;
        margin: 2rem 0;
        box-shadow: 0 25px 50px rgba(0,0,0,0.15);
        border: 2px solid rgba(255,255,255,0.3);
        position: relative;
        overflow: hidden;
    }
    
    .quiz-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1, #f9ca24, #6c5ce7);
        background-size: 300% 300%;
        animation: gradientShift 3s ease infinite;
    }
    
    /* Speech sentence styling */
    .speech-sentence {
        background: linear-gradient(135deg, rgba(255,255,255,0.8), rgba(255,255,255,0.6));
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border-left: 5px solid;
        transition: all 0.3s ease;
    }
    
    .speech-sentence:hover {
        transform: translateX(5px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.15);
    }
    
    .speech-chinese {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2c3e50;
        font-family: 'Noto Sans TC', sans-serif;
        margin-bottom: 0.5rem;
    }
    
    .speech-english {
        font-size: 1.2rem;
        font-weight: 500;
        color: #34495e;
        font-family: 'Inter', sans-serif;
        margin-bottom: 0.3rem;
    }
    
    .speech-pinyin {
        font-size: 1rem;
        font-style: italic;
        color: #7f8c8d;
        font-family: 'Inter', sans-serif;
    }
    
    /* Quiz option buttons */
    .quiz-option {
        background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.7));
        border: 2px solid rgba(102, 126, 234, 0.3);
        border-radius: 15px;
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
        width: 100%;
        text-align: left;
        font-size: 1.1rem;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
        color: #2c3e50;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        position: relative;
        overflow: hidden;
    }
    
    .quiz-option:hover {
        transform: translateY(-2px);
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        border-color: rgba(102, 126, 234, 0.6);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.2);
    }
    
    .quiz-option.correct {
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.2), rgba(139, 195, 74, 0.2));
        border-color: #4caf50;
        color: #2e7d32;
        box-shadow: 0 10px 25px rgba(76, 175, 80, 0.3);
    }
    
    .quiz-option.incorrect {
        background: linear-gradient(135deg, rgba(244, 67, 54, 0.2), rgba(255, 87, 34, 0.2));
        border-color: #f44336;
        color: #c62828;
        box-shadow: 0 10px 25px rgba(244, 67, 54, 0.3);
    }
    
    /* Text styling */
    .english-word {
        font-size: 1.3rem;
        font-weight: 600;
        color: #2c3e50;
        font-family: 'Inter', sans-serif;
        margin-bottom: 0.5rem;
    }
    
    .chinese-word {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-family: 'Noto Sans TC', sans-serif;
        margin-bottom: 0.5rem;
    }
    
    .quiz-chinese-word {
        font-size: 4rem;
        font-weight: 800;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-family: 'Noto Sans TC', sans-serif;
        margin: 2rem 0;
        text-align: center;
        text-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .pinyin-word {
        font-size: 1.1rem;
        font-weight: 500;
        color: #7f8c8d;
        font-style: italic;
        font-family: 'Inter', sans-serif;
        margin-bottom: 0.5rem;
    }
    
    .category-tag {
        display: inline-block;
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Audio button styling */
    .audio-btn {
        background: linear-gradient(45deg, #ff6b6b, #ffa726);
        border: none;
        color: white;
        padding: 0.8rem 1.5rem;
        border-radius: 50px;
        font-size: 1.2rem;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.3);
        font-weight: 600;
    }
    
    .audio-btn:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 15px 35px rgba(255, 107, 107, 0.4);
        background: linear-gradient(45deg, #ff5252, #ff9800);
    }
    
    /* Search and filter styling */
    .stSelectbox > div > div {
        background: rgba(255,255,255,0.9);
        border-radius: 15px;
        border: 2px solid transparent;
        background-clip: padding-box;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.9);
        border-radius: 15px;
        border: 2px solid transparent;
        background-clip: padding-box;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        font-family: 'Inter', sans-serif;
        font-weight: 500;
    }
    
    /* Custom animations */
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 107, 107, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(255, 107, 107, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 107, 107, 0); }
    }
    
    .pulse-animation {
        animation: pulse 2s infinite;
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-10px); }
        60% { transform: translateY(-5px); }
    }
    
    .bounce-animation {
        animation: bounce 1s ease infinite;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.8) 100%);
        backdrop-filter: blur(20px);
    }
    
    /* Hide streamlit elements for cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(45deg, #667eea, #764ba2);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(45deg, #5a6fd8, #6a4190);
    }
    
    /* Stats cards */
    .stats-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.6));
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.3);
        margin: 0.5rem;
    }
    
    .stats-number {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-family: 'Inter', sans-serif;
    }
    
    .stats-label {
        font-size: 1rem;
        color: #7f8c8d;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
        margin-top: 0.5rem;
    }
    
    /* Tab styling */
    .tab-container {
        display: flex;
        justify-content: center;
        margin: 2rem 0;
        gap: 1rem;
    }
    
    .tab-button {
        background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.7));
        border: 2px solid rgba(102, 126, 234, 0.3);
        border-radius: 25px;
        padding: 1rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        color: #2c3e50;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    .tab-button.active {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
    }
    
    .tab-button:hover {
        transform: translateY(-2px);
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        border-color: rgba(102, 126, 234, 0.6);
        box-shadow: 0 12px 30px rgba(102, 126, 234, 0.2);
    }
    
    /* Score display */
    .score-display {
        background: linear-gradient(135deg, #4caf50, #66bb6a);
        color: white;
        border-radius: 20px;
        padding: 1rem 2rem;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(76, 175, 80, 0.3);
        font-family: 'Inter', sans-serif;
        font-weight: 600;
    }
    
    .difficulty-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    .difficulty-easy {
        background: linear-gradient(45deg, #4caf50, #66bb6a);
        color: white;
    }
    
    .difficulty-medium {
        background: linear-gradient(45deg, #ff9800, #ffb74d);
        color: white;
    }
    
    .difficulty-hard {
        background: linear-gradient(45deg, #f44336, #e57373);
        color: white;
    }
    
    /* Speech controls */
    .speech-controls {
        background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.7));
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.3);
    }
    
    .speech-play-btn {
        background: linear-gradient(45deg, #4facfe, #00f2fe);
        border: none;
        color: white;
        padding: 1.2rem 2.5rem;
        border-radius: 50px;
        font-size: 1.3rem;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 10px 30px rgba(79, 172, 254, 0.4);
        font-weight: 700;
        font-family: 'Inter', sans-serif;
    }
    
    .speech-play-btn:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 20px 40px rgba(79, 172, 254, 0.5);
        background: linear-gradient(45deg, #00f2fe, #4facfe);
    }
    </style>
""", unsafe_allow_html=True)

# Enhanced floating characters with more variety
characters = [
    ("愛", "Love"), ("學", "Learn"), ("和", "Peace"), ("力", "Strength"), 
    ("夢", "Dream"), ("水", "Water"), ("天", "Sky"), ("地", "Earth"), 
    ("人", "Person"), ("心", "Heart"), ("美", "Beauty"), ("光", "Light"),
    ("風", "Wind"), ("花", "Flower"), ("月", "Moon"), ("星", "Star"),
    ("海", "Ocean"), ("山", "Mountain"), ("雲", "Cloud"), ("雨", "Rain")
]

# Create more floating characters with staggered timing
for i in range(8):
    char, meaning = random.choice(characters)
    delay = random.uniform(0, 15)  # Random delay for staggered effect
    left_pos = random.randint(0, 95)
    st.markdown(
        f'''<div class="floating-text" style="
            left:{left_pos}%; 
            animation-delay: {delay}s;
            font-size: {random.randint(28, 40)}px;
        ">{char}</div>''',
        unsafe_allow_html=True
    )

# 🌟 Enhanced App Title
st.markdown('<h1 class="main-title">🇹🇼 Learn Traditional Chinese</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: rgba(255,255,255,0.9); font-weight: 500; margin-bottom: 2rem;">Discover the beauty of Traditional Chinese with interactive audio learning, quizzes & speech practice</p>', unsafe_allow_html=True)

# Navigation tabs
st.markdown('<div class="tab-container">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📚 Learn Words", key="learn_tab", help="Browse and learn Chinese words"):
        st.session_state.quiz_active = False
        st.session_state.speech_active = False

with col2:
    if st.button("🧠 Quiz Mode", key="quiz_tab", help="Test your knowledge with interactive quizzes"):
        st.session_state.quiz_active = True
        st.session_state.speech_active = False

with col3:
    if st.button("🎤 Speech Practice", key="speech_tab", help="Practice with randomly generated Chinese speeches"):
        st.session_state.quiz_active = False
        st.session_state.speech_active = True

with col4:
    if st.button("📊 Progress", key="progress_tab", help="View your learning progress"):
        st.session_state.quiz_active = False
        st.session_state.speech_active = False

st.markdown('</div>', unsafe_allow_html=True)

# Stats section
total_words = len(df)
categories = len(df["Category"].unique())
speech_sentences = len(df[df["Category"].str.contains("speech", case=False, na=False)])
accuracy = round((st.session_state.quiz_score / max(st.session_state.quiz_total, 1)) * 100, 1) if st.session_state.quiz_total > 0 else 0

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f'''
        <div class="stats-card">
            <div class="stats-number">{total_words}</div>
            <div class="stats-label">Total Words</div>
        </div>
    ''', unsafe_allow_html=True)

with col2:
    st.markdown(f'''
        <div class="stats-card">
            <div class="stats-number">{categories}</div>
            <div class="stats-label">Categories</div>
        </div>
    ''', unsafe_allow_html=True)

with col3:
    st.markdown(f'''
        <div class="stats-card">
            <div class="stats-number">{speech_sentences}</div>
            <div class="stats-label">Speech Sentences</div>
        </div>
    ''', unsafe_allow_html=True)

with col4:
    st.markdown(f'''
        <div class="stats-card">
            <div class="stats-number">{st.session_state.quiz_total}</div>
            <div class="stats-label">Quiz Attempts</div>
        </div>
    ''', unsafe_allow_html=True)

with col5:
    st.markdown(f'''
        <div class="stats-card">
            <div class="stats-number">{accuracy}%</div>
            <div class="stats-label">Accuracy</div>
        </div>
    ''', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Speech Practice Mode
if st.session_state.speech_active:
    st.markdown("""
        <div class="speech-card">
            <h2 style="text-align: center; color: #2c3e50; font-family: 'Inter', sans-serif; font-weight: 800; margin-bottom: 2rem;">
                🎤 Chinese Speech Practice
            </h2>
            <p style="text-align: center; color: #7f8c8d; font-family: 'Inter', sans-serif; font-size: 1.1rem; margin-bottom: 2rem;">
                Generate random speeches with Chinese sentences for comprehensive listening practice
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Speech settings
    st.markdown("""
        <div class="speech-controls">
            <h3 style="color: #2c3e50; font-family: 'Inter', sans-serif; font-weight: 700; margin-bottom: 1.5rem; text-align: center;">
                🎛️ Speech Settings
            </h3>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        num_sentences = st.slider(
            "📝 Number of Sentences", 
            min_value=3, 
            max_value=15, 
            value=st.session_state.speech_settings['sentences'],
            help="Choose how many sentences to include in the speech"
        )
        st.session_state.speech_settings['sentences'] = num_sentences
    
    with col2:
        speech_speed = st.selectbox(
            "⚡ Speech Speed",
            ["slow", "normal", "fast"],
            index=["slow", "normal", "fast"].index(st.session_state.speech_settings['speed']),
            help="Choose the speed of speech playback"
        )
        st.session_state.speech_settings['speed'] = speech_speed
    
    with col3:
        include_pinyin = st.checkbox(
            "🔤 Show Pinyin", 
            value=st.session_state.speech_settings['include_pinyin'],
            help="Display Pinyin pronunciation guide"
        )
        st.session_state.speech_settings['include_pinyin'] = include_pinyin
    
    def generate_speech():
        # Get all speech sentences (sentences with "speech" in category)
        speech_df = df[df["Category"].str.contains("speech", case=False, na=False)]
        
        if len(speech_df) == 0:
            st.error("❌ No speech sentences found! Please add sentences with 'speech sentence' in the Category column.")
            return
        
        # Select random sentences
        num_to_select = min(num_sentences, len(speech_df))
        selected_sentences = speech_df.sample(num_to_select)
        
        st.session_state.current_speech = selected_sentences.to_dict('records')
    
    # Generate speech button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎲 Generate New Speech", key="generate_speech", help="Create a new random speech"):
            generate_speech()
    
    # Display current speech
    if st.session_state.current_speech:
        st.markdown("""
            <div class="speech-card">
                <h3 style="text-align: center; color: #2c3e50; font-family: 'Inter', sans-serif; font-weight: 700; margin-bottom: 2rem;">
                    📖 Your Chinese Speech
                </h3>
            </div>
        """, unsafe_allow_html=True)
        
        # Display all sentences
        for i, sentence in enumerate(st.session_state.current_speech):
            # Color scheme for speech sentences
            colors = ["#ff6b6b", "#4ecdc4", "#45b7d1", "#f093fb", "#ffa726", "#66bb6a", "#ab47bc", "#26c6da"]
            color = colors[i % len(colors)]
            
            st.markdown(f"""
                <div class="speech-sentence" style="border-left-color: {color};">
                    <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 1rem;">
                        <span style="background: {color}; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem; font-weight: 600;">
                            Sentence {i+1}
                        </span>
                    </div>
                    <div class="speech-chinese">{sentence["Traditional Chinese Word"]}</div>
                    <div class="speech-english">{sentence["English Word"]}</div>
                    {f'<div class="speech-pinyin">{sentence["Pinyin"]}</div>' if include_pinyin else ''}
                </div>
            """, unsafe_allow_html=True)
        
        # Play complete speech button
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔊 Play Complete Speech", key="play_complete_speech", help="Listen to the entire speech"):
                try:
                    # Combine all Chinese sentences
                    chinese_text = " ... ".join([sentence["Traditional Chinese Word"] for sentence in st.session_state.current_speech])
                    
                    with st.spinner("🎵 Generating complete speech audio..."):
                        # Create TTS with appropriate speed
                        tts = gTTS(text=chinese_text, lang='zh-tw', slow=(speech_speed == "slow"))
                        mp3_fp = BytesIO()
                        tts.write_to_fp(mp3_fp)
                        mp3_fp.seek(0)
                        b64 = base64.b64encode(mp3_fp.read()).decode()
                        
                        st.markdown(f"""
                            <div style="text-align: center; margin: 2rem 0;">
                                <div style="background: linear-gradient(45deg, #4facfe, #00f2fe); color: white; padding: 2rem 3rem; border-radius: 25px; display: inline-block; box-shadow: 0 15px 40px rgba(79, 172, 254, 0.4); animation: pulse 2s infinite;">
                                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎵</div>
                                    <div style="font-size: 1.3rem; font-weight: 700;">Playing Complete Speech</div>
                                    <div style="font-size: 1rem; opacity: 0.9; margin-top: 0.5rem;">{len(st.session_state.current_speech)} sentences • {speech_speed} speed</div>
                                </div>
                            </div>
                            <audio autoplay="true" controls style="width: 100%; margin: 1rem 0;">
                                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                                Your browser does not support the audio element.
                            </audio>
                        """, unsafe_allow_html=True)
                        
                        st.success("🎉 Speech audio generated successfully! Use the audio controls above to replay.")
                        
                except Exception as e:
                    st.error(f"❌ Error generating speech audio: {str(e)}")
        
        # Individual sentence audio buttons
        st.markdown("""
            <div style="text-align: center; margin: 2rem 0;">
                <h4 style="color: #2c3e50; font-family: 'Inter', sans-serif; font-weight: 600; margin-bottom: 1rem;">
                    🎧 Play Individual Sentences
                </h4>
            </div>
        """, unsafe_allow_html=True)
        
        # Create columns for individual sentence buttons
        cols = st.columns(min(len(st.session_state.current_speech), 4))
        
        for i, sentence in enumerate(st.session_state.current_speech):
            col_index = i % len(cols)
            with cols[col_index]:
                if st.button(f"🔊 Sentence {i+1}", key=f"play_sentence_{i}", help=f"Play: {sentence['English Word']}"):
                    try:
                        tts = gTTS(text=sentence["Traditional Chinese Word"], lang='zh-tw', slow=(speech_speed == "slow"))
                        mp3_fp = BytesIO()
                        tts.write_to_fp(mp3_fp)
                        mp3_fp.seek(0)
                        b64 = base64.b64encode(mp3_fp.read()).decode()
                        
                        st.markdown(f"""
                            <div style="text-align: center; margin: 1rem 0;">
                                <div style="background: linear-gradient(45deg, #ff6b6b, #ffa726); color: white; padding: 1rem 2rem; border-radius: 20px; display: inline-block; box-shadow: 0 10px 25px rgba(255, 107, 107, 0.3);">
                                    🎵 Playing: <strong>{sentence["Traditional Chinese Word"]}</strong>
                                </div>
                            </div>
                            <audio autoplay="true">
                                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                            </audio>
                        """, unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(f"❌ Error playing sentence {i+1}: {str(e)}")
        
        # Speech practice tips
        st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(139, 195, 74, 0.1)); border: 2px solid #4caf50; border-radius: 20px; padding: 2rem; margin: 2rem 0;">
                <h4 style="color: #2e7d32; font-family: 'Inter', sans-serif; font-weight: 700; margin-bottom: 1.5rem; text-align: center;">💡 Speech Practice Tips</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
                    <div style="text-align: center;">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">👂</div>
                        <strong>Listen Carefully</strong><br>
                        <small style="color: #7f8c8d;">Pay attention to tone and pronunciation</small>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔄</div>
                        <strong>Repeat Along</strong><br>
                        <small style="color: #7f8c8d;">Try to speak along with the audio</small>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">📝</div>
                        <strong>Take Notes</strong><br>
                        <small style="color: #7f8c8d;">Write down new words and phrases</small>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    else:
        # No speech generated yet
        st.markdown("""
            <div style="text-align: center; padding: 4rem; background: rgba(255,255,255,0.9); border-radius: 25px; margin: 2rem 0;">
                <div style="font-size: 5rem; margin-bottom: 1rem;">🎤</div>
                <h3 style="color: #2c3e50; font-family: 'Inter', sans-serif; font-weight: 700;">Ready for Speech Practice?</h3>
                <p style="color: #7f8c8d; font-family: 'Inter', sans-serif; margin: 1.5rem 0; font-size: 1.1rem;">
                    Click "Generate New Speech" to create a randomized Chinese speech for listening practice!
                </p>
                <div style="margin-top: 2rem;">
                    <span style="background: linear-gradient(45deg, #4facfe, #00f2fe); color: white; padding: 1rem 2rem; border-radius: 25px; font-weight: 600; font-size: 1.1rem;">
                        🌟 Perfect for improving your Chinese listening comprehension!
                    </span>
                </div>
            </div>
        """, unsafe_allow_html=True)

# Quiz Mode
elif st.session_state.quiz_active:
    st.markdown("""
        <div class="quiz-card">
            <h2 style="text-align: center; color: #2c3e50; font-family: 'Inter', sans-serif; font-weight: 800; margin-bottom: 2rem;">
                🧠 Chinese Word Quiz Challenge
            </h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Quiz settings
    col1, col2 = st.columns(2)
    
    with col1:
        quiz_category = st.selectbox(
            "🎯 Quiz Category", 
            ["All"] + sorted(df["Category"].unique().tolist()),
            key="quiz_category_select",
            help="Choose category for focused learning"
        )
        st.session_state.quiz_category = quiz_category
    
    with col2:
        quiz_difficulty = st.selectbox(
            "⚡ Difficulty Level",
            ["Easy", "Medium", "Hard"],
            key="quiz_difficulty_select",
            help="Easy: 2 options, Medium: 3 options, Hard: 4 options"
        )
        st.session_state.quiz_difficulty = quiz_difficulty
    
    # Difficulty badge
    difficulty_class = f"difficulty-{quiz_difficulty.lower()}"
    st.markdown(f"""
        <div style="text-align: center; margin: 1rem 0;">
            <span class="difficulty-badge {difficulty_class}">
                {quiz_difficulty} Level - {2 if quiz_difficulty == 'Easy' else 3 if quiz_difficulty == 'Medium' else 4} Options
            </span>
        </div>
    """, unsafe_allow_html=True)
    
    # Score display
    if st.session_state.quiz_total > 0:
        st.markdown(f"""
            <div class="score-display">
                🏆 Score: {st.session_state.quiz_score} / {st.session_state.quiz_total} ({accuracy}% Accuracy)
            </div>
        """, unsafe_allow_html=True)
    
    def generate_quiz_question():
        # Filter dataframe based on category (exclude speech sentences from quiz)
        quiz_df = df[~df["Category"].str.contains("speech", case=False, na=False)].copy()
        if st.session_state.quiz_category != "All":
            quiz_df = quiz_df[quiz_df["Category"] == st.session_state.quiz_category]
        
        if len(quiz_df) == 0:
            return None
        
        # Select correct answer
        correct_word = quiz_df.sample(1).iloc[0]
        st.session_state.current_question = correct_word
        st.session_state.correct_answer = correct_word["English Word"]
        
        # Generate wrong options
        num_options = 2 if st.session_state.quiz_difficulty == "Easy" else 3 if st.session_state.quiz_difficulty == "Medium" else 4
        other_words = quiz_df[quiz_df["English Word"] != correct_word["English Word"]].sample(min(num_options - 1, len(quiz_df) - 1))
        
        # Create options list
        options = [correct_word["English Word"]] + other_words["English Word"].tolist()
        random.shuffle(options)
        st.session_state.quiz_options = options
        st.session_state.quiz_answered = False
    
    # Generate new question button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎲 New Question", key="new_question", help="Generate a new quiz question"):
            generate_quiz_question()
    
    # Display current question
    if st.session_state.current_question is not None:
        question = st.session_state.current_question
        
        # Display Chinese word and play audio
        st.markdown(f"""
            <div class="quiz-card">
                <div style="text-align: center;">
                    <h3 style="color: #7f8c8d; font-family: 'Inter', sans-serif; font-weight: 500; margin-bottom: 1rem;">
                        🎧 Listen and select the correct English translation:
                    </h3>
                    <div class="quiz-chinese-word">{question["Traditional Chinese Word"]}</div>
                    <div style="font-size: 1.5rem; color: #7f8c8d; font-style: italic; margin-bottom: 2rem;">
                        {question["Pinyin"]}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Auto-play audio when question is generated
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔊 Play Audio Again", key="quiz_audio", help="Listen to the pronunciation"):
                try:
                    tts = gTTS(text=question["Traditional Chinese Word"], lang='zh-tw')
                    mp3_fp = BytesIO()
                    tts.write_to_fp(mp3_fp)
                    mp3_fp.seek(0)
                    b64 = base64.b64encode(mp3_fp.read()).decode()
                    
                    st.markdown(f"""
                        <div style="text-align: center; margin: 1rem 0;">
                            <div style="background: linear-gradient(45deg, #4facfe, #00f2fe); color: white; padding: 1rem 2rem; border-radius: 25px; display: inline-block; box-shadow: 0 10px 30px rgba(79, 172, 254, 0.3);">
                                🎵 Playing: <strong>{question["Traditional Chinese Word"]}</strong>
                            </div>
                        </div>
                        <audio autoplay="true">
                            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                        </audio>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"❌ Error generating audio: {str(e)}")
        
        # Display options
        st.markdown('<div style="margin: 2rem 0;">', unsafe_allow_html=True)
        
        # Create columns for options
        if len(st.session_state.quiz_options) == 2:
            cols = st.columns(2)
        elif len(st.session_state.quiz_options) == 3:
            cols = st.columns(3)
        else:
            cols = st.columns(2)
        
        for i, option in enumerate(st.session_state.quiz_options):
            col_index = i if len(st.session_state.quiz_options) <= 3 else i % 2
            with cols[col_index]:
                option_key = f"option_{i}_{option}"
                
                if st.button(
                    option, 
                    key=option_key,
                    help=f"Select {option} as your answer",
                    disabled=st.session_state.quiz_answered
                ):
                    st.session_state.quiz_answered = True
                    st.session_state.quiz_total += 1
                    
                    if option == st.session_state.correct_answer:
                        st.session_state.quiz_score += 1
                        st.success("🎉 Correct! Well done!")
                        st.balloons()
                        
                        # Show word details
                        st.markdown(f"""
                            <div style="background: linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(139, 195, 74, 0.1)); border: 2px solid #4caf50; border-radius: 15px; padding: 1.5rem; margin: 1rem 0;">
                                <h4 style="color: #2e7d32; font-family: 'Inter', sans-serif; margin-bottom: 1rem;">✅ Correct Answer Details:</h4>
                                <p><strong>English:</strong> {question["English Word"]}</p>
                                <p><strong>Chinese:</strong> {question["Traditional Chinese Word"]}</p>
                                <p><strong>Pinyin:</strong> {question["Pinyin"]}</p>
                                <p><strong>Category:</strong> {question["Category"]}</p>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(f"❌ Incorrect! The correct answer is: {st.session_state.correct_answer}")
                        
                        # Show correct answer details
                        st.markdown(f"""
                            <div style="background: linear-gradient(135deg, rgba(244, 67, 54, 0.1), rgba(255, 87, 34, 0.1)); border: 2px solid #f44336; border-radius: 15px; padding: 1.5rem; margin: 1rem 0;">
                                <h4 style="color: #c62828; font-family: 'Inter', sans-serif; margin-bottom: 1rem;">❌ Correct Answer:</h4>
                                <p><strong>English:</strong> {question["English Word"]}</p>
                                <p><strong>Chinese:</strong> {question["Traditional Chinese Word"]}</p>
                                <p><strong>Pinyin:</strong> {question["Pinyin"]}</p>
                                <p><strong>Category:</strong> {question["Category"]}</p>
                            </div>
                        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Show quiz progress
        if st.session_state.quiz_total > 0:
            progress_percentage = (st.session_state.quiz_score / st.session_state.quiz_total) * 100
            st.markdown(f"""
                <div style="margin: 2rem 0; text-align: center;">
                    <div style="background: rgba(255,255,255,0.9); border-radius: 15px; padding: 1rem; display: inline-block; box-shadow: 0 8px 25px rgba(0,0,0,0.1);">
                        <strong>Quiz Progress:</strong> {st.session_state.quiz_score}/{st.session_state.quiz_total} 
                        <span style="color: {'#4caf50' if progress_percentage >= 70 else '#ff9800' if progress_percentage >= 50 else '#f44336'};">
                            ({progress_percentage:.1f}%)
                        </span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    else:
        # No question loaded, show start message
        st.markdown("""
            <div style="text-align: center; padding: 3rem; background: rgba(255,255,255,0.9); border-radius: 20px; margin: 2rem 0;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">🚀</div>
                <h3 style="color: #2c3e50; font-family: 'Inter', sans-serif; font-weight: 600;">Ready to Test Your Knowledge?</h3>
                <p style="color: #7f8c8d; font-family: 'Inter', sans-serif; margin: 1rem 0;">Click "New Question" to start your Chinese learning quiz!</p>
                <div style="margin-top: 2rem;">
                    <span style="background: linear-gradient(45deg, #667eea, #764ba2); color: white; padding: 0.5rem 1.5rem; border-radius: 25px; font-weight: 600;">
                        🎯 Challenge yourself and improve your Chinese vocabulary!
                    </span>
                </div>
            </div>
        """, unsafe_allow_html=True)

# Learning Mode (Dictionary/Browse)
else:
    # Enhanced search and filter section
    st.markdown("""
        <div style="background: rgba(255,255,255,0.9); backdrop-filter: blur(20px); border-radius: 20px; padding: 2rem; margin: 1rem 0; box-shadow: 0 15px 35px rgba(0,0,0,0.1); border: 1px solid rgba(255,255,255,0.3);">
            <h3 style="color: #2c3e50; font-family: 'Inter', sans-serif; font-weight: 700; margin-bottom: 1.5rem; text-align: center;">🔍 Find Your Words</h3>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        category = st.selectbox(
            "📚 Select Category", 
            ["All"] + sorted(df["Category"].unique().tolist()),
            help="Choose a specific category to focus your learning"
        )

    with col2:
        search_word = st.text_input(
            "🔎 Search Words", 
            placeholder="Search in English, Chinese, or Pinyin...",
            help="Type any part of a word to find it instantly"
        )

    # Filter dataframe
    filtered_df = df.copy()
    if category != "All":
        filtered_df = filtered_df[filtered_df["Category"] == category]

    if search_word:
        filtered_df = filtered_df[
            filtered_df["English Word"].str.contains(search_word, case=False, na=False) |
            filtered_df["Traditional Chinese Word"].str.contains(search_word, case=False, na=False) |
            filtered_df["Pinyin"].str.contains(search_word, case=False, na=False)
        ]

    # Results info
    st.markdown(f"""
        <div style="text-align: center; margin: 2rem 0;">
            <span style="background: linear-gradient(45deg, #667eea, #764ba2); color: white; padding: 0.5rem 1.5rem; border-radius: 25px; font-weight: 600; font-family: 'Inter', sans-serif; box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);">
                📖 Showing {len(filtered_df)} words
            </span>
        </div>
    """, unsafe_allow_html=True)

    # Enhanced word cards
    if len(filtered_df) > 0:
        for i, row in filtered_df.iterrows():
            # Color schemes for categories
            color_schemes = {
                "Greetings": ["#ff6b6b", "#ffa726"],
                "Family": ["#4ecdc4", "#45b7d1"],
                "Food": ["#f093fb", "#f5576c"],
                "Numbers": ["#a8e6cf", "#56ab91"],
                "Colors": ["#ff8a80", "#ffab91"],
                "Animals": ["#ce93d8", "#ba68c8"],
                "Time": ["#90caf9", "#42a5f5"],
                "Weather": ["#fff176", "#ffcc02"]
            }
            
            # Special styling for speech sentences
            if "speech" in row["Category"].lower():
                color_schemes[row["Category"]] = ["#4facfe", "#00f2fe"]
            
            category_colors = color_schemes.get(row["Category"], ["#667eea", "#764ba2"])
            
            st.markdown(f"""
                <div class="word-card" style="border-left: 5px solid {category_colors[0]};">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
                        <div style="flex: 1; min-width: 200px;">
                            <div class="english-word">{row["English Word"]}</div>
                            <div class="chinese-word">{row["Traditional Chinese Word"]}</div>
                            <div class="pinyin-word">{row["Pinyin"]}</div>
                            <div style="margin-top: 1rem;">
                                <span class="category-tag" style="background: linear-gradient(45deg, {category_colors[0]}, {category_colors[1]});">
                                    {row["Category"]} {"🎤" if "speech" in row["Category"].lower() else ""}
                                </span>
                            </div>
                        </div>
                        <div style="display: flex; align-items: center;">
            """, unsafe_allow_html=True)
            
            # Enhanced audio button
            if st.button("🔊 Listen", key=f"btn_{i}", help="Click to hear pronunciation"):
                with st.spinner("🎵 Generating audio..."):
                    try:
                        tts = gTTS(text=row["Traditional Chinese Word"], lang='zh-tw')
                        mp3_fp = BytesIO()
                        tts.write_to_fp(mp3_fp)
                        mp3_fp.seek(0)
                        b64 = base64.b64encode(mp3_fp.read()).decode()
                        
                        # Enhanced audio player with visual feedback
                        st.markdown(f"""
                            <div style="text-align: center; margin: 1rem 0;">
                                <div style="background: linear-gradient(45deg, #4facfe, #00f2fe); color: white; padding: 1rem 2rem; border-radius: 25px; display: inline-block; box-shadow: 0 10px 30px rgba(79, 172, 254, 0.3); animation: pulse 2s infinite;">
                                    🎵 Playing: <strong>{row["Traditional Chinese Word"]}</strong>
                                </div>
                            </div>
                            <audio autoplay="true">
                                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                            </audio>
                        """, unsafe_allow_html=True)
                        
                        # Show success message
                        st.success("🎉 Audio played successfully!")
                        
                    except Exception as e:
                        st.error(f"❌ Error generating audio: {str(e)}")
            
            st.markdown("</div></div></div>", unsafe_allow_html=True)

    else:
        # No results found
        st.markdown("""
            <div style="text-align: center; padding: 3rem; background: rgba(255,255,255,0.9); border-radius: 20px; margin: 2rem 0;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">😔</div>
                <h3 style="color: #7f8c8d; font-family: 'Inter', sans-serif; font-weight: 600;">No words found</h3>
                <p style="color: #95a5a6; font-family: 'Inter', sans-serif;">Try adjusting your search or category filter</p>
            </div>
        """, unsafe_allow_html=True)

    

    # Random word of the day feature
    if st.button("🎲 Random Word Challenge", help="Get a random word to practice!"):
        random_word = df.sample(1).iloc[0]
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; border-radius: 25px; padding: 2rem; margin: 2rem 0; text-align: center; box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);">
                <h3 style="margin-bottom: 1rem; font-family: 'Inter', sans-serif;">🌟 Word of the Moment</h3>
                <div style="font-size: 3rem; margin: 1rem 0; font-family: 'Noto Sans TC', sans-serif;">{random_word["Traditional Chinese Word"]}</div>
                <div style="font-size: 1.5rem; margin: 0.5rem 0; opacity: 0.9;">{random_word["English Word"]}</div>
                <div style="font-size: 1.2rem; font-style: italic; opacity: 0.8;">{random_word["Pinyin"]}</div>
                <div style="margin-top: 1rem;">
                    <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.9rem;">
                        {random_word["Category"]}
                    </span>
                </div>
            </div>
        """, unsafe_allow_html=True)

# Footer with additional features
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div style="background: rgba(255,255,255,0.9); backdrop-filter: blur(20px); border-radius: 20px; padding: 2rem; margin: 2rem 0; text-align: center; box-shadow: 0 15px 35px rgba(0,0,0,0.1);">
        <h4 style="color: #2c3e50; font-family: 'Inter', sans-serif; font-weight: 700; margin-bottom: 1rem;">✨ Learning Tips</h4>
        <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 1rem;">
            <div style="flex: 1; min-width: 200px; padding: 1rem; background: linear-gradient(45deg, rgba(255,107,107,0.1), rgba(255,167,38,0.1)); border-radius: 15px;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎯</div>
                <strong>Practice Daily</strong><br>
                <small style="color: #7f8c8d;">Consistency is key to mastering Chinese</small>
            </div>
            <div style="flex: 1; min-width: 200px; padding: 1rem; background: linear-gradient(45deg, rgba(78,205,196,0.1), rgba(69,183,209,0.1)); border-radius: 15px;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🗣️</div>
                <strong>Listen & Repeat</strong><br>
                <small style="color: #7f8c8d;">Use the audio feature to perfect pronunciation</small>
            </div>
            <div style="flex: 1; min-width: 200px; padding: 1rem; background: linear-gradient(45deg, rgba(108,92,231,0.1), rgba(116,75,162,0.1)); border-radius: 15px;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📝</div>
                <strong>Take Quizzes</strong><br>
                <small style="color: #7f8c8d;">Test your knowledge with interactive quizzes</small>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Reset quiz score button (in sidebar or at bottom)
if st.session_state.quiz_total > 0:
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Reset Quiz Progress", help="Clear your quiz history and start fresh"):
            st.session_state.quiz_score = 0
            st.session_state.quiz_total = 0
            st.session_state.current_question = None
            st.session_state.quiz_answered = False
            st.success("✅ Quiz progress has been reset!")
            time.sleep(1)
            st.rerun()

# Progressive loading animation for better UX
time.sleep(0.1)  # Small delay for smoother experience
