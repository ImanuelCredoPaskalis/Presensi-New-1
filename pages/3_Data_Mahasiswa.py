"""
Modul 3: Manajemen Data Mahasiswa
Master CRUD asisten laboratorium (Nama, Program Studi, dan Status Keaktifan).
"""

import streamlit as st
import pandas as pd

from utils.ui_components import render_global_header
from utils.gsheets_manager import get_sheets_manager
from utils.auth_helper import is_admin, verify_admin_pin
from utils.export_manager import export_to_excel, export_to_csv

render_global_header("Data Mahasiswa")

sm = get_sheets_manager()
df_master = sm.get_master_mahasiswa()

# =========================================================
# TOP COMMAND & ACTION BAR
# =========================================================
st.markdown(
    """
    <div class="glass-panel" style="margin-bottom: 20px; background: linear-gradient(135deg, rgba(23, 27, 38, 0.95), rgba(15, 19, 29, 0.95)); border: 1px solid rgba(76, 215, 246, 0.2);">
      <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 16px;">
        <div style="display: flex; align-items: center; gap: 14px;">
          <div style="width: 48px; height: 48px; border-radius: 12px; background: rgba(76, 215, 246, 0.15); border: 1px solid rgba(76, 215, 246, 0.3); display: flex; align-items: center; justify-content: center; color: #4cd7f6;">
            <span class="material-symbols-outlined" style="font-size: 28px;">school</span>
          </div>
          <div>
            <div style="display: flex; align-items: center; gap: 8px;">
              <h2 style="font-family: 'Space Grotesk', sans-serif; font-size: 22px; font-weight: 700; color: #dfe2f1; margin: 0;">
                Manajemen Data Mahasiswa
              </h2>
              <span class="badge-cyan">Master Lab FisMat</span>
            </div>
            <p style="font-size: 13px; color: #869397; margin: 3px 0 0 0;">
              Daftar asisten aktif, program studi pengampu, dan status keanggotaan laboratorium.
            </p>
          </div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Tombol Aksi: Tambah Asisten, Ekspor Excel & CSV
act_col1, act_col2, act_col3 = st.columns([4, 4, 4])
with act_col1:
    open_add_modal = st.button("Tambah Asisten Baru", use_container_width=True, icon=":material/person_add:")

with act_col2:
    excel_bytes = export_to_excel(df_master, title="Master Data Mahasiswa Asisten Lab FisMat")
    st.download_button(
        "Ekspor Excel (.xlsx)",
        data=excel_bytes,
        file_name="master_mahasiswa_fismat.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        icon=":material/table_view:"
    )

with act_col3:
    csv_bytes = export_to_csv(df_master)
    st.download_button(
        "Ekspor CSV",
        data=csv_bytes,
        file_name="master_mahasiswa_fismat.csv",
        mime="text/csv",
        use_container_width=True,
        icon=":material/file_download:"
    )

# Dialog / Form Tambah Mahasiswa Baru
if open_add_modal:
    st.session_state["show_add_form"] = True

if st.session_state.get("show_add_form", False):
    with st.form("form_tambah_mahasiswa"):
        st.markdown("<h4 style='font-family:Space Grotesk; color:#4cd7f6;'>Tambah Mahasiswa Asisten Baru</h4>", unsafe_allow_html=True)
        new_nama = st.text_input("Nama Lengkap Mahasiswa:", placeholder="Contoh: Audrey Sabrina")
        new_prodi = st.selectbox("Program Studi:", ["Pendidikan Fisika", "Pendidikan Matematika", "Fisika Murni", "Lainnya"])
        new_status = st.selectbox("Status Keaktifan:", ["Aktif", "Non-Aktif"])
        
        submitted = st.form_submit_button("Simpan ke Google Sheets", type="primary", use_container_width=True)
        if submitted:
            if new_nama.strip():
                sm.add_mahasiswa(new_nama, new_prodi, new_status)
                st.session_state["show_add_form"] = False
                st.cache_data.clear()
                st.success(f"Asisten '{new_nama}' berhasil ditambahkan ke Google Sheets!")
                st.rerun()
            else:
                st.error("Nama mahasiswa tidak boleh kosong!")
        
        if st.form_submit_button("Batal", use_container_width=True):
            st.session_state["show_add_form"] = False
            st.rerun()

st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

# =========================================================
# 4 QUICK STATS CARDS
# =========================================================
s1, s2, s3, s4 = st.columns(4)

tot_count = len(df_master)
fisika_count = len(df_master[df_master["Program_Studi"].str.contains("Fisika", case=False, na=False)])
matematika_count = len(df_master[df_master["Program_Studi"].str.contains("Matematika", case=False, na=False)])
aktif_count = len(df_master[df_master["Status_Aktif"] == "Aktif"])
pct_aktif = int((aktif_count / tot_count * 100)) if tot_count > 0 else 100

with s1:
    st.markdown(
        f"""
        <div class="glass-panel" style="padding: 14px;">
          <div style="font-family: 'JetBrains Mono'; font-size: 10px; color: #869397; text-transform: uppercase;">Total Asisten</div>
          <div style="font-family: 'Space Grotesk'; font-size: 26px; font-weight: 700; color: #dfe2f1; margin: 4px 0;">{tot_count}</div>
          <div style="font-size: 11px; color: #4edea3;">Lab Micro Teaching FisMat</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with s2:
    st.markdown(
        f"""
        <div class="glass-panel" style="padding: 14px;">
          <div style="font-family: 'JetBrains Mono'; font-size: 10px; color: #4cd7f6; text-transform: uppercase;">Prodi Fisika</div>
          <div style="font-family: 'Space Grotesk'; font-size: 26px; font-weight: 700; color: #4cd7f6; margin: 4px 0;">{fisika_count}</div>
          <div style="font-size: 11px; color: #bcc9cd;">Pendidikan Fisika</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with s3:
    st.markdown(
        f"""
        <div class="glass-panel" style="padding: 14px;">
          <div style="font-family: 'JetBrains Mono'; font-size: 10px; color: #c0c1ff; text-transform: uppercase;">Pendidikan Matematika</div>
          <div style="font-family: 'Space Grotesk'; font-size: 26px; font-weight: 700; color: #c0c1ff; margin: 4px 0;">{matematika_count}</div>
          <div style="font-size: 11px; color: #bcc9cd;">Praktik Micro Teaching</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with s4:
    st.markdown(
        f"""
        <div class="glass-panel" style="padding: 14px;">
          <div style="font-family: 'JetBrains Mono'; font-size: 10px; color: #4edea3; text-transform: uppercase;">Keaktifan Lab</div>
          <div style="font-family: 'Space Grotesk'; font-size: 26px; font-weight: 700; color: #4edea3; margin: 4px 0;">{pct_aktif}%</div>
          <div style="font-size: 11px; color: #4edea3;">{aktif_count} Personel Aktif</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

# =========================================================
# FILTER BAR & PENCARIAN
# =========================================================
fcol1, fcol2, fcol3 = st.columns([5, 3.5, 3.5])
with fcol1:
    search_nama = st.text_input("Cari Nama Mahasiswa:", placeholder="Cari nama lengkap asisten...", label_visibility="collapsed")
with fcol2:
    filter_prodi = st.selectbox("Filter Prodi:", ["Semua Prodi", "Pendidikan Fisika", "Pendidikan Matematika"], label_visibility="collapsed")
with fcol3:
    filter_keaktifan = st.selectbox("Filter Status:", ["Semua Status", "Aktif", "Non-Aktif"], label_visibility="collapsed")

# Filter logic
df_filtered = df_master.copy()
if search_nama:
    df_filtered = df_filtered[df_filtered["Nama_Mahasiswa"].str.contains(search_nama, case=False, na=False)]
if filter_prodi != "Semua Prodi":
    df_filtered = df_filtered[df_filtered["Program_Studi"] == filter_prodi]
if filter_keaktifan != "Semua Status":
    df_filtered = df_filtered[df_filtered["Status_Aktif"] == filter_keaktifan]

# =========================================================
# TABEL MASTER DATA MAHASISWA & AKSI EDIT / HAPUS
# =========================================================
st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

if df_filtered.empty:
    st.info("Tidak ada data mahasiswa yang cocok dengan kriteria pencarian.")
else:
    for idx, r in enumerate(df_filtered.itertuples(index=False), 1):
        nama = getattr(r, "Nama_Mahasiswa", "-")
        prodi = getattr(r, "Program_Studi", "-")
        status = getattr(r, "Status_Aktif", "Aktif")
        avatar = getattr(r, "Avatar_Initials", nama[:2].upper())
        status_badge = '<span class="badge-emerald">Aktif</span>' if status == "Aktif" else '<span class="badge-rose">Non-Aktif</span>'

        with st.container():
            c1, c2, c3, c4 = st.columns([5, 3, 2, 2])
            with c1:
                st.markdown(
                    f"""
                    <div style="display: flex; align-items: center; gap: 12px; padding: 6px 0;">
                      <div style="width: 38px; height: 38px; border-radius: 8px; background: rgba(76, 215, 246, 0.15); border: 1px solid rgba(76, 215, 246, 0.3); display: flex; align-items: center; justify-content: center; font-family: 'Space Grotesk'; font-size: 14px; font-weight: 700; color: #4cd7f6;">
                        {avatar}
                      </div>
                      <div>
                        <div style="font-weight: 600; color: #dfe2f1; font-size: 14px;">{nama}</div>
                        <div style="font-size: 11px; color: #869397;">Asisten Laboratorium</div>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with c2:
                st.markdown(f"<div style='padding-top: 14px; font-size: 13px; color: #bcc9cd;'>{prodi}</div>", unsafe_allow_html=True)
            with c3:
                st.markdown(f"<div style='padding-top: 14px;'>{status_badge}</div>", unsafe_allow_html=True)
            with c4:
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if st.button("Edit", key=f"btn_edit_{nama}", use_container_width=True):
                        st.session_state[f"editing_{nama}"] = True
                with btn_col2:
                    if st.button("Hapus", key=f"btn_del_{nama}", use_container_width=True):
                        sm.delete_mahasiswa(nama)
                        st.cache_data.clear()
                        st.success(f"Asisten '{nama}' berhasil dihapus!")
                        st.rerun()

            # Form Edit jika tombol Edit diklik
            if st.session_state.get(f"editing_{nama}", False):
                with st.form(f"form_edit_{nama}"):
                    st.markdown(f"<h5 style='color:#4cd7f6;'>Edit Data Asisten: {nama}</h5>", unsafe_allow_html=True)
                    edit_nama = st.text_input("Nama Mahasiswa:", value=nama)
                    edit_prodi = st.selectbox("Program Studi:", ["Pendidikan Fisika", "Pendidikan Matematika", "Fisika Murni", "Lainnya"], index=0 if "Fisika" in prodi else 1)
                    edit_stat = st.selectbox("Status Keaktifan:", ["Aktif", "Non-Aktif"], index=0 if status == "Aktif" else 1)
                    
                    if st.form_submit_button("Simpan Perubahan", type="primary"):
                        sm.update_mahasiswa(nama, edit_nama, edit_prodi, edit_stat)
                        st.session_state[f"editing_{nama}"] = False
                        st.cache_data.clear()
                        st.success("Data berhasil diperbarui!")
                        st.rerun()
                    if st.form_submit_button("Batal"):
                        st.session_state[f"editing_{nama}"] = False
                        st.rerun()

            st.markdown("<hr style='border: none; border-top: 1px solid rgba(255,255,255,0.05); margin: 6px 0 10px 0;'>", unsafe_allow_html=True)
