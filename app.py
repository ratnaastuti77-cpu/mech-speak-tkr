import streamlit as st
from google import genai
from google.genai import types
from gtts import gTTS
import io
import random

# Konfigurasi Halaman
st.set_page_config(page_title="VOCA-PEARSON AI", page_icon="🎓", layout="centered")

st.title("🎓 VOCA-PEARSON AI")
st.caption("Simulasi Asesmen Speaking Kejuruan Berbasis Format Pearson Test")

# Inisialisasi Gemini API
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Bank Soal Wajib (Akan Diacak untuk Setiap Siswa)
bank_wajib = {
    "TKR (Teknik Kendaraan Ringan)": [
        {"tipe": "Repeat Sentence", "audio": "Please inspect the brake pads and check the engine oil level.", "kunci": "Please inspect the brake pads and check the engine oil level."},
        {"tipe": "Repeat Sentence", "audio": "We need to replace the car battery because the voltage is too low.", "kunci": "We need to replace the car battery because the voltage is too low."},
        {"tipe": "Answer Short Question", "audio": "What component in a car engine ignites the air and fuel mixture?", "kunci": "Spark plug (busi)."},
        {"tipe": "Answer Short Question", "audio": "What tool do mechanics use to tighten bolts and nuts?", "kunci": "Wrench / Spanner (kunci pas)."}
    ],
    "TSM (Teknik Sepeda Motor)": [
        {"tipe": "Repeat Sentence", "audio": "Please adjust the drive chain tension and check the tire pressure.", "kunci": "Please adjust the drive chain tension and check the tire pressure."},
        {"tipe": "Repeat Sentence", "audio": "Regular fuel injection cleaning keeps the motorcycle engine running smoothly.", "kunci": "Regular fuel injection cleaning keeps the motorcycle engine running smoothly."},
        {"tipe": "Answer Short Question", "audio": "What safety gear must a rider wear on their head before riding?", "kunci": "A helmet."},
        {"tipe": "Answer Short Question", "audio": "What liquid lubricates the moving parts inside a motorcycle engine?", "kunci": "Engine oil (oli mesin)."}
    ],
    "AK (Akuntansi)": [
        {"tipe": "Repeat Sentence", "audio": "All financial transactions must be recorded accurately in the monthly report.", "kunci": "All financial transactions must be recorded accurately in the monthly report."},
        {"tipe": "Repeat Sentence", "audio": "Please double-check the balance sheet to ensure there are no missing entries.", "kunci": "Please double-check the balance sheet to ensure there are no missing entries."},
        {"tipe": "Answer Short Question", "audio": "What do you call the money a business earns from selling goods or services?", "kunci": "Revenue / Income (pendapatan)."},
        {"tipe": "Answer Short Question", "audio": "What document proves that a customer has paid for a product?", "kunci": "Receipt / Invoice (kuitansi/faktur)."}
    ],
    "TKJ (Teknik Komputer dan Jaringan)": [
        {"tipe": "Repeat Sentence", "audio": "Please restart the main router and verify the network cable connection.", "kunci": "Please restart the main router and verify the network cable connection."},
        {"tipe": "Repeat Sentence", "audio": "Make sure the IP address is configured properly on the local server.", "kunci": "Make sure the IP address is configured properly on the local server."},
        {"tipe": "Answer Short Question", "audio": "What device connects multiple computers in a local network?", "kunci": "Switch or Router."},
        {"tipe": "Answer Short Question", "audio": "What software protects a computer network from unauthorized access?", "kunci": "Firewall or Antivirus."}
    ],
    "DPB (Desain dan Produksi Busana)": [
        {"tipe": "Repeat Sentence", "audio": "We selected breathable cotton fabric with neat stitching for this uniform.", "kunci": "We selected breathable cotton fabric with neat stitching for this uniform."},
        {"tipe": "Repeat Sentence", "audio": "Please measure the shoulder width and sleeve length before cutting the pattern.", "kunci": "Please measure the shoulder width and sleeve length before cutting the pattern."},
        {"tipe": "Answer Short Question", "audio": "What tool do tailors use to measure a customer's body size?", "kunci": "Measuring tape (pita ukur)."},
        {"tipe": "Answer Short Question", "audio": "What machine is used to stitch pieces of fabric together?", "kunci": "Sewing machine (mesin jahit)."}
    ],
    "APHP (Agribisnis Pengolahan Hasil Pertanian)": [
        {"tipe": "Repeat Sentence", "audio": "Always wear clean gloves and a hairnet inside the food processing room.", "kunci": "Always wear clean gloves and a hairnet inside the food processing room."},
        {"tipe": "Repeat Sentence", "audio": "Our processed fruit chips are made without any artificial preservatives.", "kunci": "Our processed fruit chips are made without any artificial preservatives."},
        {"tipe": "Answer Short Question", "audio": "What packaging method removes air to keep food fresh longer?", "kunci": "Vacuum packaging / Vacuum sealing."},
        {"tipe": "Answer Short Question", "audio": "What heating process kills harmful bacteria in fresh milk?", "kunci": "Pasteurization (pasteurisasi)."}
    ]
}

