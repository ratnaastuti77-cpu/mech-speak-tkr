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

# Inisialisasi soal acak & penghitung soal
if "soal_sekarang" not in st.session_state or st.session_state.get("jurusan_aktif") != jurusan:
    st.session_state.soal_sekarang = random.choice(bank_wajib[jurusan])
    st.session_state.jurusan_aktif = jurusan
    st.session_state.nomor_soal = 1
    st.session_state.hasil_terakhir = None

# Tampilkan hasil nilai soal sebelumnya (jika baru saja menjawab)
if st.session_state.get("hasil_terakhir"):
    hasil = st.session_state.hasil_terakhir
    st.markdown(f"### 🏆 Skor Soal Sebelumnya ({hasil['nama']}): **{hasil['skor']} / 100**")
    if hasil["skor"] == 100:
        st.success(f"🎉 Sempurna! Jawabanmu (`{hasil['jawaban']}`) 100% tepat! Sekarang lanjut soal berikutnya di bawah.")
        st.balloons()
    elif hasil["skor"] >= 75:
        st.warning(f"👍 Hampir sempurna! Jawabanmu: `{hasil['jawaban']}` | Kunci: `{hasil['kunci']}`")
    else:
        st.error(f"💪 Belum tepat! Jawabanmu: `{hasil['jawaban']}` | Kunci: `{hasil['kunci']}`")

col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    if st.button("🔀 Lewati / Acak Soal", use_container_width=True):
        st.session_state.soal_sekarang = random.choice(bank_wajib[jurusan])
        st.session_state.nomor_soal += 1
        st.session_state.hasil_terakhir = None
        st.rerun()

with col_btn2:
    if st.button("✨ Buat Soal Unik AI", use_container_width=True):
        with st.spinner("Membuat soal khusus untukmu..."):
            try:
                res = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=f"Buatkan 1 kalimat instruksi kerja sangat sederhana dalam Bahasa Inggris (3-5 kata saja) untuk siswa SMK jurusan {jurusan}. Berikan HANYA kalimat Bahasa Inggrisnya saja tanpa tanda kutip."
                )
                kalimat_baru = res.text.strip()
                st.session_state.soal_sekarang = {
                    "tipe": "Listen & Write (AI Unique)",
                    "audio": kalimat_baru,
                    "kunci": kalimat_baru
                }
                st.session_state.nomor_soal += 1
                st.session_state.hasil_terakhir = None
                st.rerun()
            except Exception:
                st.warning("⚠️ Server AI sedang sibuk. Dialihkan ke Bank Soal Wajib!")
                st.session_state.soal_sekarang = random.choice(bank_wajib[jurusan])

soal = st.session_state.soal_sekarang

# 2. Pemutar Audio (Normal & Mode Lambat)
st.markdown("---")
st.subheader(f"🎧 Soal #{st.session_state.nomor_soal} — {soal['tipe']}")

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

# 3. Kolom Menulis Jawaban & Otomatis Lanjut Soal Berikutnya
st.markdown("---")
st.subheader("⌨️ Tulis Jawabanmu")

# Menggunakan form agar kolom ketik otomatis bersih saat submit & lanjut soal baru
with st.form(key=f"form_soal_{st.session_state.nomor_soal}", clear_on_submit=True):
    jawaban_siswa = st.text_input("Ketik di sini:", placeholder="Tulis apa yang kamu dengar dalam Bahasa Inggris...")
    submit_btn = st.form_submit_button("✅ Kirim Jawaban & Lanjut Soal Berikutnya", type="primary", use_container_width=True)

def bersihkan_teks(teks):
    return re.sub(r'[^\w\s]', '', teks).strip().lower()

if submit_btn:
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
            "Jurusan": jurusan.split(" "),
            "Soal": soal["audio"],
            "Jawaban Siswa": jawaban_siswa.strip(),
            "Skor": skor
        })
        
        # Simpan hasil untuk ditampilkan di bagian atas setelah pindah soal
        st.session_state.hasil_terakhir = {
            "nama": nama_siswa.strip().title(),
            "skor": skor,
            "jawaban": jawaban_siswa.strip(),
            "kunci": soal["kunci"]
        }
        
        # Otomatis pilih soal baru yang berbeda dari soal sebelumnya
        pilihan_soal = [s for s in bank_wajib[jurusan] if s["audio"] != soal["audio"]]
        st.session_state.soal_sekarang = random.choice(pilihan_soal) if pilihan_soal else random.choice(bank_wajib[jurusan])
        st.session_state.nomor_soal += 1
        
        st.rerun()

# 4. Panel Rekap Nilai & Leaderboard untuk Pembina
st.markdown("---")
with st.expander("📊 Rekap Nilai & Papan Peringkat Kelas (Review Pembina)"):
    if len(rekap_kelas) > 0:
        df = pd.DataFrame(rekap_kelas)
        
