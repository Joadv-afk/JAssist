🚀 Cara Menjalankan
Clone repositori ini:
git clone [https://github.com/fadhstrong-netizen/Juru-Resep-Nusantara.git](https://github.com/fadhstrong-netizen/Juru-Resep-Nusantara.git)
Buat dan aktifkan environment conda:
conda create -n resep-env python=3.9
conda activate resep-env
Install semua library yang dibutuhkan:
pip install -r requirements.txt
Buat file .env dan isi dengan Google API Key Anda:
GOOGLE_API_KEY="API_KEY_ANDA"
Jalankan aplikasi Streamlit:
streamlit run app.py
