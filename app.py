import streamlit as st
from google import genai
from gtts import gTTS
import io
import random
import difflib
import re
import pandas as pd

# Konfigurasi Halaman
st.set_page_config(page_title="LISTEN & WRITE", page_icon="✍️", layout="centered")

st.title("✍️ LISTEN & WRITE")
st.caption("Latihan Listening & Spelling Kejuruan English Club")

# Inisialisasi Gemini API
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Penyimpanan Rekap Nilai Bersama (Real-Time Leaderboard)
@st.cache_resource
def get_rekap_nilai():
    return []

rekap_kelas = get_rekap_nilai()

# Bank Soal Wajib (Versi Simple untuk Semua Jurusan)
bank_wajib = {
    "TKR (Teknik Kendaraan Ringan)": [
        {"tipe": "Listen & Write (Word)", "audio": "TIRE.", "kunci": "TIRE."},
        {"tipe": "Listen & Write (Word)", "audio": "ENGINE.", "kunci": "ENGINE."},
        {"tipe": "Listen & Write (Sentence)", "audio": "OPEN THE HOOD.", "kunci": "OPEN THE HOOD."},
        {"tipe": "Listen & Write (Sentence)", "audio": "CHECK THE TIRE PRESSURE.", "kunci": "CHECK THE TIRE PRESSURE."},
        {"tipe": "Listen & Write (Sentence)", "audio": "CHANGE THE ENGINE OIL.", "kunci": "CHANGE THE ENGINE OIL."},
        {"tipe": "Listen & Answer", "audio": "What do we use to stop a car?", "kunci": "Brake"},
        {"tipe": "Listen & Answer", "audio": "What part touches the road?", "kunci": "Tire"},
        {"tipe": "Listen & Answer", "audio": "What liquid cools the car engine?", "kunci": "Coolant"}
    ],
    "TSM (Teknik Sepeda Motor)": [
        {"tipe": "Listen & Write (Word)", "audio": "HELMET.", "kunci": "HELMET."},
        {"tipe": "Listen & Write (Sentence)", "audio": "START THE ENGINE.", "kunci": "START THE ENGINE."},
        {"tipe": "Listen & Write (Sentence)", "audio": "CHECK THE CHAIN.", "kunci": "CHECK THE CHAIN."},
        {"tipe": "Listen & Write (Sentence)", "audio": "CLEAN THE AIR FILTER.", "kunci": "CLEAN THE AIR FILTER."},
        {"tipe": "Listen & Answer", "audio": "What do we wear on our head before riding?", "kunci": "Helmet"},
        {"tipe": "Listen & Answer", "audio": "What do we use to see behind us?", "kunci": "Mirror"}
    ],
    "AK (Akuntansi)": [
        {"tipe": "Listen & Write (Word)", "audio": "INVOICE.", "kunci": "INVOICE."},
        {"tipe": "Listen & Write (Sentence)", "audio": "COUNT THE MONEY.", "kunci": "COUNT THE MONEY."},
        {"tipe": "Listen & Write (Sentence)", "audio": "CHECK THE REPORT.", "kunci": "CHECK THE REPORT."},
        {"tipe": "Listen & Write (Sentence)", "audio": "SAVE THE RECEIPT.", "kunci": "SAVE THE RECEIPT."},
        {"tipe": "Listen & Answer", "audio": "What tool do we use to calculate numbers?", "kunci": "Calculator"}
    ],
    "TKJ (Teknik Komputer dan Jaringan)": [
        {"tipe": "Listen & Write (Word)", "audio": "ROUTER.", "kunci": "ROUTER."},
        {"tipe": "Listen & Write (Sentence)", "audio": "RESTART THE COMPUTER.", "kunci": "RESTART THE COMPUTER."},
        {"tipe": "Listen & Write (Sentence)", "audio": "CHECK THE CABLE.", "kunci": "CHECK THE CABLE."},
        {"tipe": "Listen & Write (Sentence)", "audio": "CONNECT TO WIFI.", "kunci": "CONNECT TO WIFI."},
        {"tipe": "Listen & Answer", "audio": "What do we use to type on a computer?", "kunci": "Keyboard"}
    ],
    "DPB (Desain dan Produksi Busana)": [
        {"tipe": "Listen & Write (Word)", "audio": "FABRIC.", "kunci": "FABRIC."},
        {"tipe": "Listen & Write (Sentence)", "audio": "CUT THE PATTERN.", "kunci": "CUT THE PATTERN."},
        {"tipe": "Listen & Write (Sentence)", "audio": "MEASURE THE SIZE.", "kunci": "MEASURE THE SIZE."},
        {"tipe": "Listen & Write (Sentence)", "audio": "SEW THE BUTTON.", "kunci": "SEW THE BUTTON."},
        {"tipe": "Listen & Answer", "audio": "What sharp tool is used to cut fabric?", "kunci": "Scissors"}
    ],
    "APHP (Agribisnis Pengolahan Hasil Pertanian)": [
        {"tipe": "Listen & Write (Word)", "audio": "GLOVES.", "kunci": "GLOVES."},
        {"tipe": "Listen & Write (Sentence)", "audio": "WASH THE FRUIT.", "kunci": "WASH THE FRUIT."},
        {"tipe": "Listen & Write (Sentence)", "audio": "WEAR A HAIRNET.", "kunci": "WEAR A HAIRNET."},
        {"tipe": "Listen & Write (Sentence)", "audio": "SEAL THE PACKAGE.", "kunci": "SEAL THE PACKAGE."},
        {"tipe": "Listen & Answer", "audio": "Where do we store food to keep it cold?", "kunci": "Refrigerator"}
    ]
}

