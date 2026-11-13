import pandas as pd

# Penyimpanan bersama antar seluruh HP siswa
@st.cache_resource
def get_rekap_nilai():
    return []

rekap_kelas = get_rekap_nilai()

# --- (Taruh kode ini di dalam blok 'if st.button("✅ Periksa Jawaban...")' setelah skor dihitung) ---
# rekap_kelas.append({
#     "Nama": nama_siswa if nama_siswa else "Anonim",
#     "Jurusan": jurusan.split(" ")[0],
#     "Soal": soal["audio"],
#     "Jawaban Siswa": jawaban_siswa,
#     "Skor": skor
# })

# --- Taruh kode berikut di bagian PALING BAWAH file app.py ---
st.markdown("---")
with st.expander("📊 Rekap Nilai & Papan Peringkat Kelas (Khusus Pembina)"):
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
            label="📥 Download Detail Jawaban & Nilai (.CSV)",
            data=csv,
            file_name="rekap_listen_and_write.csv",
            mime="text/csv"
        )
    else:
        st.info("Belum ada siswa yang mengirimkan jawaban.")
