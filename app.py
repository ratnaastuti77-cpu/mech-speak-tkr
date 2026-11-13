import streamlit as st
from gtts import gTTS
import io
import difflib
import re
import pandas as pd

# Konfigurasi Halaman
st.set_page_config(page_title="LISTEN & WRITE", page_icon="✍️", layout="centered")

st.title("✍️ LISTEN & WRITE")
st.caption("Latihan Listening & Spelling Kejuruan English Club")

# Penyimpanan Rekap Nilai Bersama (Real-Time Leaderboard)
@st.cache_resource
def get_rekap_nilai():
    return []

rekap_kelas = get_rekap_nilai()

# Bank Soal Wajib (Berurutan dari Mudah ke Sedang untuk Semua Jurusan)
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

daftar_soal = bank_wajib[jurusan]
total_soal = len(daftar_soal)

# Inisialisasi urutan soal (mulai dari index 0 / Soal ke-1)
if "index_soal" not in st.session_state or st.session_state.get("jurusan_aktif") != jurusan:
    st.session_state.index_soal = 0
    st.session_state.jurusan_aktif = jurusan
    st.session_state.hasil_terakhir = None
    st.session_state.skor_sesi = []

# Tampilkan hasil nilai soal sebelumnya (jika baru saja menjawab)
if st.session_state.get("hasil_terakhir"):
    hasil = st.session_state.hasil_terakhir
    st.markdown(f"### 🏆 Skor Soal #{hasil['nomor']} ({hasil['nama']}): **{hasil['skor']} / 100**")
    if hasil["skor"] == 100:
        st.success(f"🎉 Sempurna! Jawabanmu (`{hasil['jawaban']}`) 100% tepat!")
        st.balloons()
    elif hasil["skor"] >= 75:
        st.warning(f"👍 Hampir sempurna! Jawabanmu: `{hasil['jawaban']}` | Kunci: `{hasil['kunci']}`")
    else:
        st.error(f"💪 Belum tepat! Jawabanmu: `{hasil['jawaban']}` | Kunci: `{hasil['kunci']}`")

def bersihkan_teks(teks):
    return re.sub(r'[^\w\s]', '', teks).strip().lower()

# Cek apakah semua soal sudah selesai dikerjakan
if st.session_state.index_soal < total_soal:
    idx = st.session_state.index_soal
    soal = daftar_soal[idx]

    # Progress bar & info nomor soal
    st.progress((idx) / total_soal)
    st.subheader(f"🎧 Soal {idx + 1} dari {total_soal} — {soal['tipe']}")

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

    # Kolom Menulis Jawaban & Otomatis Lanjut Soal Berikutnya
    st.markdown("---")
    with st.form(key=f"form_soal_{idx}", clear_on_submit=True):
        jawaban_siswa = st.text_input("⌨️ Ketik jawabanmu di sini:", placeholder="Tulis apa yang kamu dengar dalam Bahasa Inggris...")
        submit_btn = st.form_submit_button("✅ Kirim Jawaban & Lanjut", type="primary", use_container_width=True)

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
                "No_Soal": idx + 1,
                "Soal": soal["audio"],
                "Jawaban Siswa": jawaban_siswa.strip(),
                "Skor": skor
            })

            st.session_state.skor_sesi.append(skor)
            st.session_state.hasil_terakhir = {
                "nomor": idx + 1,
                "nama": nama_siswa.strip().title(),
                "skor": skor,
                "jawaban": jawaban_siswa.strip(),
                "kunci": soal["kunci"]
            }

            # Maju ke nomor soal berikutnya secara berurutan
            st.session_state.index_soal += 1
            st.rerun()

else:
    # Tampilan saat seluruh soal selesai dikerjakan
    st.progress(1.0)
    st.markdown("---")
    rata_akhir = round(sum(st.session_state.skor_sesi) / total_soal, 1) if st.session_state.skor_sesi else 0
    total_poin = sum(st.session_state.skor_sesi)

    st.success(f"🎊 **Selamat, {nama_siswa.strip().title() if nama_siswa else 'Kamu'}!** Semua **{total_soal} soal** jurusan **{jurusan}** telah selesai dikerjakan!")
    st.metric(label="Total Poin / Rata-Rata Akhir", value=f"{total_poin} Poin (Rata-rata: {rata_akhir})")

    if st.button("🔄 Ulangi dari Soal Nomor 1", use_container_width=True):
        st.session_state.index_soal = 0
        st.session_state.hasil_terakhir = None
        st.session_state.skor_sesi = []
        st.rerun()

# Panel Rekap Nilai & Leaderboard untuk Pembina
st.markdown("---")
with st.expander("📊 Rekap Nilai & Papan Peringkat Kelas (Review Pembina)"):
    if len(rekap_kelas) > 0:
        df = pd.DataFrame(rekap_kelas)

        leaderboard = df.groupby(["Nama", "Jurusan"], as_index=False).agg(
            Jumlah_Soal=("Skor", "count"),
            Rata_Rata=("Skor", "mean"),
            Total_Poin=("Skor", "sum")
        ).sort_values(by="Total_Poin", ascending=False)
        leaderboard["Rata_Rata"] = leaderboard["Rata_Rata"].round(1)

        st.subheader("🏆 Klasemen Sementara")
        st.dataframe(leaderboard, use_container_width=True, hide_index=True)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Semua Detail Jawaban & Nilai (.CSV)",
            data=csv,
            file_name="rekap_listen_and_write.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