# 1. Input Identitas & Jurusan Siswa
nama_siswa = st.text_input("Nama Siswa / Kelompok:", placeholder="Masukkan nama lengkap atau nama kelompok...")
jurusan = st.selectbox("Pilih Jurusan:", list(bank_wajib.keys()))

# Inisialisasi soal acak
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
        with st.spinner("Gemini membuat soal pendek khusus untukmu..."):
            res = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"Buatkan 1 kalimat instruksi kerja sangat sederhana dalam Bahasa Inggris (3-5 kata saja) untuk siswa SMK jurusan {jurusan}. Berikan HANYA kalimat Bahasa Inggrisnya saja tanpa tanda kutip."
            )
            kalimat_baru = res.text.strip()
            st.session_state.soal_sekarang = {
                "tipe": "Listen & Write (AI Unique)",
                "audio": kalimat_baru,
                "kunci": kalimat_baru
            }
            st.rerun()

soal = st.session_state.soal_sekarang

# 2. Pemutar Audio (Normal & Mode Lambat)
st.markdown("---")
st.subheader(f"🎧 Tipe Tantangan: {soal['tipe']}")

if "Listen & Answer" in soal["tipe"]:
    st.info("👂 Dengarkan pertanyaan berikut, lalu **ketik jawaban singkatnya (1 kata)** dalam Bahasa Inggris!")
else:
    st.info("👂 Dengarkan audio berikut dengan saksama, lalu **ketik persis kata/kalimat yang kamu dengar**!")

kecepatan = st.checkbox("🐢 Putar Audio Lebih Lambat (Slow Mode)")

tts = gTTS(text=soal["audio"], lang='en', slow=kecepatan)
audio_fp = io.BytesIO()
tts.write_to_fp(audio_fp)
audio_fp.seek(0)
st.audio(audio_fp, format="audio/mp3")

# 3. Kolom Menulis Jawaban & Penilaian Otomatis
st.markdown("---")
st.subheader("⌨️ Tulis Jawabanmu")
jawaban_siswa = st.text_input("Ketik di sini:", placeholder="Tulis apa yang kamu dengar dalam Bahasa Inggris...")

def bersihkan_teks(teks):
    return re.sub(r'[^\w\s]', '', teks).strip().lower()

if st.button("✅ Periksa Jawaban & Lihat Skor", type="primary", use_container_width=True):
    if not nama_siswa.strip():
        st.warning("⚠️ Isi **Nama Siswa / Kelompok** di bagian atas terlebih dahulu agar nilaimu tercatat!")
    elif not jawaban_siswa.strip():
        st.warning("⚠️ Silakan ketik jawabanmu terlebih dahulu!")
    else:
        bersih_siswa = bersihkan_teks(jawaban_siswa)
        bersih_kunci = bersihkan_teks(soal["kunci"])
        
        kemiripan = difflib.SequenceMatcher(None, bersih_siswa, bersih_kunci).ratio()
        skor = round(kemiripan * 100)
        
        # Simpan nilai ke rekap bersama
        rekap_kelas.append({
            "Nama": nama_siswa.strip().title(),
            "Jurusan": jurusan.split(" ")[0],
            "Soal": soal["audio"],
            "Jawaban Siswa": jawaban_siswa.strip(),
            "Skor": skor
        })
        
        st.markdown(f"### 🏆 Skor {nama_siswa.strip().title()}: **{skor} / 100**")
        
        if skor == 100:
            st.success("🎉 Sempurna! Ejaan (*spelling*) dan pendengaranmu 100% tepat!")
            st.balloons()
        elif skor >= 75:
            st.warning(f"👍 Hampir sempurna! Ada sedikit perbedaan huruf.\n\n**Kunci Jawaban:** `{soal['kunci']}`")
        else:
            st.error(f"💪 Terus berlatih! Dengarkan lagi audionya.\n\n**Teks Audio Asli:** `{soal['audio']}`\n\n**Kunci Jawaban:** `{soal['kunci']}`")

# 4. Panel Rekap Nilai & Leaderboard untuk Pembina
st.markdown("---")
with st.expander("📊 Rekap Nilai & Papan Peringkat Kelas (Review Pembina)"):
    if len(rekap_kelas) > 0:
        df = pd.DataFrame(rekap_kelas)
        
        # Ringkasan total skor per siswa
        leaderboard = df.groupby(["Nama", "Jurusan"], as_index=False).agg(
            Jumlah_Soal=("Skor", "count"),
            Rata_Rata=("Skor", "mean"),
            Total_Poin=("Skor", "sum")
        ).sort_values(by="Total_Poin", ascending=False)
        leaderboard["Rata_Rata"] = leaderboard["Rata_Rata"].round(1)
        
        st.subheader("🏆 Klasemen Sementara")
        st.dataframe(leaderboard, use_container_width=True, hide_index=True)
        
        # Tombol Download ke Excel/CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Semua Detail Jawaban & Nilai (.CSV)",
            data=csv,
            file_name="rekap_listen_and_write.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("Belum ada siswa yang mengirimkan jawaban. Nilai akan otomatis muncul di sini saat siswa menekan tombol Periksa Jawaban.")
