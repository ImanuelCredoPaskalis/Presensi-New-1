# Presensi Mahasiswa — Lab Micro Teaching FisMat

Aplikasi presensi mahasiswa berbasis **Streamlit** dengan desain dark dashboard *Nocturne Precision Lab*. Aplikasi mencatat presensi 8-aksi, memantau Dashboard Live, mengelola data mahasiswa, serta menghasilkan rekap laporan.

> **Database:** Google Sheets sebagai sumber data utama.  
> **Tanpa SQL:** Tidak menggunakan SQLite, MySQL, maupun PostgreSQL.

---

## Fitur

- Presensi 1-klik: Jam Masuk, Ke Kelas, Tugas Luar, Izin Keluar, Kembali Kelas, Kembali Tugas, Kembali Shift, dan Jam Keluar.
- Dashboard Live: KPI kehadiran, donut status, feed aktivitas, serta tabel audit.
- Data Mahasiswa minimalis: Nama, Program Studi, Status Aktif, dan Avatar Inisial.
- Rekap & Laporan: filter data, ekspor CSV/Excel, dan print browser ke PDF.
- Pengaturan: profil lab, parameter shift, koreksi catatan, PIN admin SHA-256, dan status koneksi Google Sheets.
- Fallback lokal: bila Google Sheets belum dikonfigurasi, aplikasi memakai `data/local_sheets_data.json` agar tetap bisa diuji.

---

## Struktur Proyek

```text
.
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml              # Jangan commit kredensial asli
├── assets/styles/theme.css
├── data/local_sheets_data.json   # Fallback pengembangan lokal
├── pages/
│   ├── 1_Presensi_Mahasiswa.py
│   ├── 2_Dashboard_Live.py
│   ├── 3_Data_Mahasiswa.py
│   ├── 4_Rekap_Laporan.py
│   └── 5_Pengaturan.py
├── utils/
│   ├── auth_helper.py
│   ├── export_manager.py
│   ├── gsheets_manager.py
│   ├── time_calculator.py
│   └── ui_components.py
├── app.py
├── requirements.txt
└── README.md
```

---

## Menjalankan Secara Lokal

### 1. Siapkan environment Python

Disarankan memakai Python **3.10+**.

```bash
python -m venv .venv
```

Aktifkan environment:

**Windows PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows CMD**

