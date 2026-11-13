import streamlit as st
from google import genai
from gtts import gTTS
import io
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

# Bank Soal Wajib Berurutan (Tingkat Mudah -> Sedang -> Tanya Jawab)
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

# Fungsi bantu membersihkan tanda baca & huruf kapital
def bersihkan_teks(teks):
    return re.sub(r'[^\w\s]', '', teks).strip().upper()

# 1. Input Identitas & Jurusan Siswa
nama_siswa = st.text_input("Nama Siswa / Kelompok:", placeholder="Masukkan nama lengkap atau nama kelompok...")
jurusan = st.selectbox("Pilih Jurusan:", list(bank_wajib.keys()))

daftar_soal = bank_wajib[jurusan]
total_soal = len(daftar_soal)

# Reset progres jika siswa mengganti jurusan atau baru mulai
if "indeks_soal" not in st.session_state or st.session_state.get("jurusan_aktif") != jurusan:
    st.session_state.indeks_soal = 0
    st.session_state.jurusan_aktif = jurusan
    st.session_state.riwayat_sesi = []
    st.session_state.hasil_terakhir = None

# ==============================================================================
# KONDISI A: SEMUA SOAL SUDAH SELESAI -> TAMPILKAN NILAI PEROLEHAN AKHIR
# ==============================================================================
if st.session_state.indeks_soal >= total_soal:
    st.markdown("---")
    st.success(f"🎉 Selamat **{nama_siswa if nama_siswa else 'Siswa'}**! Kamu telah menyelesaikan semua **{total_soal} soal** jurusan **{jurusan}**.")
    st.balloons()
    
    # Hitung nilai rata-rata akhir
    if st.session_state.riwayat_sesi:
        total_skor = sum(item["Skor"] for item in st.session_state.riwayat_sesi)
        nilai_akhir = round(total_skor / total_soal)
        
        st.markdown(f"## 🏆 Nilai Akhir Perolehan: **{nilai_akhir} / 100**")
        
        # Tampilkan rincian jawaban per nomor soal
        st.subheader("📋 Rincian Hasil Pengerjaanmu:")
        df_sesi = pd.DataFrame(st.session_state.riwayat_sesi)
        st.dataframe(df_sesi, use_container_width=True, hide_index=True)
        
        # Simpan nilai akhir ke Leaderboard Kelas (sekali per sesi selesai)
        if not st.session_state.get("sudah_masuk_leaderboard"):
            rekap_kelas.append({
                "Nama": nama_siswa.strip() if nama_siswa.strip() else "Tanpa Nama",
                "Jurusan": jurusan.split(" "),
                "Soal Selesai": f"{total_soal}/{total_soal}",
                "Nilai Akhir": nilai_akhir
            })
            st.session_state.sudah_masuk_leaderboard = True

    if st.button("🔄 Ulangi Latihan dari Soal #1", type="primary", use_container_width=True):
        st.session_state.indeks_soal = 0
        st.session_state.riwayat_sesi = []
        st.session_state.hasil_terakhir = None
        st.session_state.sudah_masuk_leaderboard = False
        st.rerun()

# ==============================================================================
# KONDISI B: MASIH DALAM SESI PENGERJAAN SOAL BERURUTAN (1 s/d TOTAL SOAL)
# ==============================================================================
else:
    idx = st.session_state.indeks_soal
    soal = daftar_soal[idx]
    
    # Progress Bar Urutan Soal
    st.progress((idx) / total_soal, text=f"Progres Pengerjaan: Soal {idx + 1} dari {total_soal}")

    # Tampilkan umpan balik soal sebelumnya (jika baru saja menjawab)
    if st.session_state.get("hasil_terakhir"):
        hasil = st.session_state.hasil_terakhir
        if hasil["skor"] == 100:
            st.success(f"✅ Soal #{idx} Benar (`{hasil['jawaban']}`) — Skor: **100**")
        elif hasil["skor"] >= 75:
            st.warning(f"⚠️ Soal #{idx} Hampir Tepat (`{hasil['jawaban']}` | Kunci: `{hasil['kunci']}`) — Skor: **{hasil['skor']}**")
        else:
            st.error(f"❌ Soal #{idx} Kurang Tepat (`{hasil['jawaban']}` | Kunci: `{hasil['kunci']}`) — Skor: **{hasil['skor']}**")

    # Pemutar Audio
    st.markdown("---")
    st.subheader(f"🎧 Soal #{idx + 1} dari {total_soal} — {soal['tipe']}")

    if "Listen & Answer" in soal["tipe"]:
        st.info("👂 Dengarkan pertanyaan berikut, lalu **ketik jawaban singkatnya (1 kata)** dalam Bahasa Inggris!")
    else:
        st.info("👂 Dengarkan audio berikut dengan saksama, lalu **ketik persis kata/kalimat yang kamu dengar**!")

    kecepatan = st.checkbox("🐢 Putar Audio Lebih Lambat (Slow Mode)", key=f"slow_{idx}")

    tts = gTTS(text=soal["audio"], lang='en', slow=kecepatan)
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
    st.audio(audio_fp, format="audio/mp3")

    # Kolom Menulis Jawaban
    st.markdown("---")
    st.subheader("⌨️ Tulis Jawabanmu")

    with st.form(key=f"form_urut_{jurusan}_{idx}", clear_on_submit=True):
        jawaban_siswa = st.text_input("Ketik di sini:", placeholder="Tulis jawabanmu dalam Bahasa Inggris...")
        tombol_teks = "🏁 Kirim & Lihat Nilai Akhir" if (idx + 1 == total_soal) else "➡️ Kirim & Lanjut Soal Berikutnya"
        submit_btn = st.form_submit_button(tombol_teks, type="primary", use_container_width=True)

    if submit_btn:
        if not nama_siswa.strip():
            st.warning("⚠️ Isi Nama Siswa / Kelompok terlebih dahulu di bagian atas!")
        elif not jawaban_siswa.strip():
            st.warning("⚠️ Ketik jawabanmu terlebih dahulu sebelum mengirim!")
        else:
            kunci_bersih = bersihkan_teks(soal["kunci"])
            jawab_bersih = bersihkan_teks(jawaban_siswa)
            
            rasio = difflib.SequenceMatcher(None, kunci_bersih, jawab_bersih).ratio()
            skor = round(rasio * 100)
            
            st.session_state.hasil_terakhir = {
                "jawaban": jawaban_siswa.strip(),
                "kunci": soal["kunci"],
                "skor": skor
            }
            
            st.session_state.riwayat_sesi.append({
                "No": idx + 1,
