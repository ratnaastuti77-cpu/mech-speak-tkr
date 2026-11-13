import streamlit as st
from gtts import gTTS
import io
import difflib
import re
import csv

# Konfigurasi Halaman
st.set_page_config(page_title="LISTEN & WRITE", page_icon="✍️", layout="centered")

st.title("✍️ LISTEN & WRITE")
st.caption("Asesmen Listening & Spelling Kejuruan English Club (10 Soal Berurutan / Jurusan)")

# Penyimpanan Rekap Nilai Bersama di Server (Real-Time)
@st.cache_resource
def get_rekap_nilai():
    return []

rekap_kelas = get_rekap_nilai()

# Bank Soal Wajib (10 Soal Berurutan dari Nomor 1 sampai 10 per Jurusan)
bank_wajib = {
    "TKR (Teknik Kendaraan Ringan)": [
        {"tipe": "Listen & Write (Word)", "audio": "TIRE.", "kunci": "TIRE."},
        {"tipe": "Listen & Write (Word)", "audio": "ENGINE.", "kunci": "ENGINE."},
        {"tipe": "Listen & Write (Word)", "audio": "BATTERY.", "kunci": "BATTERY."},
        {"tipe": "Listen & Write (Sentence)", "audio": "OPEN THE HOOD.", "kunci": "OPEN THE HOOD."},
        {"tipe": "Listen & Write (Sentence)", "audio": "CHECK THE TIRE PRESSURE.", "kunci": "CHECK THE TIRE PRESSURE."},
        {"tipe": "Listen & Write (Sentence)", "audio": "CHANGE THE ENGINE OIL.", "kunci": "CHANGE THE ENGINE OIL."},
        {"tipe": "Listen & Write (Sentence)", "audio": "TEST THE CAR BRAKES.", "kunci": "TEST THE CAR BRAKES."},
        {"tipe": "Listen & Answer", "audio": "What do we use to stop a car?", "kunci": "Brake"},
        {"tipe": "Listen & Answer", "audio": "What part touches the road?", "kunci": "Tire"},
        {"tipe": "Listen & Answer", "audio": "What liquid cools the car engine?", "kunci": "Coolant"}
    ],
    "TSM (Teknik Sepeda Motor)": [
        {"tipe": "Listen & Write (Word)", "audio": "HELMET.", "kunci": "HELMET."},
        {"tipe": "Listen & Write (Word)", "audio": "CHAIN.", "kunci": "CHAIN."},
        {"tipe": "Listen & Write (Word)", "audio": "MIRROR.", "kunci": "MIRROR."},
        {"tipe": "Listen & Write (Sentence)", "audio": "START THE ENGINE.", "kunci": "START THE ENGINE."},
        {"tipe": "Listen & Write (Sentence)", "audio": "CHECK THE CHAIN.", "kunci": "CHECK THE CHAIN."},
        {"tipe": "Listen & Write (Sentence)", "audio": "CLEAN THE AIR FILTER.", "kunci": "CLEAN THE AIR FILTER."},
        {"tipe": "Listen & Write (Sentence)", "audio": "CHECK THE BRAKE FLUID.", "kunci": "CHECK THE BRAKE FLUID."},
        {"tipe": "Listen & Answer", "audio": "What do we wear on our head before riding?", "kunci": "Helmet"},
        {"tipe": "Listen & Answer", "audio": "What do we use to see behind us?", "kunci": "Mirror"},
        {"tipe": "Listen & Answer", "audio": "What liquid protects the motorcycle engine?", "kunci": "Oil"}
    ],
    "AK (Akuntansi)": [
        {"tipe": "Listen & Write (Word)", "audio": "INVOICE.", "kunci": "INVOICE."},
        {"tipe": "Listen & Write (Word)", "audio": "RECEIPT.", "kunci": "RECEIPT."},
        {"tipe": "Listen & Write (Word)", "audio": "PROFIT.", "kunci": "PROFIT."},
        {"tipe": "Listen & Write (Sentence)", "audio": "COUNT THE MONEY.", "kunci": "COUNT THE MONEY."},
        {"tipe": "Listen & Write (Sentence)", "audio": "CHECK THE REPORT.", "kunci": "CHECK THE REPORT."},
        {"tipe": "Listen & Write (Sentence)", "audio": "SAVE THE RECEIPT.", "kunci": "SAVE THE RECEIPT."},
        {"tipe": "Listen & Write (Sentence)", "audio": "RECORD EVERY TRANSACTION.", "kunci": "RECORD EVERY TRANSACTION."},
        {"tipe": "Listen & Answer", "audio": "What tool do we use to calculate numbers?", "kunci": "Calculator"},
        {"tipe": "Listen & Answer", "audio": "Where do we keep business money safely?", "kunci": "Bank"},
        {"tipe": "Listen & Answer", "audio": "What paper proves a customer has paid?", "kunci": "Receipt"}
    ],
    "TKJ (Teknik Komputer dan Jaringan)": [
        {"tipe": "Listen & Write (Word)", "audio": "ROUTER.", "kunci": "ROUTER."},
        {"tipe": "Listen & Write (Word)", "audio": "SERVER.", "kunci": "SERVER."},
        {"tipe": "Listen & Write (Word)", "audio": "CABLE.", "kunci": "CABLE."},
        {"tipe": "Listen & Write (Sentence)", "audio": "RESTART THE COMPUTER.", "kunci": "RESTART THE COMPUTER."},
        {"tipe": "Listen & Write (Sentence)", "audio": "CHECK THE CABLE.", "kunci": "CHECK THE CABLE."},
        {"tipe": "Listen & Write (Sentence)", "audio": "CONNECT TO WIFI.", "kunci": "CONNECT TO WIFI."},
        {"tipe": "Listen & Write (Sentence)", "audio": "INSTALL THE ANTIVIRUS.", "kunci": "INSTALL THE ANTIVIRUS."},
        {"tipe": "Listen & Answer", "audio": "What do we use to type on a computer?", "kunci": "Keyboard"},
        {"tipe": "Listen & Answer", "audio": "What device moves the cursor on the screen?", "kunci": "Mouse"},
        {"tipe": "Listen & Answer", "audio": "What software protects a computer from viruses?", "kunci": "Antivirus"}
    ],
    "DPB (Desain dan Produksi Busana)": [
        {"tipe": "Listen & Write (Word)", "audio": "FABRIC.", "kunci": "FABRIC."},
        {"tipe": "Listen & Write (Word)", "audio": "NEEDLE.", "kunci": "NEEDLE."},
        {"tipe": "Listen & Write (Word)", "audio": "BUTTON.", "kunci": "BUTTON."},
        {"tipe": "Listen & Write (Sentence)", "audio": "CUT THE PATTERN.", "kunci": "CUT THE PATTERN."},
        {"tipe": "Listen & Write (Sentence)", "audio": "MEASURE THE SIZE.", "kunci": "MEASURE THE SIZE."},
        {"tipe": "Listen & Write (Sentence)", "audio": "SEW THE BUTTON.", "kunci": "SEW THE BUTTON."},
        {"tipe": "Listen & Write (Sentence)", "audio": "IRON THE CLOTHES.", "kunci": "IRON THE CLOTHES."},
        {"tipe": "Listen & Answer", "audio": "What sharp tool is used to cut fabric?", "kunci": "Scissors"},
        {"tipe": "Listen & Answer", "audio": "What machine is used to sew clothes?", "kunci": "Sewing machine"},
        {"tipe": "Listen & Answer", "audio": "What material is used to make a shirt?", "kunci": "Fabric"}
    ],
    "APHP (Agribisnis Pengolahan Hasil Pertanian)": [
        {"tipe": "Listen & Write (Word)", "audio": "GLOVES.", "kunci": "GLOVES."},
        {"tipe": "Listen & Write (Word)", "audio": "FRESH.", "kunci": "FRESH."},
        {"tipe": "Listen & Write (Word)", "audio": "PACKAGE.", "kunci": "PACKAGE."},
        {"tipe": "Listen & Write (Sentence)", "audio": "WASH THE FRUIT.", "kunci": "WASH THE FRUIT."},
        {"tipe": "Listen & Write (Sentence)", "audio": "WEAR A HAIRNET.", "kunci": "WEAR A HAIRNET."},
        {"tipe": "Listen & Write (Sentence)", "audio": "SEAL THE PACKAGE.", "kunci": "SEAL THE PACKAGE."},
        {"tipe": "Listen & Write (Sentence)", "audio": "CHECK THE EXPIRY DATE.", "kunci": "CHECK THE EXPIRY DATE."},
        {"tipe": "Listen & Answer", "audio": "Where do we store food to keep it cold?", "kunci": "Refrigerator"},
        {"tipe": "Listen & Answer", "audio": "What do we wear on our hands when processing food?", "kunci": "Gloves"},
        {"tipe": "Listen & Answer", "audio": "What process heats milk to kill bacteria?", "kunci": "Pasteurization"}
    ]
}