```bat
.venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Jalankan aplikasi

```bash
streamlit run app.py
```

Buka alamat berikut di browser:

```text
http://localhost:8501
```

---

# Konfigurasi Google Sheets

Untuk deployment produksi, Google Sheets digunakan sebagai basis data utama.

## 1. Siapkan Spreadsheet & Google Apps Script

1. Buka Google Drive.
2. Unggah file berikut:
   ```text
   migrasi_data_presensi_google_sheets.xlsx
   ```
3. Buka file tersebut sebagai Google Spreadsheet.
4. Buka menu **Extensions → Apps Script**.
5. Hapus semua kode default lalu tempelkan isi file `google_apps_script.js`.
6. Klik **Deploy → New Deployment**.
   - Jenis: **Web app**
   - Jalankan sebagai: **Me (your email)**
   - Akses: **Anyone**
7. Klik **Deploy** lalu salin **URL Aplikasi Web** yang muncul.

> Spreadsheet ini sudah memiliki empat tab utama: `Master_Mahasiswa`, `Presensi_Harian`, `Log_Aktivitas`, dan `Pengaturan` beserta seluruh data awal 5 mahasiswa dan riwayat presensi yang sudah disertakan.

---

# Deploy ke Streamlit Community Cloud

## 1. Upload proyek ke GitHub

1. Buat repository GitHub baru.
2. Upload seluruh file proyek, **kecuali** file rahasia.
3. Jangan commit file berikut:

```text
.streamlit/secrets.toml
```

Buat file `.gitignore` berikut di root proyek:

```gitignore
.venv/
__pycache__/
*.pyc
.streamlit/secrets.toml
data/local_sheets_data.json
```

> `data/local_sheets_data.json` opsional. Anda boleh commit sebagai data demo, tetapi jangan digunakan untuk data produksi yang sensitif.

## 2. Buat aplikasi di Streamlit Cloud

1. Buka [share.streamlit.io](https://share.streamlit.io/).
2. Login menggunakan akun GitHub.
3. Klik **Create app**.
4. Pilih repository, branch, dan file utama:

```text
Main file path: app.py
```

5. Klik **Deploy**.

## 3. Tambahkan Streamlit Secrets

Setelah aplikasi dibuat:

1. Buka aplikasi di Streamlit Cloud.
2. Klik **Manage app**.
3. Buka **Settings → Secrets**.
4. Tempel konfigurasi berikut. Ganti nilai URL dengan URL Web App yang sudah Anda salin dari Google Apps Script.

```toml
[google_apps_script]
gsheets_webhook_url = "https://script.google.com/macros/s/AKfycb.../exec"
```

5. Klik **Save** lalu lakukan **Reboot app**.

## 4. Alternatif Tanpa Deploy ke Cloud

Jika hanya menjalankan aplikasi secara lokal, Anda juga dapat memasukkan URL webhook di kolom **URL Web App Google Apps Script** pada menu **Pengaturan**. Opsi ini hanya berlaku untuk sesi yang sedang aktif.

---

## Validasi Deployment

Setelah reboot, buka halaman **Pengaturan** pada aplikasi.

Jika konfigurasi benar:

- Sidebar menampilkan **Google Apps Script Web App**.
- Header menampilkan **Tersinkron Google Sheets** atau **Mode Lokal** jika URL belum diisi.
- Halaman Pengaturan menunjukkan koneksi Cloud aktif.
- Presensi baru akan langsung ditulis ke tab `Presensi_Harian` dan `Log_Aktivitas`.

Jika belum dikonfigurasi atau gagal terhubung:

- Aplikasi tetap berjalan dalam **Mode Lokal**.
- Periksa kembali Secrets, Service Account, API Google, dan akses Editor ke spreadsheet.

---

## Catatan Keamanan

- Jangan memasukkan kredensial Service Account ke source code.
- Jangan commit `.streamlit/secrets.toml` ke GitHub.
- Pastikan Service Account hanya diberi akses ke spreadsheet yang diperlukan.
- Ganti PIN Admin default `admin123` pada halaman **Pengaturan** setelah deployment.
- Jangan menyimpan data pribadi mahasiswa yang tidak diperlukan.

---

## Troubleshooting

| Masalah | Solusi |
|---|---|
| Aplikasi menunjukkan `Mode Lokal` | Pastikan `gsheets_webhook_url` terisi dan app sudah di-reboot. Anda juga bisa mengisinya langsung dari menu **Pengaturan** untuk sesi lokal. |
| Webhook tidak merespons | Pastikan Deploy Web App di Apps Script sudah aktif dan dijalankan sebagai **Anyone**. |
| Data tidak masuk ke Spreadsheet | Periksa apakah tab `Master_Mahasiswa`, `Presensi_Harian`, `Log_Aktivitas`, dan `Pengaturan` sudah tersedia di spreadsheet hasil unggah. |
| `ModuleNotFoundError` | Pastikan dependency sudah tercantum di `requirements.txt`. |
| Perubahan kode belum muncul | Buka Manage App → Reboot app, atau push commit baru ke branch deployment. |

---

## Teknologi

- [Streamlit](https://streamlit.io/)
- [Google Sheets API](https://developers.google.com/sheets/api)
- [gspread](https://github.com/burnash/gspread)
- [Pandas](https://pandas.pydata.org/)
- [Plotly](https://plotly.com/python/)
- [OpenPyXL](https://openpyxl.readthedocs.io/)
