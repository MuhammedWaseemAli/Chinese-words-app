import streamlit as st
import pandas as pd
from gtts import gTTS
import base64
from io import BytesIO
import random
from pathlib import Path

EXCEL_FILE = Path(__file__).parent / "chinese_learning_streamlit (1).xlsx"

@st.cache_data
def load_data(path):
    return pd.read_excel(path)

df = load_data(EXCEL_FILE)

# ── Session state ──────────────────────────────────────────────────────────────
defaults = {
    'mode': 'learn',
    'current_question': None,
    'quiz_options': [],
    'correct_answer': '',
    'quiz_score': 0,
    'quiz_total': 0,
    'quiz_answered': False,
    'current_speech': [],
    'speech_sentences': 5,
    'speech_speed': 'normal',
    'speech_show_pinyin': True,
    'play_audio_text': None,   # text to play this render cycle
    'play_audio_slow': False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Simple CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.word-card {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 0.75rem;
    background: #fafafa;
}
.chinese { font-size: 2rem; font-weight: bold; }
.pinyin  { font-size: 1rem; color: #666; font-style: italic; }
.tag     { display:inline-block; background:#eee; border-radius:12px;
           padding:2px 10px; font-size:0.8rem; margin-top:4px; }
.score-bar { background:#f0f0f0; border-radius:8px; padding:0.5rem 1rem;
             margin-bottom:1rem; font-weight:bold; }
</style>
""", unsafe_allow_html=True)

# ── Audio helpers ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def build_audio_b64(text: str, slow: bool) -> str:
    """Build base64 MP3 (cached so same word is not re-generated every click)."""
    tts = gTTS(text=text, lang='zh-tw', slow=slow)
    buf = BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()

def render_audio(slot, text: str, slow: bool = False):
    """Render an autoplay audio player into the given st.empty() slot."""
    try:
        b64 = build_audio_b64(text, slow)
        slot.markdown(
            f'<audio autoplay controls style="width:100%;margin-top:8px">'
            f'<source src="data:audio/mp3;base64,{b64}" type="audio/mp3">'
            f'</audio>',
            unsafe_allow_html=True,
        )
    except Exception as e:
        slot.error(f"Audio error: {e}")

def request_audio(text: str, slow: bool = False):
    """Queue audio for the next render pass, then rerun."""
    st.session_state.play_audio_text = text
    st.session_state.play_audio_slow = slow
    st.rerun()

# ── Title & nav ────────────────────────────────────────────────────────────────
st.title("🇹🇼 Learn Traditional Chinese")

c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("📚 Learn"):
        st.session_state.mode = 'learn'
        st.session_state.play_audio_text = None
with c2:
    if st.button("🧠 Quiz"):
        st.session_state.mode = 'quiz'
        st.session_state.play_audio_text = None
with c3:
    if st.button("🎤 Speech"):
        st.session_state.mode = 'speech'
        st.session_state.play_audio_text = None
with c4:
    if st.button("📊 Progress"):
        st.session_state.mode = 'progress'
        st.session_state.play_audio_text = None

st.divider()

# ── Stats row ──────────────────────────────────────────────────────────────────
total_words = len(df)
categories  = df["Category"].nunique()
speech_rows = len(df[df["Category"].str.contains("speech", case=False, na=False)])
accuracy    = (
    round(st.session_state.quiz_score / st.session_state.quiz_total * 100, 1)
    if st.session_state.quiz_total > 0 else 0.0
)

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Total Words",      total_words)
m2.metric("Categories",       categories)
m3.metric("Speech Sentences", speech_rows)
m4.metric("Quiz Attempts",    st.session_state.quiz_total)
m5.metric("Accuracy",         f"{accuracy}%")

st.divider()

# ── Audio slot (rendered once, near top of content) ───────────────────────────
# We create the slot here so it always appears in the same DOM position.
audio_slot = st.empty()
if st.session_state.play_audio_text:
    render_audio(audio_slot, st.session_state.play_audio_text, st.session_state.play_audio_slow)
    # Clear so it doesn't re-play on the next unrelated rerun
    st.session_state.play_audio_text = None
    st.session_state.play_audio_slow = False

# ══════════════════════════════════════════════════════════════════════════════
# 📚 LEARN MODE
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.mode == 'learn':
    st.subheader("📚 Browse & Learn")

    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox("Category", ["All"] + sorted(df["Category"].unique().tolist()))
    with col2:
        search = st.text_input("Search (English / Chinese / Pinyin)", placeholder="Type to search…")

    filtered = df.copy()
    if category != "All":
        filtered = filtered[filtered["Category"] == category]
    if search:
        mask = (
            filtered["English Word"].str.contains(search, case=False, na=False) |
            filtered["Traditional Chinese Word"].str.contains(search, case=False, na=False) |
            filtered["Pinyin"].str.contains(search, case=False, na=False)
        )
        filtered = filtered[mask]

    st.caption(f"Showing {len(filtered)} words")

    if filtered.empty:
        st.info("No words match your filter.")
    else:
        for i, row in filtered.iterrows():
            st.markdown(f"""
            <div class="word-card">
              <div class="chinese">{row['Traditional Chinese Word']}</div>
              <div><strong>{row['English Word']}</strong></div>
              <div class="pinyin">{row['Pinyin']}</div>
              <div class="tag">{row['Category']}</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🔊 Listen", key=f"learn_audio_{i}"):
                request_audio(row["Traditional Chinese Word"])

    st.divider()
    if st.button("🎲 Random Word"):
        rw = df.sample(1).iloc[0]
        st.info(
            f"**{rw['Traditional Chinese Word']}** — {rw['English Word']} "
            f"*({rw['Pinyin']})*  \nCategory: {rw['Category']}"
        )
        request_audio(rw["Traditional Chinese Word"])

# ══════════════════════════════════════════════════════════════════════════════
# 🧠 QUIZ MODE
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.mode == 'quiz':
    st.subheader("🧠 Quiz Mode")

    if st.session_state.quiz_total > 0:
        st.markdown(
            f'<div class="score-bar">🏆 Score: {st.session_state.quiz_score} / '
            f'{st.session_state.quiz_total} &nbsp;({accuracy}%)</div>',
            unsafe_allow_html=True,
        )

    col1, col2 = st.columns(2)
    with col1:
        quiz_category = st.selectbox(
            "Category", ["All"] + sorted(df["Category"].unique().tolist()), key="qcat"
        )
    with col2:
        quiz_difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], key="qdiff")

    num_opts = {"Easy": 2, "Medium": 3, "Hard": 4}[quiz_difficulty]

    def generate_question():
        qdf = df[~df["Category"].str.contains("speech", case=False, na=False)].copy()
        if quiz_category != "All":
            qdf = qdf[qdf["Category"] == quiz_category]
        if qdf.empty:
            st.warning("No words in this category.")
            return
        correct = qdf.sample(1).iloc[0]
        others  = qdf[qdf["English Word"] != correct["English Word"]].sample(
            min(num_opts - 1, len(qdf) - 1)
        )
        opts = [correct["English Word"]] + others["English Word"].tolist()
        random.shuffle(opts)
        st.session_state.current_question = correct.to_dict()
        st.session_state.correct_answer   = correct["English Word"]
        st.session_state.quiz_options     = opts
        st.session_state.quiz_answered    = False
        # Auto-play the new word
        request_audio(correct["Traditional Chinese Word"])

    if st.button("🎲 New Question"):
        generate_question()

    q = st.session_state.current_question
    if q:
        st.markdown("### What is the meaning of:")
        st.markdown(
            f"<div class='chinese' style='text-align:center;font-size:3rem'>"
            f"{q['Traditional Chinese Word']}</div>",
            unsafe_allow_html=True,
        )
        st.caption(f"Pinyin: {q['Pinyin']}")

        if st.button("🔊 Play Again", key="quiz_play"):
            request_audio(q["Traditional Chinese Word"])

        st.markdown("**Choose the correct translation:**")

        n = len(st.session_state.quiz_options)
        opt_cols = st.columns(n if n <= 3 else 2)

        for idx, opt in enumerate(st.session_state.quiz_options):
            with opt_cols[idx % len(opt_cols)]:
                if st.button(opt, key=f"opt_{idx}_{opt}", disabled=st.session_state.quiz_answered):
                    st.session_state.quiz_answered = True
                    st.session_state.quiz_total   += 1
                    if opt == st.session_state.correct_answer:
                        st.session_state.quiz_score += 1
                        st.success("✅ Correct!")
                        st.balloons()
                    else:
                        st.error(f"❌ Wrong! Correct answer: **{st.session_state.correct_answer}**")

        if st.session_state.quiz_answered:
            st.info(
                f"**{q['English Word']}** = {q['Traditional Chinese Word']} "
                f"({q['Pinyin']}) — {q['Category']}"
            )
    else:
        st.info("Press **New Question** to start!")

    st.divider()
    if st.session_state.quiz_total > 0:
        if st.button("🔄 Reset Quiz Score"):
            st.session_state.quiz_score       = 0
            st.session_state.quiz_total       = 0
            st.session_state.current_question = None
            st.session_state.quiz_answered    = False
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# 🎤 SPEECH PRACTICE
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.mode == 'speech':
    st.subheader("🎤 Speech Practice")

    col1, col2, col3 = st.columns(3)
    with col1:
        num_sent = st.slider("Sentences", 3, 15, st.session_state.speech_sentences)
        st.session_state.speech_sentences = num_sent
    with col2:
        speed = st.selectbox(
            "Speed", ["slow", "normal"],
            index=["slow", "normal"].index(st.session_state.speech_speed)
        )
        st.session_state.speech_speed = speed
    with col3:
        show_py = st.checkbox("Show Pinyin", value=st.session_state.speech_show_pinyin)
        st.session_state.speech_show_pinyin = show_py

    if st.button("🎲 Generate Speech"):
        speech_df = df[df["Category"].str.contains("speech", case=False, na=False)]
        if speech_df.empty:
            st.error("No speech sentences found. Category must contain the word 'speech'.")
        else:
            selected = speech_df.sample(min(num_sent, len(speech_df)))
            st.session_state.current_speech = selected.to_dict("records")

    speech = st.session_state.current_speech
    if speech:
        for i, s in enumerate(speech):
            st.markdown(f"""
            <div class="word-card">
              <strong>Sentence {i+1}</strong><br>
              <div class="chinese">{s['Traditional Chinese Word']}</div>
              <div>{s['English Word']}</div>
              {"<div class='pinyin'>" + s['Pinyin'] + "</div>" if show_py else ""}
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"🔊 Play sentence {i+1}", key=f"sp_btn_{i}"):
                request_audio(s["Traditional Chinese Word"], slow=(speed == "slow"))

        st.divider()
        if st.button("🔊 Play Full Speech"):
            full_text = " ... ".join(s["Traditional Chinese Word"] for s in speech)
            request_audio(full_text, slow=(speed == "slow"))
    else:
        st.info("Press **Generate Speech** to create a random speech set.")

# ══════════════════════════════════════════════════════════════════════════════
# 📊 PROGRESS
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.mode == 'progress':
    st.subheader("📊 Your Progress")

    st.metric("Quiz Attempts",   st.session_state.quiz_total)
    st.metric("Correct Answers", st.session_state.quiz_score)
    st.metric("Accuracy",        f"{accuracy}%")

    if st.session_state.quiz_total > 0:
        st.progress(st.session_state.quiz_score / st.session_state.quiz_total)
        if st.button("🔄 Reset All Progress"):
            st.session_state.quiz_score       = 0
            st.session_state.quiz_total       = 0
            st.session_state.current_question = None
            st.session_state.quiz_answered    = False
            st.success("Progress reset!")
            st.rerun()
    else:
        st.info("No quiz attempts yet. Go to **Quiz** mode to start!")

    st.divider()
    st.subheader("📋 Words per Category")
    cat_counts = df.groupby("Category").size().reset_index(name="Count")
    st.dataframe(cat_counts, use_container_width=True)
