import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime

# =============== PAGE CONFIG ===============
st.set_page_config(page_title="💬 JAssist", page_icon="💬", layout="centered")

# =============== GLOBAL STYLES (UI) ===============
st.markdown("""
<style>
.block-container {max-width: 820px;}
.stChatMessage {margin-bottom: 0.4rem;}
.small-muted {font-size: 0.75rem; opacity: 0.65; margin-top: -0.25rem;}
hr {margin: 0.6rem 0;}
</style>
""", unsafe_allow_html=True)

# =============== HEADER ===============
st.title("💬 JAssist")
st.caption("""
Siap membantu apa pun topikmu.
Sesi chat akan hilang jika di-reload.
Isi chat bisa di-download.
""")

# =============== API KEY SETUP ===============
load_dotenv()
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY", ""))

if not GOOGLE_API_KEY:
    st.error("⚠️ GOOGLE_API_KEY tidak ditemukan. Set di Secrets Streamlit atau file .env.")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

# =============== PARAMETER BOT ===============
SYSTEM_PROMPT = (
    "Kamu adalah JAssist, asisten AI berbahasa Indonesia yang ramah, ringkas, dan membantu. "
    "Gunakan bahasa sederhana, sopan, dan jelas. Bila cocok, gunakan poin-poin. "
    "Hindari klaim medis/hukum berisiko. Minta klarifikasi jika pertanyaan tidak jelas."
)
MAX_TURNS_DISPLAY = 12
MAX_INPUT_CHARS = 4000

# =============== SIDEBAR ===============
with st.sidebar:
    st.subheader("⚙️ Kontrol")
    # Unduh riwayat percakapan
    if "messages" in st.session_state and st.session_state.get("messages"):
        export_text = []
        for m in st.session_state["messages"]:
            role = "Kamu" if m["role"] == "user" else "JAssist"
            t = m.get("time", "")
            export_text.append(f"[{t}] {role}: {m['content']}")
        st.download_button(
            "⬇️ Unduh Riwayat (.txt)",
            data="\n\n".join(export_text),
            file_name=f"JAssist_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
    if st.button("🧹 Hapus Riwayat Chat"):
        st.session_state.messages = []
        model = genai.GenerativeModel(MODEL_NAME, system_instruction=SYSTEM_PROMPT)
        st.session_state.chat = model.start_chat(history=[])
        st.rerun()

# =============== INIT SESSION STATE ===============
if "messages" not in st.session_state:
    st.session_state.messages = []   # untuk UI: [{role, content, time}]

if "chat" not in st.session_state:
    model = genai.GenerativeModel(MODEL_NAME, system_instruction=SYSTEM_PROMPT)
    st.session_state.chat = model.start_chat(history=[])

# =============== HELPERS ===============
def now_str():
    return datetime.now().strftime("%H:%M")

def render_msg(role: str, content: str, time_str: str):
    avatar = "🧑" if role == "user" else "🤖"
    with st.chat_message(role, avatar=avatar):
        st.markdown(content)
        st.markdown(f"<div class='small-muted'>{time_str}</div>", unsafe_allow_html=True)

# =============== TAMPILKAN RIWAYAT ===============
for msg in st.session_state.messages[-2*MAX_TURNS_DISPLAY:]:
    render_msg(msg["role"], msg["content"], msg.get("time", ""))

# =============== INPUT PENGGUNA ===============
prompt = st.chat_input("Ketik pesan kamu di sini…")

if prompt:
    prompt = prompt.strip()[:MAX_INPUT_CHARS]
    time_user = now_str()
    st.session_state.messages.append({"role": "user", "content": prompt, "time": time_user})
    render_msg("user", prompt, time_user)

    # Minta jawaban dari Gemini (dengan streaming)
    time_bot = now_str()
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("JAssist sedang mengetik…"):
            placeholder = st.empty()
            full_text = ""

            try:
                stream = st.session_state.chat.send_message(
                    prompt,
                    stream=True,
                    generation_config=genai.types.GenerationConfig(
                        temperature=TEMPERATURE
                    )
                )
                for chunk in stream:
                    if hasattr(chunk, "text") and chunk.text:
                        full_text += chunk.text
                        placeholder.markdown(full_text)
            except Exception as e:
                full_text = f"Maaf, terjadi kesalahan: {e}"
                placeholder.markdown(full_text)

        st.markdown(f"<div class='small-muted'>{time_bot}</div>", unsafe_allow_html=True)

    # Simpan jawaban bot ke riwayat UI
    st.session_state.messages.append({"role": "assistant", "content": full_text, "time": time_bot})
