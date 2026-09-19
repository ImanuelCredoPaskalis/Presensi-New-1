"""
Modul 1: Presensi Mahasiswa
Pencatatan presensi real-time 8-aksi dengan Google Sheets.
"""

from datetime import datetime
import streamlit as st
import pandas as pd

from utils.ui_components import render_global_header, render_telemetry_banner, get_status_badge_html, safe_html
from utils.gsheets_manager import get_sheets_manager

render_global_header("Presensi Mahasiswa")

sm = get_sheets_manager()
today_str = datetime.now().strftime("%Y-%m-%d")

# Ambil data master mahasiswa dan data presensi hari ini
df_master = sm.get_master_mahasiswa()
df_presensi = sm.get_presensi(today_str)

# Hitung ringkasan status hari ini
total_mhs = len(df_master)
di_lab_count = len(df_presensi[df_presensi["Status_Terkini"] == "Hadir di Lab"])
kelas_count = len(df_presensi[df_presensi["Status_Terkini"] == "Sedang di Kelas"])
tugas_count = len(df_presensi[df_presensi["Status_Terkini"] == "Sedang Tugas"])

render_telemetry_banner(
    title="Presensi Mahasiswa Hari Ini",
    subtitle="Pencatatan kehadiran 1-klik, audit pergerakan kelas, tugas luar, dan durasi asisten laboratorium.",
    extra_metric_val=f"{total_mhs} Asisten",
    extra_metric_lbl="Total Terdaftar"
)

# Inisialisasi session state untuk feedback & input dinamis
if "last_action_feedback" not in st.session_state:
    st.session_state["last_action_feedback"] = None

# =========================================================
# DUAL-PANEL GRID: SELECTOR & 8-ACTION MATRIX
# =========================================================
col_left, col_right = st.columns([5, 7], gap="large")