# 1. Input Identitas & Jurusan Siswa
nama_siswa = st.text_input("Nama Siswa:", placeholder="Masukkan nama lengkapmu...")
jurusan = st.selectbox("Pilih Jurusan:", list(bank_wajib.keys()))

# Inisialisasi soal acak per sesi siswa
if "soal_sekarang" not in st.session_state or st.session_state.get("jurusan_aktif") != jurusan:
    st.session_state.soal_sekarang = random.choice(bank_wajib[jurusan])
    st.session_state.jurusan_aktif = jurusan

col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    if st.button("🔀 Acak Soal Berikutnya", use_container_width=True):
        st.session_state.soal_sekarang = random.choice(bank_wajib[jurusan])
        st.rerun()

with col_btn2:
    if st.button("✨ Buat Soal Unik AI", use_container_width=True):
        with st.spinner("Gemini membuat soal unik khusus untukmu..."):
            res = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"Buatkan 1 kalimat instruksi/pernyataan profesional Bahasa Inggris (10-14 kata) untuk dunia kerja SMK jurusan {jurusan}. Berikan HANYA kalimat Bahasa Inggrisnya saja tanpa tanda kutip."
            )
            kalimat_baru = res.text.strip()
            st.session_state.soal_sekarang = {
                "tipe": "Repeat Sentence (AI Unique)",
                "audio": kalimat_baru,
                "kunci": kalimat_baru
            }
            st.rerun()

soal = st.session_state.soal_sekarang

# 2. Tampilan Audio Soal (Teks Disembunyikan)
st.markdown("---")
st.subheader(f"🎧 Tipe Tes: {soal['tipe']}")

if "Repeat Sentence" in soal["tipe"]:
    st.info("🙈 **Teks disembunyikan!** Dengarkan kalimat berikut, lalu **ucapkan ulang** persis seperti yang kamu dengar.")
else:
    st.info("🙈 **Teks disembunyikan!** Dengarkan pertanyaan singkat berikut, lalu **jawab dengan 1–3 kata** yang tepat.")

tts = gTTS(text=soal["audio"], lang='en', slow=False)
audio_fp = io.BytesIO()
tts.write_to_fp(audio_fp)
audio_fp.seek(0)
st.audio(audio_fp, format="audio/mp3")

# 3. Rekam Jawaban & Nilai
st.markdown("---")
st.subheader("🎙️ Rekam Jawabanmu")
audio_siswa = st.audio_input("Tekan mikrofon untuk mulai berbicara:")

if audio_siswa is not None:
    if st.button("📊 Hitung Skor Ala Pearson (10–90)", type="primary", use_container_width=True):
        with st.spinner("Menganalisis Content, Pronunciation, dan Oral Fluency..."):
            audio_bytes = audio_siswa.read()
            
            prompt = f"""
            Kamu adalah sistem penilai otomatis standar Pearson English Test (skala 10-90) untuk siswa SMK bernama {nama_siswa if nama_siswa else 'Siswa'} dari jurusan {jurusan}.
            Tipe Soal: {soal['tipe']}
            Audio Soal Asli: "{soal['audio']}"
            Kunci Jawaban: "{soal['kunci']}"
            
            Evaluasi rekaman suara siswa berikut dalam Bahasa Indonesia dengan format laporan skor Pearson:
            
            ### 🏆 Overall Speaking Score: [10-90] / 90
            * **Content / Accuracy (Ketepatan Isi):** [10-90] / 90 — [Penjelasan singkat 1 kalimat]
            * **Pronunciation (Pelafalan):** [10-90] / 90 — [Penjelasan singkat 1 kalimat]
            * **Oral Fluency (Kelancaran):** [10-90] / 90 — [Penjelasan singkat 1 kalimat]
            
            ### 💡 Saran Perbaikan:
            [1 tips spesifik untuk percobaan berikutnya]
            """
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    prompt,
                    types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav")
                ]
            )
            
            st.markdown("---")
            st.success(f"🔓 **Transkrip Audio:** *\"{soal['audio']}\"*\n\n✅ **Kunci Jawaban:** *{soal['kunci']}*")
            st.markdown(response.text)
