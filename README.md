# 💬 JAssist – Asisten AI Serbaguna
Sebuah chatbot cerdas berbasis AI yang berfungsi sebagai asisten percakapan umum berbahasa Indonesia.
Aplikasi ini dibuat menggunakan Streamlit dan Google Gemini API (gemini-2.5-flash) dengan memori percakapan dan streaming jawaban.

## ✨ Fitur-fitur

* **Chat Berkelanjutan (Memory):** Bot mengingat konteks percakapan (pakai start_chat).
* **Streaming Jawaban:** Teks muncul bertahap sehingga terasa lebih cepat.
* **Hapus & Unduh Riwayat:** Satu klik untuk reset atau menyimpan chat ke .txt.

## 🚀 Cara Menjalankan

1.  **Clone repositori ini:**
    ```bash
    git clone [https://github.com/Joadv-afk/JAssist](https://github.com/Joadv-afk/JAssist)
    ```
2.  **Buat dan aktifkan environment conda:**
    ```bash
    conda create -n resep-env python=3.9
    conda activate resep-env
    ```
3.  **Install semua library yang dibutuhkan:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Buat file `.env`** dan isi dengan Google API Key Anda:
    ```
    GOOGLE_API_KEY="API_KEY_ANDA"
    ```
5.  **Jalankan aplikasi Streamlit:**
    ```bash
    streamlit run app.py
    ```