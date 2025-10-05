import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

# =============== PAGE CONFIG ===============
st.set_page_config(page_title="💬 JAssist", page_icon="💬", layout="centered")
st.title("💬 JAssist")
st.caption("Ngobrol santai dengan AI yang siap membantu apa pun topikmu 🤖")

# =============== API KEY SETUP ===============
load_dotenv()
# Prioritas: Streamlit Secrets -> ENV
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY", ""))

if not GOOGLE_API_KEY:
    st.error("⚠️ GOOGLE_API_KEY tidak ditemukan. Set di Secrets Streamlit atau file .env.")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

# =============== PARAMETER BOT ===============
MODEL_NAME = "gemini-2.5-flash"   # boleh ganti ke "gemini-1.5-flash" jika ingin lebih cepat
TEMPERATURE = 0.6
SYSTEM_PROMPT = (
    "Kamu adalah JAssist, asisten AI berbahasa Indonesia yang ramah, ringkas, dan membantu. "
    "Gunakan bahasa sederhana, sopan, dan jelas. Bila cocok, gunakan poin-poin. "
    "Hindari klaim medis/hukum berisiko. Minta klarifikasi jika pertanyaan tidak jelas."
)
MAX_TURNS_DISPLAY = 12    # banyaknya pasangan (user,assistant) yang ditampilkan di UI
MAX_INPUT_CHARS = 4000    # batasi panjang input agar responsif

# =============== INIT SESSION STATE ===============
if "messages" not in st.session_state:
    st.session_state.messages = []   # untuk UI (list of dict {role, content})

if "chat" not in st.session_state:
    # Buat satu sesi chat yang menyimpan konteks percakapan di sisi model
    model = genai.GenerativeModel(MODEL_NAME, system_instruction=SYSTEM_PROMPT)
    st.session_state.chat = model.start_chat(history=[])  # history model (server-side)

# =============== TAMPILKAN RIWAYAT (dibatasi) ===============
for msg in st.session_state.messages[-2*MAX_TURNS_DISPLAY:]:
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.markdown(msg["content"])

# =============== INPUT PENGGUNA ===============
prompt = st.chat_input("Ketik pesan kamu di sini…")

if prompt:
    # Simpan dan tampilkan pesan user
    prompt = prompt.strip()[:MAX_INPUT_CHARS]
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Minta jawaban ke sesi chat (dengan streaming)
    with st.chat_message("assistant"):
        with st.spinner("JAssist sedang mengetik…"):
            placeholder = st.empty()
            full_text = ""

            try:
                # Streaming token demi token
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

    # Simpan jawaban bot ke riwayat UI
    st.session_state.messages.append({"role": "assistant", "content": full_text})

# =============== KONTROL TAMBAHAN ===============
st.divider()
col1, col2 = st.columns(2)
with col1:
    if st.button("🧹 Hapus Riwayat Chat"):
        # reset UI & memori model
        st.session_state.messages = []
        model = genai.GenerativeModel(MODEL_NAME, system_instruction=SYSTEM_PROMPT)
        st.session_state.chat = model.start_chat(history=[])
        st.rerun()
with col2:
    st.caption("Tip: untuk respons lebih cepat, coba model *gemini-1.5-flash*.")
