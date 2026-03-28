import streamlit as st
import pandas as pd
import jieba
import requests
import re
import time
import random
import base64
from io import BytesIO
from pathlib import Path
from gtts import gTTS

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Traditional Chinese Learning Hub", page_icon="🇹🇼", layout="wide")

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
    'play_audio_text': None,
    'play_audio_slow': False,
    'analyzer': None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.word-card {
    border:1px solid #ddd; border-radius:8px;
    padding:1rem; margin-bottom:0.75rem; background:#fafafa;
}
.chinese  { font-size:2rem; font-weight:bold; }
.pinyin   { font-size:1rem; color:#666; font-style:italic; }
.tag      { display:inline-block; background:#eee; border-radius:12px;
            padding:2px 10px; font-size:0.8rem; margin-top:4px; }
.score-bar{ background:#f0f0f0; border-radius:8px; padding:0.5rem 1rem;
            margin-bottom:1rem; font-weight:bold; }
.big-font    { font-size:42px !important; font-weight:bold; color:#1f77b4; }
.medium-font { font-size:32px !important; font-weight:bold; }
.chinese-char{
    font-size:48px !important; font-weight:bold; color:#1f77b4;
    font-family:'SimHei','Microsoft YaHei','PingFang SC',sans-serif;
}
.chinese-word{
    font-size:44px !important; font-weight:bold; color:#d62728;
    font-family:'SimHei','Microsoft YaHei','PingFang SC',sans-serif;
}
.meaning      { font-size:26px !important; color:#2ca02c; font-weight:500; margin:10px 0; }
.ana-pinyin   { font-size:24px !important; color:#ff7f0e; font-style:italic; font-weight:bold; margin:8px 0; }
.sentence-box {
    border:4px solid #9b59b6; border-radius:15px; padding:35px; margin:25px 0;
    background:linear-gradient(135deg,#e8f4fd,#c7e0f4);
    box-shadow:0 6px 12px rgba(0,0,0,0.15);
}
.sentence-text{
    font-size:40px !important; font-weight:bold; color:#2c3e50;
    text-align:center; margin:15px 0;
    font-family:'SimHei','Microsoft YaHei','PingFang SC',sans-serif;
}
.sentence-pinyin{
    font-size:28px !important; color:#e74c3c; font-style:italic; font-weight:bold;
    text-align:center; margin:15px 0; background:#fff3cd; padding:10px; border-radius:8px;
}
.sentence-meaning{ font-size:28px !important; color:#27ae60; font-weight:600; text-align:center; margin:15px 0; }
.analysis-box{
    border:3px solid #e0e0e0; border-radius:15px; padding:30px; margin:20px 0;
    background:linear-gradient(135deg,#f5f7fa,#c3cfe2);
    box-shadow:0 4px 6px rgba(0,0,0,0.1);
}
.character-box{
    border:3px solid #1f77b4; border-radius:12px; padding:25px; margin:12px;
    background:linear-gradient(135deg,#667eea,#764ba2);
    color:white; text-align:center; min-width:160px; min-height:140px;
    display:flex; flex-direction:column; justify-content:center;
    box-shadow:0 4px 8px rgba(0,0,0,0.2);
}
.word-box{
    border:3px solid #d62728; border-radius:12px; padding:30px; margin:20px 0;
    background:linear-gradient(135deg,#ffeaa7,#fab1a0);
    box-shadow:0 4px 8px rgba(0,0,0,0.1);
}
.combination-text{
    font-size:28px !important; font-weight:bold;
    background:linear-gradient(45deg,#667eea,#764ba2);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}
.pinyin-highlight{
    background:linear-gradient(135deg,#ff9a9e,#fecfef);
    padding:8px 12px; border-radius:6px; font-size:22px !important; font-weight:bold; color:#333;
}
.success-badge{ background:#28a745; color:white; padding:4px 8px; border-radius:4px; font-size:12px; margin-left:10px; }
.error-badge  { background:#dc3545; color:white; padding:4px 8px; border-radius:4px; font-size:12px; margin-left:10px; }
.study-map-title{ font-size:2.2rem; font-weight:800; color:#2c3e50; text-align:center; margin-bottom:0.3rem; }
.study-map-subtitle{ text-align:center; color:#666; font-size:1.1rem; margin-bottom:2rem; }
.para-card{
    border:2px solid #764ba2; border-radius:16px; padding:1.8rem; margin-bottom:2rem;
    background:#faf7ff; box-shadow:0 4px 12px rgba(118,75,162,0.12);
}
.para-card-title{ font-size:1rem; font-weight:700; color:#764ba2; text-transform:uppercase; letter-spacing:1px; margin-bottom:1rem; }
.para-chinese{
    font-size:1.45rem; line-height:2.2rem; color:#1a1a2e;
    font-family:'SimHei','Microsoft YaHei','PingFang SC',sans-serif; margin-bottom:0.8rem;
}
.para-english{ font-size:1.1rem; color:#444; line-height:1.8rem; margin-bottom:0.8rem; }
.para-pinyin { font-size:1rem; color:#e67e22; font-style:italic; line-height:1.8rem; }
.line-card{
    border-left:5px solid #4ecdc4; border-radius:0 12px 12px 0;
    padding:1rem 1.2rem; margin:0.8rem 0; background:#f0fffe;
}
.line-chinese{
    font-size:1.4rem; font-weight:bold; color:#1a1a2e;
    font-family:'SimHei','Microsoft YaHei','PingFang SC',sans-serif;
}
ruby{ display:inline-flex; flex-direction:column-reverse; align-items:center; }
ruby rt{ font-size:0.65em; color:#e74c3c; font-style:italic; font-weight:bold; line-height:1.2; text-align:center; }
.ruby-wrap{
    font-size:1.5rem; line-height:3rem;
    font-family:'SimHei','Microsoft YaHei','PingFang SC',sans-serif;
}
.word-chip{
    display:inline-block; border:2px solid #9b59b6; border-radius:10px;
    padding:0.5rem 0.8rem; margin:0.3rem; background:white;
    text-align:center; min-width:80px; vertical-align:top;
}
.chip-chinese{ font-size:1.3rem; font-weight:bold; color:#2c3e50; }
.chip-pinyin { font-size:0.75rem; color:#e74c3c; font-style:italic; }
.chip-english{ font-size:0.75rem; color:#27ae60; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Pinyin / Translation engine
# ══════════════════════════════════════════════════════════════════════════════
class ComprehensivePinyinConverter:
    def __init__(self):
        self.cache = {}
        self.translation_cache = {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7'
        })
        self.pinyin_dict = self._load_dict()

    def _load_dict(self):
        return {
            '的':'de','一':'yī','是':'shì','不':'bù','了':'le','人':'rén','我':'wǒ',
            '在':'zài','有':'yǒu','他':'tā','这':'zhè','個':'gè','个':'gè','们':'men',
            '中':'zhōng','来':'lái','來':'lái','上':'shàng','大':'dà','为':'wéi',
            '為':'wéi','和':'hé','国':'guó','國':'guó','地':'dì','到':'dào',
            '以':'yǐ','说':'shuō','說':'shuō','时':'shí','時':'shí','要':'yào',
            '就':'jiù','出':'chū','会':'huì','會':'huì','可':'kě','也':'yě',
            '你':'nǐ','对':'duì','對':'duì','生':'shēng','能':'néng','而':'ér',
            '子':'zi','那':'nà','得':'dé','于':'yú','於':'yú','着':'zhe',
            '著':'zhe','下':'xià','自':'zì','之':'zhī','年':'nián','过':'guò',
            '過':'guò','发':'fā','發':'fā','后':'hòu','後':'hòu','作':'zuò',
            '里':'lǐ','裡':'lǐ','用':'yòng','道':'dào','行':'xíng','所':'suǒ',
            '然':'rán','家':'jiā','种':'zhǒng','種':'zhǒng','事':'shì','方':'fāng',
            '多':'duō','经':'jīng','經':'jīng','么':'me','麼':'me','去':'qù',
            '法':'fǎ','学':'xué','學':'xué','如':'rú','她':'tā','看':'kàn',
            '天':'tiān','样':'yàng','樣':'yàng','其':'qí','新':'xīn','手':'shǒu',
            '又':'yòu','当':'dāng','當':'dāng','没':'méi','沒':'méi','动':'dòng',
            '動':'dòng','面':'miàn','起':'qǐ','老':'lǎo','公':'gōng','高':'gāo',
            '想':'xiǎng','小':'xiǎo','从':'cóng','從':'cóng','开':'kāi','開':'kāi',
            '头':'tóu','頭':'tóu','等':'děng','长':'cháng','長':'cháng','水':'shuǐ',
            '几':'jǐ','幾':'jǐ','民':'mín','现':'xiàn','現':'xiàn','山':'shān',
            '分':'fēn','望':'wàng','第':'dì','位':'wèi','比':'bǐ','路':'lù',
            '神':'shén','太':'tài','机':'jī','機':'jī','安':'ān',
            '适':'shì','適':'shì','合':'hé','工':'gōng','班':'bān','需':'xū',
            '帮':'bāng','幫':'bāng','助':'zhù','总':'zǒng','總':'zǒng','统':'tǒng',
            '統':'tǒng','府':'fǔ','爱':'ài','愛':'ài','北':'běi','京':'jīng',
            '谢':'xiè','謝':'xiè','好':'hǎo','世':'shì','界':'jiè','今':'jīn',
            '气':'qì','氣':'qì','很':'hěn','忙':'máng','碌':'lù','汉':'hàn',
            '漢':'hàn','语':'yǔ','語':'yǔ','习':'xí','習':'xí','听':'tīng',
            '聽':'tīng','吃':'chī','喝':'hē','走':'zǒu','跑':'pǎo','站':'zhàn',
            '坐':'zuò','睡':'shuì','书':'shū','書':'shū','电':'diàn','電':'diàn',
            '话':'huà','話':'huà','买':'mǎi','買':'mǎi','卖':'mài','賣':'mài',
            '钱':'qián','錢':'qián','车':'chē','車':'chē','住':'zhù','请':'qǐng',
            '請':'qǐng','什':'shén','哪':'nǎ','怎':'zěn','少':'shǎo','旧':'jiù',
            '舊':'jiù','短':'duǎn','低':'dī','快':'kuài','慢':'màn','眼':'yǎn',
            '耳':'ěr','口':'kǒu','鼻':'bí','心':'xīn','脚':'jiǎo','腳':'jiǎo',
            '文':'wén','化':'huà','教':'jiào','育':'yù','音':'yīn','乐':'lè',
            '樂':'lè','影':'yǐng','院':'yuàn','医':'yī','醫':'yī','护':'hù',
            '護':'hù','士':'shì','银':'yín','銀':'yín','店':'diàn','饭':'fàn',
            '飯':'fàn','馆':'guǎn','館':'guǎn','宾':'bīn','賓':'bīn','菜':'cài',
            '肉':'ròu','鱼':'yú','魚':'yú','牛':'niú','猪':'zhū','豬':'zhū',
            '鸡':'jī','雞':'jī','蛋':'dàn','米':'mǐ','麵':'miàn','包':'bāo',
            '茶':'chá','咖':'kā','啡':'fēi','酒':'jiǔ','果':'guǒ','花':'huā',
            '树':'shù','樹':'shù','草':'cǎo','鸟':'niǎo','鳥':'niǎo','狗':'gǒu',
            '猫':'māo','貓':'māo','马':'mǎ','馬':'mǎ','羊':'yáng','火':'huǒ',
            '土':'tǔ','金':'jīn','木':'mù','石':'shí','日':'rì','月':'yuè',
            '星':'xīng','云':'yún','雲':'yún','雨':'yǔ','雪':'xuě','风':'fēng',
            '風':'fēng','春':'chūn','夏':'xià','秋':'qiū','冬':'dōng','早':'zǎo',
            '晚':'wǎn','夜':'yè','午':'wǔ','晨':'chén','夕':'xī','阳':'yáng',
            '陽':'yáng','阴':'yīn','陰':'yīn',
            '迷':'mí','右':'yòu','轉':'zhuǎn','转':'zhuǎn','遠':'yuǎn','远':'yuǎn',
            '師':'shī','师':'shī','附':'fù','近':'jìn','提':'tí','款':'kuǎn',
            '超':'chāo','商':'shāng','郵':'yóu','局':'jú','便':'biàn','利':'lì',
            '客':'kè','紅':'hóng','綠':'lǜ','燈':'dēng','灯':'dēng','平':'píng',
            '東':'dōng','段':'duàn','見':'jiàn','见':'jiàn','知':'zhī','告':'gào',
            '訴':'sù','诉':'sù','還':'hái','还':'hái','再':'zài','直':'zhí',
            '嗎':'ma','嗯':'ń','呢':'ne','吧':'ba','喔':'ō','哦':'ó',
            '啊':'a','哈':'hā','哇':'wā','喂':'wèi','哎':'āi',
        }

    def _google_pinyin(self, text):
        try:
            r = self.session.get(
                "https://translate.googleapis.com/translate_a/single",
                params={'client':'gtx','sl':'zh-CN','tl':'zh-Latn-pinyin','dt':'rm','q':text},
                timeout=10
            )
            if r.status_code == 200:
                res = r.json()
                if res and len(res) > 2 and res[2]:
                    parts = [item[1] for item in res[2] if isinstance(item, list) and len(item) > 1]
                    if parts:
                        return ' '.join(parts)
                if res and isinstance(res[0], list):
                    for item in res[0]:
                        if isinstance(item, list) and len(item) > 2 and item[2] and item[2] != text:
                            if re.match(r'^[a-zA-Zāáǎàēéěèīíǐìōóǒòūúǔùüǘǚǜ\s]+$', item[2]):
                                return item[2].strip()
        except Exception:
            pass
        return None

    def _char_by_char(self, text):
        parts = []
        for c in text:
            if '\u4e00' <= c <= '\u9fff':
                py = self.pinyin_dict.get(c)
                if py:
                    parts.append(py)
                else:
                    online = self._google_pinyin(c)
                    if online and online != c:
                        cleaned = re.sub(r'[^\w\sāáǎàēéěèīíǐìōóǒòūúǔùüǘǚǜ]','',online)
                        if cleaned:
                            self.pinyin_dict[c] = cleaned
                            parts.append(cleaned)
                        else:
                            parts.append(f'[{c}]')
                    else:
                        parts.append(f'[{c}]')
            elif c.strip():
                parts.append(c)
        return ' '.join(parts)

    def get_comprehensive_pinyin(self, text):
        if not text or not text.strip():
            return ""
        text = text.strip()
        if text in self.cache:
            return self.cache[text]
        if len(text) == 1 and '\u4e00' <= text <= '\u9fff':
            b = self.pinyin_dict.get(text)
            if b:
                self.cache[text] = b
                return b
        g = self._google_pinyin(text)
        if g and g != text:
            cleaned = ' '.join(re.sub(r'[^\w\sāáǎàēéěèīíǐìōóǒòūúǔùüǘǚǜ]',' ',g).split())
            if cleaned and not any('\u4e00' <= c <= '\u9fff' for c in cleaned):
                self.cache[text] = cleaned
                return cleaned
        cb = self._char_by_char(text)
        if cb and '[' not in cb:
            self.cache[text] = cb
            return cb
        partial = ' '.join(self.pinyin_dict.get(c,c) if '\u4e00' <= c <= '\u9fff' else c for c in text)
        self.cache[text] = partial
        return partial

    def translate_text(self, text):
        if not text or not text.strip():
            return "No text provided"
        text = text.strip()
        if text in self.translation_cache:
            return self.translation_cache[text]
        try:
            r = self.session.get(
                "https://translate.googleapis.com/translate_a/single",
                params={'client':'gtx','sl':'zh-CN','tl':'en','dt':'t','q':text},
                timeout=10
            )
            if r.status_code == 200:
                res = r.json()
                if res and res[0]:
                    t = ''.join(item[0] for item in res[0] if item and item[0]).strip()
                    if t and t != text:
                        self.translation_cache[text] = t
                        return t
        except Exception:
            pass
        self.translation_cache[text] = "Translation unavailable"
        return "Translation unavailable"


class EnhancedChineseAnalyzer:
    def __init__(self):
        self.pc = ComprehensivePinyinConverter()

    def get_pinyin(self, text):
        return self.pc.get_comprehensive_pinyin(text)

    def get_translation(self, text):
        return self.pc.translate_text(text)

    def analyze_text(self, text):
        text = text.strip()
        if not text:
            return [], None
        try:
            sentence_analysis = {
                'pinyin': self.get_pinyin(text),
                'meaning': self.get_translation(text)
            }
            analysis = []
            for word in jieba.cut(text):
                word = word.strip()
                if not word or not any('\u4e00' <= c <= '\u9fff' for c in word):
                    continue
                chars = []
                if len(word) > 1:
                    for c in word:
                        if '\u4e00' <= c <= '\u9fff':
                            chars.append({
                                'char': c,
                                'pinyin': self.get_pinyin(c),
                                'meaning': self.get_translation(c)
                            })
                analysis.append({
                    'word': word,
                    'word_pinyin': self.get_pinyin(word),
                    'word_meaning': self.get_translation(word),
                    'characters': chars
                })
            return analysis, sentence_analysis
        except Exception as e:
            st.error(f"Analysis error: {e}")
            return [], None

    def build_ruby_html(self, text):
        html = '<span class="ruby-wrap">'
        for c in text:
            if '\u4e00' <= c <= '\u9fff':
                py = self.pc.pinyin_dict.get(c, '?')
                html += f'<ruby>{c}<rt>{py}</rt></ruby>'
            else:
                html += c
        return html + '</span>'

    def word_chips_html(self, text):
        html = '<div style="line-height:3.5rem;">'
        for w in jieba.cut(text):
            w = w.strip()
            if not w:
                continue
            if any('\u4e00' <= c <= '\u9fff' for c in w):
                py  = self.get_pinyin(w)
                eng = self.get_translation(w)
                html += (
                    f'<span class="word-chip">'
                    f'<span class="chip-chinese">{w}</span><br>'
                    f'<span class="chip-pinyin">{py}</span><br>'
                    f'<span class="chip-english">{eng[:18]}</span>'
                    f'</span>'
                )
            else:
                html += f'<span style="font-size:1.3rem;margin:0 2px;">{w}</span>'
        return html + '</div>'


# ── Initialize analyzer once ──────────────────────────────────────────────────
if st.session_state.analyzer is None:
    with st.spinner("Initializing pinyin engine..."):
        st.session_state.analyzer = EnhancedChineseAnalyzer()
analyzer = st.session_state.analyzer


# ── Audio helpers ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def build_audio_b64(text: str, slow: bool) -> str:
    tts = gTTS(text=text, lang='zh-tw', slow=slow)
    buf = BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()

def render_audio(slot, text: str, slow: bool = False):
    try:
        b64 = build_audio_b64(text, slow)
        slot.markdown(
            f'<audio autoplay controls style="width:100%;margin-top:8px">'
            f'<source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>',
            unsafe_allow_html=True,
        )
    except Exception as e:
        slot.error(f"Audio error: {e}")

def request_audio(text: str, slow: bool = False):
    """Used by Learn/Quiz/Speech tabs — queues audio then reruns."""
    st.session_state.play_audio_text = text
    st.session_state.play_audio_slow = slow
    st.rerun()

def inline_audio(text: str, slow: bool = False):
    """Used by Analyzer/StudyMap tabs — renders audio directly inline."""
    try:
        b64 = build_audio_b64(text, slow)
        st.empty().markdown(
            f'<audio autoplay controls style="width:100%;margin-top:6px">'
            f'<source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>',
            unsafe_allow_html=True,
        )
    except Exception as e:
        st.error(f"Audio error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# STATS BAR (always visible)
# ══════════════════════════════════════════════════════════════════════════════
st.title("🇹🇼 Traditional Chinese Learning Hub")
st.divider()

total_words = len(df)
categories  = df["Category"].nunique()
speech_rows = len(df[df["Category"].str.contains("speech", case=False, na=False)])
accuracy    = round(st.session_state.quiz_score / st.session_state.quiz_total * 100, 1) \
              if st.session_state.quiz_total > 0 else 0.0

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Total Words",      total_words)
m2.metric("Categories",       categories)
m3.metric("Speech Sentences", speech_rows)
m4.metric("Quiz Attempts",    st.session_state.quiz_total)
m5.metric("Accuracy",         f"{accuracy}%")

st.divider()

# Global audio slot — used by Learn / Quiz / Speech tabs
audio_slot = st.empty()
if st.session_state.play_audio_text:
    render_audio(audio_slot, st.session_state.play_audio_text, st.session_state.play_audio_slow)
    st.session_state.play_audio_text = None
    st.session_state.play_audio_slow = False

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_learn, tab_quiz, tab_speech, tab_progress, tab_analyzer, tab_studymap = st.tabs([
    "📚 Learn Words",
    "🧠 Quiz",
    "🎤 Speech Practice",
    "📊 Progress",
    "🔍 Text Analyzer",
    "🗺️ Textbook Study Map",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — LEARN WORDS
# ══════════════════════════════════════════════════════════════════════════════
with tab_learn:
    st.subheader("📚 Browse & Learn")

    col1, col2 = st.columns(2)
    with col1:
        learn_cat = st.selectbox(
            "Category",
            ["All"] + sorted(df["Category"].unique().tolist()),
            key="learn_cat"
        )
    with col2:
        learn_search = st.text_input(
            "Search (English / Chinese / Pinyin)",
            placeholder="Type to search…",
            key="learn_search"
        )

    filtered = df.copy()
    if learn_cat != "All":
        filtered = filtered[filtered["Category"] == learn_cat]
    if learn_search:
        mask = (
            filtered["English Word"].str.contains(learn_search, case=False, na=False) |
            filtered["Traditional Chinese Word"].str.contains(learn_search, case=False, na=False) |
            filtered["Pinyin"].str.contains(learn_search, case=False, na=False)
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
    if st.button("🎲 Random Word", key="rand_word"):
        rw = df.sample(1).iloc[0]
        st.info(
            f"**{rw['Traditional Chinese Word']}** — {rw['English Word']} "
            f"*({rw['Pinyin']})*  \nCategory: {rw['Category']}"
        )
        request_audio(rw["Traditional Chinese Word"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — QUIZ
# ══════════════════════════════════════════════════════════════════════════════
with tab_quiz:
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
            "Category",
            ["All"] + sorted(df["Category"].unique().tolist()),
            key="qcat"
        )
    with col2:
        quiz_difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], key="qdiff")

    num_opts = {"Easy": 2, "Medium": 3, "Hard": 4}[quiz_difficulty]

    def generate_question():
        qdf = df[~df["Category"].str.contains("speech", case=False, na=False)].copy()
        qdf = qdf[~qdf["Category"].str.lower().str.contains("textbook entire study map", na=False)]
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
        request_audio(correct["Traditional Chinese Word"])

    if st.button("🎲 New Question", key="new_q"):
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
        n        = len(st.session_state.quiz_options)
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
# TAB 3 — SPEECH PRACTICE
# ══════════════════════════════════════════════════════════════════════════════
with tab_speech:
    st.subheader("🎤 Speech Practice")

    col1, col2, col3 = st.columns(3)
    with col1:
        num_sent = st.slider("Sentences", 3, 15, st.session_state.speech_sentences, key="sp_slider")
        st.session_state.speech_sentences = num_sent
    with col2:
        speed = st.selectbox(
            "Speed", ["slow", "normal"],
            index=["slow", "normal"].index(st.session_state.speech_speed),
            key="sp_speed"
        )
        st.session_state.speech_speed = speed
    with col3:
        show_py = st.checkbox("Show Pinyin", value=st.session_state.speech_show_pinyin, key="sp_pinyin")
        st.session_state.speech_show_pinyin = show_py

    if st.button("🎲 Generate Speech", key="gen_speech"):
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
        if st.button("🔊 Play Full Speech", key="play_full_speech"):
            full = " ... ".join(s["Traditional Chinese Word"] for s in speech)
            request_audio(full, slow=(speed == "slow"))
    else:
        st.info("Press **Generate Speech** to create a random speech set.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — PROGRESS
# ══════════════════════════════════════════════════════════════════════════════
with tab_progress:
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
        st.info("No quiz attempts yet. Go to the **Quiz** tab to start!")

    st.divider()
    st.subheader("📋 Words per Category")
    cat_counts = df.groupby("Category").size().reset_index(name="Count")
    st.dataframe(cat_counts, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — TEXT ANALYZER
# ══════════════════════════════════════════════════════════════════════════════
with tab_analyzer:
    st.markdown('<h1 class="big-font">🔍 Chinese Text Analyzer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="medium-font">Multi-source pinyin · word segmentation · character breakdown</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧪 Test Pinyin System", key="test_pinyin"):
            test_chars = ["適","合","我","愛","你","學","習","漢","語","工","作","需","要"]
            with st.spinner("Testing..."):
                for char in test_chars:
                    py  = analyzer.get_pinyin(char)
                    tr  = analyzer.get_translation(char)
                    badge = '<span class="success-badge">✓</span>' if '[' not in py else '<span class="error-badge">⚠</span>'
                    st.markdown(f"**{char}** → `{py}` → *{tr}* {badge}", unsafe_allow_html=True)
                    time.sleep(0.05)
    with col2:
        if st.button("🎯 Test Word Combinations", key="test_words"):
            test_words = ["適合","我愛你","工作","學習","漢語","北京大學"]
            with st.spinner("Testing..."):
                for word in test_words:
                    py  = analyzer.get_pinyin(word)
                    tr  = analyzer.get_translation(word)
                    badge = '<span class="success-badge">✓</span>' if '[' not in py else '<span class="error-badge">⚠</span>'
                    st.markdown(f"**{word}** → `{py}` → *{tr}* {badge}", unsafe_allow_html=True)
                    time.sleep(0.05)

    st.divider()
    chinese_text = st.text_area(
        "Enter Chinese text:",
        placeholder="適合我的工作需要幫助",
        height=120,
        key="ana_input"
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        analyze_btn = st.button("🚀 Analyze", type="primary", key="ana_btn")
    with col2:
        show_debug = st.checkbox("Debug info", key="ana_debug")

    if analyze_btn and chinese_text:
        with st.spinner("Analyzing..."):
            analysis, sentence_analysis = analyzer.analyze_text(chinese_text)

        if sentence_analysis:
            st.markdown('<div class="sentence-box">', unsafe_allow_html=True)
            st.markdown(f'<div class="sentence-text">{chinese_text}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="sentence-pinyin">🎵 {sentence_analysis["pinyin"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="sentence-meaning">📝 {sentence_analysis["meaning"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            if st.button("🔊 Play Sentence", key="ana_audio"):
                inline_audio(chinese_text)

            st.divider()

            for wd in analysis:
                word         = wd['word']
                word_pinyin  = wd['word_pinyin']
                word_meaning = wd['word_meaning']
                characters   = wd['characters']

                st.markdown('<div class="word-box">', unsafe_allow_html=True)
                st.markdown(f'<div class="chinese-word">{word}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="pinyin-highlight">🎵 {word_pinyin}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="meaning">📝 {word_meaning}</div>', unsafe_allow_html=True)
                badge = '<span class="success-badge">✅ Perfect</span>' if '[' not in word_pinyin else '<span class="error-badge">⚠️ Fallback</span>'
                st.markdown(badge, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                if len(characters) > 1:
                    st.markdown("**Character breakdown:**")
                    cols = st.columns(min(len(characters), 4))
                    for j, cd in enumerate(characters):
                        with cols[j % 4]:
                            st.markdown('<div class="character-box">', unsafe_allow_html=True)
                            st.markdown(f'<div class="chinese-char">{cd["char"]}</div>', unsafe_allow_html=True)
                            st.markdown(f'<div class="ana-pinyin" style="color:#ffd700;">{cd["pinyin"]}</div>', unsafe_allow_html=True)
                            st.markdown(f'<div style="color:white;font-size:16px;">{cd["meaning"][:22]}</div>', unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)

                    st.markdown('<div class="analysis-box">', unsafe_allow_html=True)
                    parts = [f'**{c["char"]}** ({c["pinyin"]}: {c["meaning"].split(",")[0][:12]})' for c in characters]
                    st.markdown(f'<div class="combination-text">{" + ".join(parts)} = **{word}**</div>', unsafe_allow_html=True)
                    st.markdown(f'<p style="font-size:20px;color:#555;">Combined: <strong>{word_meaning}</strong></p>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                if show_debug:
                    st.caption(f"Debug: word='{word}', chars={len(characters)}, pinyin='{word_pinyin}'")

                st.divider()

            perfect = sum(1 for w in analysis if '[' not in w['word_pinyin'])
            c1, c2, c3 = st.columns(3)
            c1.metric("Words",    len(analysis))
            c2.metric("Chars",    sum(len(w['characters']) for w in analysis))
            c3.metric("Perfect",  f"{perfect}/{len(analysis)}")

    elif chinese_text and not analyze_btn:
        st.info("Click **Analyze** to process your text.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — TEXTBOOK ENTIRE STUDY MAP
# ══════════════════════════════════════════════════════════════════════════════
with tab_studymap:
    st.markdown('<div class="study-map-title">🗺️ Textbook Entire Study Map</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="study-map-subtitle">'
        'Full textbook dialogues — listen, read, and break down every word & character'
        '</div>',
        unsafe_allow_html=True
    )

    study_df = df[df["Category"].str.lower().str.contains("textbook entire study map", na=False)].copy()

    if study_df.empty:
        st.warning(
            "No rows found with **Category = 'textbook entire study map'**.\n\n"
            "Add rows to your Excel file with that category. "
            "Put the Chinese text in **Traditional Chinese Word**, "
            "English in **English Word**, and pinyin in **Pinyin**."
        )
    else:
        sm_speed  = st.radio("🔊 Audio speed", ["Normal", "Slow"], horizontal=True, key="sm_speed")
        slow_audio = sm_speed == "Slow"
        st.divider()

        for row_idx, (_, row) in enumerate(study_df.iterrows()):
            chinese_para = str(row.get("Traditional Chinese Word", "")).strip()
            english_para = str(row.get("English Word", "")).strip()
            pinyin_para  = str(row.get("Pinyin", "")).strip()
            if not chinese_para:
                continue

            # ── Full paragraph card ────────────────────────────────────────
            st.markdown('<div class="para-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="para-card-title">📖 Passage {row_idx + 1}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="para-chinese">{chinese_para}</div>', unsafe_allow_html=True)
            if english_para:
                st.markdown(f'<div class="para-english">🇬🇧 {english_para}</div>', unsafe_allow_html=True)
            if pinyin_para:
                st.markdown(f'<div class="para-pinyin">🎵 {pinyin_para}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            if st.button(f"🔊 Play Full Passage {row_idx + 1}", key=f"sm_play_para_{row_idx}"):
                st.session_state[f"sm_play_para_{row_idx}"] = True
            if st.session_state.get(f"sm_play_para_{row_idx}"):
                with st.spinner("Generating audio..."):
                    inline_audio(chinese_para, slow=slow_audio)
                st.session_state[f"sm_play_para_{row_idx}"] = False

            # ── Line-by-line expander ──────────────────────────────────────
            with st.expander(f"📋 Line-by-line — Passage {row_idx + 1}"):
                sentences = [s.strip() for s in re.split(r'(?<=[。？！\n])', chinese_para) if s.strip()]
                for s_idx, sentence in enumerate(sentences):
                    st.markdown(
                        f'<div class="line-card">'
                        f'<div class="line-chinese">{sentence}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    if st.button("🔊 Play", key=f"sm_line_btn_{row_idx}_{s_idx}"):
                        st.session_state[f"sm_line_play_{row_idx}_{s_idx}"] = True
                    if st.session_state.get(f"sm_line_play_{row_idx}_{s_idx}"):
                        with st.spinner("Generating audio..."):
                            inline_audio(sentence, slow=slow_audio)
                        st.session_state[f"sm_line_play_{row_idx}_{s_idx}"] = False            # ── Deep analysis expander ─────────────────────────────────────
            with st.expander(f"🔬 Full Analysis — Passage {row_idx + 1}"):

                st.markdown("#### 🈶 Pinyin Above Every Character")
                st.markdown(analyzer.build_ruby_html(chinese_para), unsafe_allow_html=True)
                st.divider()

                st.markdown("#### 🧩 Word Chips per Sentence")
                for s_idx, sentence in enumerate(
                    [s.strip() for s in re.split(r'(?<=[。？！\n])', chinese_para) if s.strip()]
                ):
                    st.markdown(f"**Sentence {s_idx + 1}:** `{sentence}`")
                    with st.spinner("Segmenting..."):
                        st.markdown(analyzer.word_chips_html(sentence), unsafe_allow_html=True)

                st.divider()
                st.markdown("#### 📖 Word & Character Deep Dive")
                if st.button("🚀 Run Deep Analysis", key=f"sm_deep_{row_idx}"):
                    st.session_state[f"sm_deep_done_{row_idx}"] = True

                if st.session_state.get(f"sm_deep_done_{row_idx}"):
                    with st.spinner("Analyzing all words and characters..."):
                        analysis, sentence_analysis = analyzer.analyze_text(chinese_para)
                    if sentence_analysis:
                        st.markdown(f"**Pinyin:** `{sentence_analysis['pinyin']}`")
                        st.markdown(f"**Meaning:** {sentence_analysis['meaning']}")
                        st.divider()
                    for wd in analysis:
                        st.markdown('<div class="word-box">', unsafe_allow_html=True)
                        st.markdown(f'<div class="chinese-word">{wd["word"]}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="pinyin-highlight">🎵 {wd["word_pinyin"]}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="meaning">📝 {wd["word_meaning"]}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        if len(wd['characters']) > 1:
                            cols = st.columns(min(len(wd['characters']), 4))
                            for j, cd in enumerate(wd['characters']):
                                with cols[j % 4]:
                                    st.markdown('<div class="character-box">', unsafe_allow_html=True)
                                    st.markdown(f'<div class="chinese-char">{cd["char"]}</div>', unsafe_allow_html=True)
                                    st.markdown(f'<div class="ana-pinyin" style="color:#ffd700;">{cd["pinyin"]}</div>', unsafe_allow_html=True)
                                    st.markdown(f'<div style="color:white;font-size:16px;">{cd["meaning"][:22]}</div>', unsafe_allow_html=True)
                                    st.markdown('</div>', unsafe_allow_html=True)
                        st.markdown("")

            st.divider()
