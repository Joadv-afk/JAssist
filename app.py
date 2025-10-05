import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

# --- KONFIGURASI DASAR ---
load_dotenv()
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except Exception as e:
    st.error("⚠️ API Key tidak ditemukan. Pastikan file .env berisi GOOGLE_API_KEY.")
    st.stop()

# --- INISIALISASI CHAT HISTORY ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- FUNGSI MENDAPATKAN RESPON DARI GEMINI ---
def dapatkan_respon(user_input):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(
            f"""
            Kamu adalah asisten AI yang ramah dan membantu bernama **JAssist**.
            Balas dengan gaya percakapan santai, sopan, dan mudah dipahami.
            Jika pertanyaan terlalu sensitif, jawab dengan netral dan aman.
            Berikut pertanyaan pengguna:
            {user_input}
            """
        )
        return response.text
    except Exception as e:
        return f"Terjadi kesalahan: {e}"

# --- ANTARMUKA UTAMA ---
st.set_page_config(page_title="💬 JAssist", page_icon="💬", layout="centered")
st.title("💬 JAssist")
st.caption("Ngobrol santai dengan AI yang siap membantu apa pun topikmu 🤖")

# --- INPUT PENGGUNA ---
user_input = st.text_input("Ketik pesan kamu di sini...")

if st.button("Kirim"):
    if user_input.strip() != "":
        # Simpan input ke riwayat
        st.session_state.chat_history.append(("🧑 Kamu", user_input))
        
        with st.spinner("JAssist sedang mengetik..."):
            bot_reply = dapatkan_respon(user_input)
        
        # Simpan balasan bot ke riwayat
        st.session_state.chat_history.append(("🤖 JAssist", bot_reply))
    else:
        st.warning("Tolong ketik sesuatu dulu ya!")

# --- TAMPILKAN RIWAYAT CHAT ---
st.divider()
st.subheader("Riwayat Percakapan")

if st.session_state.chat_history:
    for sender, message in st.session_state.chat_history:
        st.markdown(f"**{sender}:** {message}")
else:
    st.info("Belum ada percakapan. Mulailah dengan mengetik pertanyaan di atas ☝️")

# --- OPSI RESET CHAT ---
if st.button("🧹 Hapus Riwayat Chat"):
    st.session_state.chat_history = []
    st.experimental_rerun()