def bersihkan_teks(teks):
    return re.sub(r'[^\w\s]', '', teks).strip().lower()

# 1. Input Identitas & Jurusan Siswa
nama_siswa = st.text_input("Nama Lengkap Siswa / Kelompok:", key="input_nama", placeholder="Contoh: Budi Santoso (atau Kelompok 1)")
jurusan = st.selectbox("Pilih Jurusan:", list(bank_wajib.keys()), key="pilih_jurusan")

daftar_soal = bank_wajib[jurusan]
total_soal = len(daftar_soal)

# Inisialisasi Sesi Siswa (Berurutan dari Soal Nomor 1)
if "index_soal" not in st.session_state or st.session_state.get("jurusan_aktif") != jurusan:
    st.session_state.index_soal = 0
    st.session_state.jurusan_aktif = jurusan
    st.session_state.hasil_terakhir = None
    st.session_state.skor_sesi = []
    st.session_state.pesan_error = ""

# Callback Saat Tombol Kirim Diklik (Otomatis Lanjut ke Nomor Berikutnya)
def proses_jawaban():
    nama_val = st.session_state.get("input_nama", "").strip()
    jawaban_val = st.session_state.get("input_jawaban", "").strip()
    idx_sekarang = st.session_state.index_soal

    if not nama_val:
        st.session_state.pesan_error = "⚠️ Isi **Nama Lengkap Siswa / Kelompok** di bagian atas terlebih dahulu!"
        return
    if not jawaban_val:
        st.session_state.pesan_error = "⚠️ Silakan ketik jawabanmu terlebih dahulu!"
        return

    st.session_state.pesan_error = ""
    soal_sekarang = daftar_soal[idx_sekarang]

    bersih_siswa = bersihkan_teks(jawaban_val)
    bersih_kunci = bersihkan_teks(soal_sekarang["kunci"])

    kemiripan = difflib.SequenceMatcher(None, bersih_siswa, bersih_kunci).ratio()
    skor = round(kemiripan * 100)
    nama_bersih = nama_val.title()

    # Simpan ke rekap pembina
    rekap_kelas.append({
        "nama": nama_bersih,
        "jurusan": jurusan,
        "no_soal": idx_sekarang + 1,
        "soal": soal_sekarang["audio"],
        "jawaban": jawaban_val,
        "skor": skor
    })

    st.session_state.skor_sesi.append(skor)
    st.session_state.hasil_terakhir = {
        "nomor": idx_sekarang + 1,
        "nama": nama_bersih,
        "skor": skor,
        "jawaban": jawaban_val,
        "kunci": soal_sekarang["kunci"]
    }

    # Pindah ke nomor soal berikutnya & kosongkan kotak ketik
    st.session_state.index_soal += 1
    st.session_state.input_jawaban = ""

if st.session_state.get("pesan_error"):
    st.warning(st.session_state.pesan_error)

# Umpan Balik Skor Soal Sebelumnya
if st.session_state.get("hasil_terakhir"):
    hasil = st.session_state.hasil_terakhir
    st.markdown(f"### 🏆 Skor Soal #{hasil['nomor']} ({hasil['nama']}): **{hasil['skor']} / 100**")
    if hasil["skor"] == 100:
        st.success(f"🎉 Sempurna! Jawabanmu (`{hasil['jawaban']}`) 100% tepat!")
    elif hasil["skor"] >= 75:
        st.warning(f"👍 Hampir tepat! Jawabanmu: `{hasil['jawaban']}` | Kunci: `{hasil['kunci']}`")
    else:
        st.error(f"💪 Belum tepat! Jawabanmu: `{hasil['jawaban']}` | Kunci: `{hasil['kunci']}`")

# 2. Area Mengerjakan Soal (Berurutan Nomor 1 sampai Selesai)
