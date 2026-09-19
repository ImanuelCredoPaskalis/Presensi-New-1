"""
Modul 5: Pengaturan Sistem & Integrasi Google Sheets
Profil Lab, Parameter Jam Standar, Keamanan PIN Admin SHA-256, dan Tools Google Sheets.
"""

from datetime import datetime
import time
import streamlit as st
import pandas as pd

from utils.ui_components import render_global_header
from utils.gsheets_manager import get_sheets_manager
from utils.auth_helper import is_admin, verify_admin_pin, update_admin_pin, logout_admin

render_global_header("Pengaturan Sistem")

if not is_admin():
    st.info("Halaman ini hanya dapat diakses oleh admin. Silakan masukkan PIN terlebih dahulu dari sidebar.")
    st.stop()

sm = get_sheets_manager()
pengaturan = sm.get_pengaturan()
status_koneksi = sm.get_status()

# =========================================================
# TOP HEADER BANNER
# =========================================================
st.markdown(
    """
    <div class="glass-panel" style="margin-bottom: 20px; background: linear-gradient(135deg, rgba(23, 27, 38, 0.95), rgba(15, 19, 29, 0.95)); border: 1px solid rgba(76, 215, 246, 0.2);">
      <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 16px;">
        <div>
          <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
            <span class="badge-cyan">Sistem Presensi</span>
            <span style="color: #869397;">•</span>
            <span style="font-family: 'JetBrains Mono'; font-size: 11px; color: #bcc9cd;">Node ID: LAB-FM-03</span>
          </div>
          <h2 style="font-family: 'Space Grotesk', sans-serif; font-size: 24px; font-weight: 700; color: #dfe2f1; margin: 0 0 4px 0;">
            Pengaturan Sistem
          </h2>
          <p style="font-size: 13px; color: #869397; margin: 0;">
            Kelola profil laboratorium, jam kehadiran standar, keamanan admin, dan sinkronisasi Google Sheets.
          </p>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

# 2 Kolom Layout
p_left, p_right = st.columns([7, 5], gap="large")

# ----------------- KOLOM KIRI: KOREKSI DATA, PROFIL LAB, JAM SHIFT -----------------
with p_left:
    # 1. KOREKSI CATATAN PRESENSI ADMIN
    with st.container():
        st.markdown(
            """
            <div class="glass-panel" style="margin-bottom: 16px; padding: 16px;">
              <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <span class="material-symbols-outlined" style="color: #4cd7f6; font-size: 22px;">edit_note</span>
                <div>
                  <h4 style="font-family: 'Space Grotesk'; font-size: 16px; font-weight: 700; color: #dfe2f1; margin: 0;">Pusat Koreksi Catatan Presensi</h4>
                  <p style="font-size: 11px; color: #869397; margin: 2px 0 0 0;">Koreksi jam masuk/pulang atau status kehadiran jika ada kekeliruan</p>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        today_str = datetime.now().strftime("%Y-%m-%d")
        df_today_p = sm.get_presensi(today_str)

        if not df_today_p.empty:
            mhs_in_p = list(df_today_p["Nama_Mahasiswa"].unique())
            sel_koreksi_nama = st.selectbox("Pilih Mahasiswa yang Dikoreksi:", mhs_in_p)
            row_koreksi = df_today_p[df_today_p["Nama_Mahasiswa"] == sel_koreksi_nama].iloc[0]

            kc1, kc2 = st.columns(2)
            with kc1:
                edit_jam_masuk = st.text_input("Koreksi Jam Masuk:", value=str(row_koreksi.get("Jam_Masuk", "07:55 WIB")))
            with kc2:
                edit_status = st.selectbox(
                    "Koreksi Status Terkini:",
                    ["Hadir di Lab", "Sedang di Kelas", "Sedang Tugas", "Izin Keluar", "Pulang"],
                    index=["Hadir di Lab", "Sedang di Kelas", "Sedang Tugas", "Izin Keluar", "Pulang"].index(row_koreksi.get("Status_Terkini", "Hadir di Lab")) if row_koreksi.get("Status_Terkini") in ["Hadir di Lab", "Sedang di Kelas", "Sedang Tugas", "Izin Keluar", "Pulang"] else 0
                )

            if st.button("Simpan Koreksi Catatan", type="primary", use_container_width=True):
                pid = row_koreksi.get("ID_Presensi", "")
                sm.update_presensi_row(pid, "Jam_Masuk", edit_jam_masuk)
                sm.update_presensi_row(pid, "Status_Terkini", edit_status)
                st.cache_data.clear()
                st.success(f"Catatan presensi untuk {sel_koreksi_nama} berhasil diperbarui!")
                st.rerun()
        else:
            st.info("Belum ada catatan presensi hari ini untuk dikoreksi.")

    # 2. PROFIL LABORATORIUM
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    with st.container():
        st.markdown(
            """
            <div class="glass-panel" style="margin-bottom: 16px; padding: 16px;">
              <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <span class="material-symbols-outlined" style="color: #4cd7f6; font-size: 22px;">domain</span>
                <div>
                  <h4 style="font-family: 'Space Grotesk'; font-size: 16px; font-weight: 700; color: #dfe2f1; margin: 0;">Profil Laboratorium</h4>
                  <p style="font-size: 11px; color: #869397; margin: 2px 0 0 0;">Identitas instansi dan ruangan pelaksanaan kegiatan</p>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        p_lab_nama = st.text_input("Nama Laboratorium / Prodi:", value=pengaturan.get("lab_name", "Lab Micro Teaching FisMat"))
        p_lab_lokasi = st.text_input("Lokasi / Ruangan:", value=pengaturan.get("lab_location", "Kampus 3"))

        if st.button("Perbarui Profil Lab", use_container_width=True):
            sm.update_pengaturan("lab_name", p_lab_nama)
            sm.update_pengaturan("lab_location", p_lab_lokasi)
            st.success("Profil laboratorium berhasil diperbarui!")
            st.rerun()

    # 3. PARAMETER JAM SHIFT
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    with st.container():
        st.markdown(
            """
            <div class="glass-panel" style="margin-bottom: 16px; padding: 16px;">
              <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <span class="material-symbols-outlined" style="color: #4edea3; font-size: 22px;">schedule</span>
                <div>
                  <h4 style="font-family: 'Space Grotesk'; font-size: 16px; font-weight: 700; color: #dfe2f1; margin: 0;">Parameter Jam Standar Shift</h4>
                  <p style="font-size: 11px; color: #869397; margin: 2px 0 0 0;">Ambang batas kehadiran dan toleransi keterlambatan asisten</p>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        jc1, jc2, jc3 = st.columns(3)
        with jc1:
            inp_jam_masuk = st.text_input("Jam Masuk:", value=pengaturan.get("jam_datang_standar", "07:00"))
        with jc2:
            inp_jam_selesai = st.text_input("Jam Selesai:", value=pengaturan.get("jam_selesai_standar", "18:00"))
        with jc3:
            inp_toleransi = st.selectbox("Toleransi Terlambat:", ["0", "5", "10", "15", "30"], index=3)

        if st.button("Simpan Parameter Shift", use_container_width=True):
            sm.update_pengaturan("jam_datang_standar", inp_jam_masuk)
            sm.update_pengaturan("jam_selesai_standar", inp_jam_selesai)
            sm.update_pengaturan("toleransi_menit", inp_toleransi)
            st.success("Parameter jam standar shift disimpan!")
            st.rerun()

    # 4. KEAMANAN PIN ADMIN
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    with st.container():
        st.markdown(
            """
            <div class="glass-panel" style="margin-bottom: 16px; padding: 16px;">
              <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <span class="material-symbols-outlined" style="color: #c0c1ff; font-size: 22px;">security</span>
                <div>
                  <h4 style="font-family: 'Space Grotesk'; font-size: 16px; font-weight: 700; color: #dfe2f1; margin: 0;">Keamanan & PIN Admin</h4>
                  <p style="font-size: 11px; color: #869397; margin: 2px 0 0 0;">PIN admin untuk mengakses panel pengaturan</p>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        new_pin_admin = st.text_input("PIN Baru Admin:", type="password", placeholder="Ketik PIN baru...")
        if st.button("Perbarui PIN Admin", use_container_width=True):
            if len(new_pin_admin.strip()) >= 4:
                update_admin_pin(new_pin_admin)
                st.success("PIN Admin berhasil diubah!")
            else:
                st.error("PIN minimal 4 karakter!")

# ----------------- KOLOM KANAN: INTEGRASI GOOGLE SHEETS CLOUD -----------------
with p_right:
    st.markdown(
        """
        <div class="glass-panel" style="margin-bottom: 16px; padding: 16px; background: rgba(28, 31, 42, 0.85);">
          <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 10px; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 8px;">
              <span class="material-symbols-outlined" style="color: #4edea3; font-size: 22px;">cloud_sync</span>
              <div>
                <h4 style="font-family: 'Space Grotesk'; font-size: 16px; font-weight: 700; color: #dfe2f1; margin: 0;">Integrasi Google Sheets</h4>
                <p style="font-size: 11px; color: #869397; margin: 2px 0 0 0;">Database Spreadsheet Presensi Mahasiswa</p>
              </div>
            </div>
            <span class="badge-emerald">Google Apps Script</span>
          </div>

          <div style="background: rgba(10, 14, 24, 0.7); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 12px; margin-bottom: 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-weight: 600; color: #dfe2f1; font-size: 13px;">Status Koneksi</span>
              <span class="badge-emerald">Live Ready</span>
            </div>
            <div style="font-size: 11px; color: #869397; margin-top: 4px;">
              Aplikasi mengirim dan menerima data ke Google Sheets melalui URL Web App Apps Script.
            </div>
            <div style="display: flex; gap: 14px; margin-top: 10px; font-family: 'JetBrains Mono'; font-size: 11px; color: #4edea3;">
              <span>• Webhook Mode</span>
              <span>• Latensi: {status_koneksi.get('latency_ms', '-')}ms</span>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    webhook_url_value = st.text_input(
        "URL Web App Google Apps Script",
        value=sm.get_webhook_url(),
        placeholder="https://script.google.com/macros/s/.../exec",
    )

    webhook_col1, webhook_col2 = st.columns(2)
    with webhook_col1:
        if st.button("Simpan URL Webhook", use_container_width=True, icon=":material/save:"):
            sm.update_webhook_url(webhook_url_value)
            st.success("URL webhook disimpan untuk sesi ini. Untuk penyimpanan permanen, tambahkan di Streamlit Secrets.")
    with webhook_col2:
        if st.button("Uji Koneksi Webhook", use_container_width=True, icon=":material/network_check:"):
            with st.spinner("Mengirim percobaan ping ke Apps Script Web App..."):
                result = sm._post_action("ping", {"source": "streamlit_settings"})
                if isinstance(result, dict) and result.get("ok"):
                    st.success("Koneksi ke Google Sheets via Apps Script berhasil.")
                else:
                    error_msg = result.get("error") if isinstance(result, dict) else "Respons tidak valid"
                    st.error(f"Gagal terhubung ke webhook: {error_msg}")

    # Tombol Tarik Data Terbaru
    if st.button("Tarik Data Terbaru dari Sheets", use_container_width=True, icon=":material/cloud_download:"):
        st.cache_data.clear()
        st.success("Data berhasil disinkronkan dari Google Sheets!")
        st.rerun()

    # Tombol Unduh Cadangan / Backup Seluruh Sheet
    all_presensi = sm.get_presensi()
    from utils.export_manager import export_to_excel
    bk_excel = export_to_excel(all_presensi, title="Backup Database Presensi Lab FisMat")
    st.download_button(
        "Unduh Cadangan Database (.xlsx)",
        data=bk_excel,
        file_name="backup_presensi_lab_fismat.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        icon=":material/download:"
    )

    st.markdown(
        """
        <div style="background: rgba(23, 27, 38, 0.6); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 12px; margin-top: 16px;">
          <div style="font-size: 12px; font-weight: 600; color: #4cd7f6; margin-bottom: 4px;">
            <span class="material-symbols-outlined" style="font-size: 14px; vertical-align: middle;">info</span>
            Petunjuk Penyiapan Google Sheets:
          </div>
          <ol style="font-size: 11px; color: #bcc9cd; margin: 0; padding-left: 18px; line-height: 1.6;">
            <li>Unggah <code>migrasi_data_presensi_google_sheets.xlsx</code> ke Google Drive lalu buka sebagai Google Spreadsheet.</li>
            <li>Buka <strong>Extensions → Apps Script</strong>, tempel kode <code>google_apps_script.js</code>, lalu Deploy sebagai <strong>Web App</strong>.</li>
            <li>Salin URL Web App lalu tempelkan ke kolom <strong>URL Web App Google Apps Script</strong>.</li>
          </ol>
        </div>
        """,
        unsafe_allow_html=True
    )
