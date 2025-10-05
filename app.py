# JAssist – Chatbot Serbaguna (Streamlit + google-genai)
# File: app.py

import os
import streamlit as st
from google import genai

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="💬 JAssist", page_icon="💬", layout="centered")
st.title("💬 JAssist")
st.caption("Ngobrol santai dengan AI yang siap membantu apa pun topikmu 🤖")

# ---------- SIDEBAR SETTINGS ----------
with st.sidebar:
    st.subheader("⚙️ Pengaturan")
    # Ambil API key dari Secrets (disarankan) atau ENV sebagai fallback
    default_key = st.secrets.get("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY", ""))
    google_api_key = st.text_input("GOOGLE_API_KEY", value=default_key, type="password")

    model_name = st.selectbox(
        "Pilih model",
        # 2.0-flash-exp biasanya cepat; 1.5-flash juga cepat & stabil
        ["gemini-2.0-flash-exp", "gemini-1.5-flash", "gemini-2.5-flash"],
        index=0,
        help="Gunakan 2.0-flash-exp untuk respons cepat."
    )
    temperature = st.slider("Temperature (kreativitas)", 0.0, 1.0, 0.6, 0.05)
    sys_prompt = st.text_area(
        "System Prompt (persona JAssist)",
        value=(
            "Kamu adalah JAssist, asisten AI berbahasa Indonesia yang ramah, ringkas, "
            "dan membantu. Jawab dengan sopan, gunakan poin-poin bila cocok, "
            "hindari klaim medis/hukum berisiko, dan minta klarifikasi jika perlu."
        ),
        height=120
    )

# ---------- CLIENT & CHAT (CACHED) ----------
@st.cache_resource(show_spinner=False)
def get_client(api_key: str):
    if not api_key:
        raise ValueError("API key tidak ditemukan. Set di sidebar atau Secrets.")
    return genai.Client(api_key=api_key)

def reset_chat_if_key_changed(current_key: str):
    if "_last_key" not in st.session_state or st.session_state._last_key != current_key:
        st.session_state._last_key = current_key
        st.session_state.pop("chat", None)
        st.session_state.pop("messages", None)

# Panggil dan validasi client
try:
    reset_chat_if_key_changed(google_api_key)
    client = get_client(google_api_key)
except Exception as e:
    st.error(f"⚠️ {e}")
    st.stop()

# Pesan awal
if "messages" not in st.session_state:
    st.session_state.messages = []

# Buat chat session sekali (ketika belum ada)
if "chat" not in st.session_state:
    try:
        st.session_state.chat = client.chats.create(
            model=model_name,
            config={
                "temperature": temperature,
                "system_instruction": sys_prompt
            }
        )
    except Exception as e:
        st.error(f"Gagal membuat sesi chat: {e}")
        st.stop()

# ---------- TAMPILKAN RIWAYAT ----------
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# ---------- INPUT USER ----------
prompt = st.chat_input("Ketik pesan kamu di sini…")

if prompt:
    # Tampilkan pesan user
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Kirim ke Gemini
    try:
        with st.chat_message("assistant"):
            with st.spinner("JAssist sedang mengetik…"):
                # pangkas input agar tidak terlalu panjang
                user_input = prompt.strip()[:4000]

                # Kirim single-turn message ke sesi chat
                response = st.session_state.chat.send_message(
                    user_input,
                    config={  # bisa override per pesan kalau mau
                        "temperature": temperature,
                    },
                )

                # Ambil teks jawaban (API google-genai tidak selalu .text)
                if hasattr(response, "text") and response.text:
                    answer = response.text
                else:
                    answer = str(response)

                st.markdown(answer)

        # simpan ke riwayat
        st.session_state.messages.append({"role": "assistant", "content": answer})

    except Exception as e:
        st.error(f"Terjadi kesalahan saat meminta jawaban: {e}")

# ---------- TOMBOL HAPUS ----------
st.divider()
col1, col2 = st.columns(2)
with col1:
    if st.button("🧹 Hapus Riwayat Chat"):
        st.session_state.pop("messages", None)
        st.session_state.pop("chat", None)
        st.rerun()
with col2:
    st.caption("Tip: untuk respons lebih cepat, coba model **gemini-2.0-flash-exp**.")