# ----------------- KOLOM KIRI: PILIH MAHASISWA -----------------
with col_left:
    st.markdown(
        """
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
          <div style="display: flex; align-items: center; gap: 8px;">
            <span class="material-symbols-outlined" style="color: #4cd7f6; font-size: 20px;">person_search</span>
            <div>
              <div style="font-family: 'JetBrains Mono'; font-size: 10px; color: #869397; text-transform: uppercase;">Langkah 1</div>
              <div style="font-family: 'Space Grotesk'; font-size: 18px; font-weight: 700; color: #dfe2f1;">Pilih Mahasiswa</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Filter daftar mahasiswa aktif saja
    active_mhs = df_master[df_master["Status_Aktif"] == "Aktif"] if "Status_Aktif" in df_master.columns else df_master
    nama_options = list(active_mhs["Nama_Mahasiswa"].unique()) if not active_mhs.empty else ["Audrey Sabrina"]

    selected_nama = st.selectbox(
        "Pilih Mahasiswa:",
        options=nama_options,
        index=0,
        label_visibility="collapsed"
    )

    # Ambil info mahasiswa terpilih
    mhs_info = active_mhs[active_mhs["Nama_Mahasiswa"] == selected_nama].iloc[0] if not active_mhs.empty and selected_nama in active_mhs["Nama_Mahasiswa"].values else None
    prodi_val = mhs_info["Program_Studi"] if mhs_info is not None else "Pendidikan Fisika"
    avatar_val = mhs_info["Avatar_Initials"] if mhs_info is not None else selected_nama[:2].upper()

    # Cek status kehadiran hari ini
    today_record = df_presensi[df_presensi["Nama_Mahasiswa"] == selected_nama]
    if not today_record.empty:
        cur_row = today_record.iloc[0]
        cur_status = cur_row.get("Status_Terkini", "Belum Presensi")
        jam_masuk = cur_row.get("Jam_Masuk", "--:--")
        durasi_aktif = cur_row.get("Durasi_Shift", "--")
    else:
        cur_status = "Belum Presensi"
        jam_masuk = "--:--"
        durasi_aktif = "--"

    badge_html = get_status_badge_html(cur_status)
    avatar_html = safe_html(avatar_val)
    nama_html = safe_html(selected_nama)
    prodi_html = safe_html(prodi_val)
    jam_masuk_html = safe_html(jam_masuk)
    durasi_aktif_html = safe_html(durasi_aktif)

    # Kartu Profil Mahasiswa Terpilih
    st.markdown(
        f"""
        <div class="glass-panel" style="margin-top: 12px; background: rgba(28, 31, 42, 0.7); border: 1px solid rgba(76, 215, 246, 0.25);">
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px;">
            <div style="display: flex; align-items: center; gap: 12px;">
              <div style="width: 44px; height: 44px; border-radius: 10px; background: rgba(76, 215, 246, 0.15); border: 1px solid rgba(76, 215, 246, 0.3); display: flex; align-items: center; justify-content: center; font-family: 'Space Grotesk'; font-size: 18px; font-weight: 700; color: #4cd7f6;">
                {avatar_html}
              </div>
              <div>
                <div style="font-family: 'Space Grotesk'; font-size: 16px; font-weight: 700; color: #dfe2f1;">{nama_html}</div>
                <div style="font-size: 12px; color: #869397;">{prodi_html}</div>
              </div>
            </div>
            {badge_html}
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px;">
            <div style="background: rgba(23, 27, 38, 0.7); padding: 8px 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06);">
              <span style="font-size: 11px; color: #869397; font-family: 'JetBrains Mono';">Jam Masuk Lab:</span>
              <div style="font-family: 'JetBrains Mono'; font-size: 14px; font-weight: 600; color: #4edea3; margin-top: 2px;">{jam_masuk_html}</div>
            </div>
            <div style="background: rgba(23, 27, 38, 0.7); padding: 8px 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06);">
              <span style="font-size: 11px; color: #869397; font-family: 'JetBrains Mono';">Durasi Aktif:</span>
              <div style="font-family: 'JetBrains Mono'; font-size: 14px; font-weight: 600; color: #4cd7f6; margin-top: 2px;">{durasi_aktif_html}</div>
            </div>
          </div>

          <div style="display: flex; align-items: center; justify-content: space-between; font-size: 11px; color: #869397; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 8px;">
            <span style="display: flex; align-items: center; gap: 4px; color: #4edea3;">
              <span class="material-symbols-outlined" style="font-size: 14px;">verified_user</span> Presensi Terintegrasi
            </span>
            <span style="font-family: 'JetBrains Mono';">Terminal #MT-01</span>
          </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-top: 10px; text-align: center;">
          <div style="background: rgba(28, 31, 42, 0.5); padding: 8px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06);">
            <div style="font-size: 10px; color: #869397; font-family: 'JetBrains Mono';">Di Lab</div>
            <div style="font-size: 18px; font-weight: 700; color: #4edea3; font-family: 'Space Grotesk';">{di_lab_count}</div>
          </div>
          <div style="background: rgba(28, 31, 42, 0.5); padding: 8px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06);">
            <div style="font-size: 10px; color: #869397; font-family: 'JetBrains Mono';">Sesi Kelas</div>
            <div style="font-size: 18px; font-weight: 700; color: #c0c1ff; font-family: 'Space Grotesk';">{kelas_count}</div>
          </div>
          <div style="background: rgba(28, 31, 42, 0.5); padding: 8px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06);">
            <div style="font-size: 10px; color: #869397; font-family: 'JetBrains Mono';">Tugas Luar</div>
            <div style="font-size: 18px; font-weight: 700; color: #4cd7f6; font-family: 'Space Grotesk';">{tugas_count}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ----------------- KOLOM KANAN: MATRIKS 8 AKSI PRESENSI -----------------
with col_right:
    st.markdown(
        """
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
          <div style="display: flex; align-items: center; gap: 8px;">
            <span class="material-symbols-outlined" style="color: #4edea3; font-size: 20px;">touch_app</span>
            <div>
              <div style="font-family: 'JetBrains Mono'; font-size: 10px; color: #869397; text-transform: uppercase;">Langkah 2</div>
              <div style="font-family: 'Space Grotesk'; font-size: 18px; font-weight: 700; color: #dfe2f1;">Pilih Aksi Presensi</div>
            </div>
          </div>
          <span class="badge-cyan"><span class="material-symbols-outlined" style="font-size: 13px;">bolt</span> 1-Klik Rekam</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Input Opsional untuk Keterangan Matkul / Tugas
    with st.expander("Keterangan Tambahan (Opsional untuk Kuliah / Tugas Luar)", expanded=False):
        extra_detail = st.text_input(
            "Mata Kuliah / Deskripsi Tugas Luar:",
            placeholder="Contoh: Fisika Modern (R. 302) atau Ambil Modul di Lab Pusat",
            key="input_extra_detail"
        )

    # Grid 8 tombol dengan label singkat agar stabil pada layar sempit.
    r1c1, r1c2, r1c3, r1c4 = st.columns(4)
    with r1c1:
        if st.button("Jam Masuk", use_container_width=True, key="btn_masuk", help="Catat kedatangan di laboratorium"):
            res = sm.save_action_presensi(selected_nama, "masuk", prodi=prodi_val)
            st.session_state["last_action_feedback"] = res
            st.rerun()

    with r1c2:
        if st.button("Ke Kelas", use_container_width=True, key="btn_kelas", help="Catat mulai sesi kuliah"):
            res = sm.save_action_presensi(selected_nama, "ke-kelas", prodi=prodi_val, extra_info=extra_detail)
            st.session_state["last_action_feedback"] = res
            st.rerun()

    with r1c3:
        if st.button("Tugas Luar", use_container_width=True, key="btn_tugas", help="Catat mulai tugas luar laboratorium"):
            res = sm.save_action_presensi(selected_nama, "tugas-keluar", prodi=prodi_val, extra_info=extra_detail)
            st.session_state["last_action_feedback"] = res
            st.rerun()

    with r1c4:
        if st.button("Izin Keluar", use_container_width=True, key="btn_izin", help="Catat izin sementara"):
            res = sm.save_action_presensi(selected_nama, "izin-keluar", prodi=prodi_val)
            st.session_state["last_action_feedback"] = res
            st.rerun()

    st.markdown("<div style='margin-top: 6px;'></div>", unsafe_allow_html=True)
    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
    with r2c1:
        if st.button("Kembali Kelas", use_container_width=True, key="btn_kembali_kelas", help="Catat selesai sesi kuliah"):
            res = sm.save_action_presensi(selected_nama, "kembali-kelas", prodi=prodi_val)
            st.session_state["last_action_feedback"] = res
            st.rerun()

    with r2c2:
        if st.button("Kembali Tugas", use_container_width=True, key="btn_kembali_tugas", help="Catat selesai tugas luar"):
            res = sm.save_action_presensi(selected_nama, "kembali-tugas", prodi=prodi_val)
            st.session_state["last_action_feedback"] = res
            st.rerun()

    with r2c3:
        if st.button("Kembali Shift", use_container_width=True, key="btn_kembali_shift", help="Catat kembali standby di laboratorium"):
            res = sm.save_action_presensi(selected_nama, "kembali-shift", prodi=prodi_val)
            st.session_state["last_action_feedback"] = res
            st.rerun()

    with r2c4:
        if st.button("Jam Keluar", use_container_width=True, key="btn_pulang", help="Catat selesai shift dan pulang"):
            res = sm.save_action_presensi(selected_nama, "pulang", prodi=prodi_val)
            st.session_state["last_action_feedback"] = res
            st.rerun()

    # Feedback Box Interaktif
    connection_badge = "Tersinkron Google Sheets" if sm.get_status()["online"] else "Tersimpan Mode Lokal"
    fb = st.session_state.get("last_action_feedback")
    if fb:
        st.markdown(
            f"""
            <div style="margin-top: 14px; background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 12px; display: flex; align-items: center; justify-content: space-between;">
              <div style="display: flex; align-items: center; gap: 10px;">
                <span class="material-symbols-outlined" style="color: #4edea3; font-size: 20px;">task_alt</span>
                <div>
                  <div style="font-size: 13px; font-weight: 600; color: #4edea3;">{fb.get('message', 'Aksi berhasil!')}</div>
                  <div style="font-size: 11px; color: #bcc9cd;">Target: <strong>{fb.get('target', '')}</strong> • Status Baru: <strong>{fb.get('status', '')}</strong></div>
                </div>
              </div>
              <span class="badge-emerald">{connection_badge}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div style="margin-top: 14px; background: rgba(28, 31, 42, 0.6); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 10px 14px; display: flex; align-items: center; justify-content: space-between;">
              <span style="font-size: 12px; color: #869397;">
                <span class="material-symbols-outlined" style="font-size: 14px; vertical-align: middle;">info</span>
                Siap merekam. Pilih mahasiswa lalu tekan salah satu tombol aksi.
              </span>
              <span style="font-family: 'JetBrains Mono'; font-size: 11px; color: #4cd7f6;">Target: {selected_nama}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

# =========================================================
# TABEL RIWAYAT PRESENSI HARI INI (LIVE REAL-TIME)
# =========================================================
st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
st.markdown(
    """
    <div style="display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 12px;">
      <div>
        <div style="display: flex; align-items: center; gap: 8px;">
          <h3 style="font-family: 'Space Grotesk'; font-size: 18px; font-weight: 700; color: #dfe2f1; margin: 0;">Riwayat & Status Presensi Hari Ini</h3>
          <span class="badge-emerald"><span class="pulse-emerald"></span> Live Sync</span>
        </div>
        <p style="font-size: 12px; color: #869397; margin: 2px 0 0 0;">Monitoring kehadiran dan pergerakan asisten laboratorium micro teaching terdaftar.</p>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Toolbar Filter Cepat & Search
tcol1, tcol2 = st.columns([8, 4])
with tcol1:
    filter_status = st.radio(
        "Filter Cepat:",
        ["Semua", "Hadir di Lab", "Sedang di Kelas", "Sedang Tugas"],
        horizontal=True,
        label_visibility="collapsed"
    )
with tcol2:
    search_query = st.text_input(
        "Cari Mahasiswa:",
        placeholder="Cari nama mahasiswa...",
        label_visibility="collapsed"
    )

# Filter data tabel
df_display = df_presensi.copy()
if filter_status != "Semua":
    df_display = df_display[df_display["Status_Terkini"] == filter_status]
if search_query:
    df_display = df_display[df_display["Nama_Mahasiswa"].str.contains(search_query, case=False, na=False)]

if df_display.empty:
    st.info("Belum ada data presensi yang sesuai dengan filter hari ini.")
else:
    # Gunakan tabel native Streamlit agar markup HTML tidak dibaca sebagai blok kode.
    table_columns = [
        "Nama_Mahasiswa", "Program_Studi", "Jam_Masuk", "Nama_Mata_Kuliah",
        "Durasi_Kelas", "Jam_Tugas_Luar", "Jam_Kembali_Tugas",
        "Jam_Izin_Keluar", "Durasi_Shift", "Status_Terkini"
    ]
    table_labels = {
        "Nama_Mahasiswa": "Nama Mahasiswa",
        "Program_Studi": "Program Studi",
        "Jam_Masuk": "Jam Masuk",
        "Nama_Mata_Kuliah": "Mata Kuliah",
        "Durasi_Kelas": "Durasi Kelas",
        "Jam_Tugas_Luar": "Tugas Luar",
        "Jam_Kembali_Tugas": "Kembali Tugas",
        "Jam_Izin_Keluar": "Izin",
        "Durasi_Shift": "Durasi Shift",
        "Status_Terkini": "Status Terkini",
    }
    table_data = df_display[table_columns].rename(columns=table_labels).reset_index(drop=True)
    table_data.index = table_data.index + 1
    table_data.index.name = "No"
    st.dataframe(table_data, use_container_width=True, hide_index=False)
