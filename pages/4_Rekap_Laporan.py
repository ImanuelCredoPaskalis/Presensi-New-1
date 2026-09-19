"""
Modul 4: Rekap & Laporan Presensi
Filter rentang tanggal, agregasi durasi jam lab, ekspor Excel (.xlsx), CSV, dan Cetak PDF.
"""

from datetime import datetime, timedelta
import streamlit as st
import pandas as pd

from utils.ui_components import render_global_header, get_status_badge_html
from utils.gsheets_manager import get_sheets_manager
from utils.export_manager import export_to_excel, export_to_csv

render_global_header("Rekap & Laporan")

sm = get_sheets_manager()

# Ambil semua data presensi historis
df_all = sm.get_presensi()
df_master = sm.get_master_mahasiswa()

# =========================================================
# TOP ACTION & OVERVIEW HEADER
# =========================================================
st.markdown(
    """
    <div class="glass-panel" style="margin-bottom: 20px; background: linear-gradient(135deg, rgba(23, 27, 38, 0.95), rgba(15, 19, 29, 0.95)); border: 1px solid rgba(76, 215, 246, 0.2);">
      <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 16px;">
        <div>
          <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
            <span class="badge-cyan">Arsip Telemetri</span>
            <span style="color: #869397;">•</span>
            <span style="font-size: 12px; color: #bcc9cd;">Laboratorium Micro Teaching FisMat</span>
          </div>
          <h2 style="font-family: 'Space Grotesk', sans-serif; font-size: 24px; font-weight: 700; color: #dfe2f1; margin: 0 0 4px 0;">
            Rekapitulasi & Laporan Presensi Mahasiswa
          </h2>
          <p style="font-size: 13px; color: #869397; margin: 0;">
            Arsip riwayat kehadiran, durasi kelas, dan rekap jam kerja laboratorium terintegrasi.
          </p>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Export Suite
exp_col1, exp_col2, exp_col3 = st.columns([4, 4, 4])
with exp_col1:
    excel_file = export_to_excel(df_all, title="Laporan Presensi Mahasiswa Lab Micro Teaching FisMat")
    st.download_button(
        "Ekspor ke Excel (.xlsx)",
        data=excel_file,
        file_name="rekap_presensi_mahasiswa_fismat.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        icon=":material/table_view:"
    )

with exp_col2:
    csv_file = export_to_csv(df_all)
    st.download_button(
        "Ekspor ke CSV",
        data=csv_file,
        file_name="rekap_presensi_mahasiswa_fismat.csv",
        mime="text/csv",
        use_container_width=True,
        icon=":material/file_download:"
    )

with exp_col3:
    st.button(
        "Gunakan Print Browser",
        use_container_width=True,
        icon=":material/print:",
        help="Tekan Ctrl+P (Windows/Linux) atau Cmd+P (macOS) untuk mencetak halaman laporan ini."
    )
    st.caption("Gunakan Ctrl+P / Cmd+P untuk menyimpan sebagai PDF.")

st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

# =========================================================
# TELEMETRY STATS STRIP (4 METRIK)
# =========================================================
c1, c2, c3, c4 = st.columns(4)

total_records = len(df_all)
tepat_waktu_count = len(df_all[df_all["Status_Ketepatan"] == "Tepat Waktu"])
ketepatan_pct = round((tepat_waktu_count / total_records * 100), 1) if total_records > 0 else 100.0
total_sesi_luar = len(df_all[(df_all["Jam_Ke_Kelas"] != "-") | (df_all["Jam_Tugas_Luar"] != "-")])

def parse_duration_minutes(value) -> int:
    parts = str(value).replace("j", " ").replace("m", " ").split()
    try:
        if len(parts) >= 2:
            return int(parts[0]) * 60 + int(parts[1])
    except ValueError:
        pass
    return 0

total_minutes = sum(parse_duration_minutes(v) for v in df_all.get("Durasi_Shift", pd.Series(dtype=str)))
avg_minutes = round(total_minutes / total_records) if total_records else 0
kumulatif_shift = f"{total_minutes // 60}j {total_minutes % 60}m"
rerata_shift = f"{avg_minutes // 60}j {avg_minutes % 60}m"

with c1:
    st.markdown(
        f"""
        <div class="glass-panel" style="padding: 14px;">
          <div style="font-family: 'JetBrains Mono'; font-size: 10px; color: #869397; text-transform: uppercase;">Total Catatan</div>
          <div style="font-family: 'Space Grotesk'; font-size: 26px; font-weight: 700; color: #4cd7f6; margin: 4px 0;">{total_records}</div>
          <div style="font-size: 11px; color: #4edea3;">100% Tervalidasi</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        f"""
        <div class="glass-panel" style="padding: 14px;">
          <div style="font-family: 'JetBrains Mono'; font-size: 10px; color: #869397; text-transform: uppercase;">Kumulatif Lab</div>
          <div style="font-family: 'Space Grotesk'; font-size: 26px; font-weight: 700; color: #dfe2f1; margin: 4px 0;">{kumulatif_shift}</div>
          <div style="font-size: 11px; color: #869397;">Rerata {rerata_shift}/sesi</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c3:
    st.markdown(
        f"""
        <div class="glass-panel" style="padding: 14px;">
          <div style="font-family: 'JetBrains Mono'; font-size: 10px; color: #4edea3; text-transform: uppercase;">Ketepatan Waktu</div>
          <div style="font-family: 'Space Grotesk'; font-size: 26px; font-weight: 700; color: #4edea3; margin: 4px 0;">{ketepatan_pct}%</div>
          <div style="font-size: 11px; color: #869397;">Toleransi 15m</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c4:
    st.markdown(
        f"""
        <div class="glass-panel" style="padding: 14px;">
          <div style="font-family: 'JetBrains Mono'; font-size: 10px; color: #c0c1ff; text-transform: uppercase;">Sesi Izin / Luar</div>
          <div style="font-family: 'Space Grotesk'; font-size: 26px; font-weight: 700; color: #c0c1ff; margin: 4px 0;">{total_sesi_luar} Sesi</div>
          <div style="font-size: 11px; color: #bcc9cd;">Semua tervalidasi</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

# =========================================================
# INTEGRATED FILTER DECK
# =========================================================
with st.expander("Filter Riwayat Komprehensif", expanded=True):
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    
    today = datetime.now().date()
    month_ago = today - timedelta(days=30)
    
    with f_col1:
        start_date = st.date_input("Mulai Tanggal:", value=month_ago)
    with f_col2:
        end_date = st.date_input("Sampai Tanggal:", value=today)
    with f_col3:
        mhs_list = ["Semua Mahasiswa"] + list(df_master["Nama_Mahasiswa"].unique()) if not df_master.empty else ["Semua Mahasiswa"]
        sel_mhs = st.selectbox("Mahasiswa:", mhs_list)
    with f_col4:
        sel_status = st.selectbox(
            "Status Sesi:",
            ["Semua Status", "Hadir di Lab", "Sedang di Kelas", "Sedang Tugas", "Pulang"]
        )

# Terapkan Filter
df_rep = df_all.copy()
if "Tanggal" in df_rep.columns:
    df_rep["Tanggal_parsed"] = pd.to_datetime(df_rep["Tanggal"], errors="coerce").dt.date
    df_rep = df_rep[(df_rep["Tanggal_parsed"] >= start_date) & (df_rep["Tanggal_parsed"] <= end_date)]

if sel_mhs != "Semua Mahasiswa":
    df_rep = df_rep[df_rep["Nama_Mahasiswa"] == sel_mhs]

if sel_status != "Semua Status":
    df_rep = df_rep[df_rep["Status_Terkini"] == sel_status]

# =========================================================
# SUMMARY COUNTER BANNER
# =========================================================
st.markdown(
    f"""
    <div style="background: rgba(28, 31, 42, 0.7); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 10px 14px; margin: 14px 0; display: flex; align-items: center; justify-content: space-between;">
      <div style="display: flex; align-items: center; gap: 8px;">
        <span class="badge-cyan">Total Ditemukan: {len(df_rep)} Catatan Presensi</span>
        <span style="color: #869397;">•</span>
        <span style="font-size: 12px; color: #bcc9cd;">Rentang: {start_date.strftime('%d %b %Y')} s/d {end_date.strftime('%d %b %Y')}</span>
      </div>
      <span style="font-size: 11px; color: #869397;">Audit Log Google Sheets</span>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# TABEL LAPORAN TELEMETRI KOMPREHENSIF
# =========================================================
if df_rep.empty:
    st.info("Tidak ada data presensi yang sesuai dengan kriteria filter.")
else:
    report_columns = [
        "Tanggal", "Nama_Mahasiswa", "Program_Studi", "Jam_Masuk", "Sesi_Shift",
        "Nama_Mata_Kuliah", "Durasi_Kelas", "Jam_Tugas_Luar", "Jam_Kembali_Tugas",
        "Jam_Izin_Keluar", "Jam_Keluar", "Durasi_Shift", "Status_Terkini"
    ]
    report_labels = {
        "Tanggal": "Tanggal",
        "Nama_Mahasiswa": "Mahasiswa",
        "Program_Studi": "Program Studi",
        "Jam_Masuk": "Jam Masuk",
        "Sesi_Shift": "Sesi",
        "Nama_Mata_Kuliah": "Rincian Kelas",
        "Durasi_Kelas": "Durasi Kelas",
        "Jam_Tugas_Luar": "Tugas Luar",
        "Jam_Kembali_Tugas": "Kembali Tugas",
        "Jam_Izin_Keluar": "Izin",
        "Jam_Keluar": "Jam Keluar",
        "Durasi_Shift": "Durasi Shift",
        "Status_Terkini": "Status",
    }
    report_data = df_rep[report_columns].rename(columns=report_labels).reset_index(drop=True)
    report_data.index = report_data.index + 1
    report_data.index.name = "No"
    st.dataframe(report_data, use_container_width=True, hide_index=False)
