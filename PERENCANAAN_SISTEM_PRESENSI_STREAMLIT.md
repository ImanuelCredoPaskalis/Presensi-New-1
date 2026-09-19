# DOKUMEN PERENCANAAN & ARSITEKTUR WEB APP PRESENSI MAHASISWA
## Berbasis Streamlit dengan Integrasi Penuh Google Sheets (Tanpa SQL)
### Desain Sistem: "Nocturne Precision Lab" — Laboratorium Micro Teaching Fisika & Matematika (FisMat)
**Penyederhanaan Ekstrem: Hanya Nama, Program Studi, dan Status Keaktifan**

---

## 1. PENDAHULUAN & PENDEKATAN TANPA SQL

### 1.1 Latar Belakang & Prinsip Data Ultra-Minimalis
Aplikasi ini dirancang sebagai pusat operasional dan pencatatan presensi asisten di Laboratorium Micro Teaching FisMat.
Sesuai arahan, sistem menerapkan **penyederhanaan data total**:
1. **Tanpa Database SQL:** Sepenuhnya menggunakan **Google Sheets** langsung sebagai *Single Source of Truth*.
2. **Entitas Data Mahasiswa Ultra-Minimalis:**
   - ❌ **Tidak ada NIM**
   - ❌ **Tidak ada Nomor WhatsApp**
   - ❌ **Tidak ada Angkatan / Semester**
   - ❌ **Tidak ada Tanggal Daftar**
   - ✅ **Hanya menyimpan:** **Nama Mahasiswa**, **Program Studi**, dan **Status Keaktifan** (dengan inisial avatar otomatis).
3. **Ergonomis, Cepat, dan Bersih:** Menghapus seluruh beban input data administratif yang tidak relevan dengan operasional harian lab, sehingga antarmuka menjadi sangat bersih, cepat, dan mudah dioperasikan.

---

## 2. STRUKTUR WORKBOOK GOOGLE SHEETS (MINIMALIS)

Workbook Google Sheets utama diberi nama:  
**`Presensi_Mahasiswa_Lab_FisMat`**

Workbook ini memiliki **4 lembar kerja (Tab)**:

```
Google Spreadsheet: Presensi_Mahasiswa_Lab_FisMat
├── [Tab 1] Master_Mahasiswa   -> Hanya: Nama_Mahasiswa, Program_Studi, Status_Aktif, Avatar_Initials
├── [Tab 2] Presensi_Harian    -> Catatan 8-aksi presensi per hari berbasis nama
├── [Tab 3] Log_Aktivitas      -> Audit feed kronologis (Live Feed)
└── [Tab 4] Pengaturan         -> Jam standar shift, toleransi, & PIN Admin
```

---

### 2.1 Tab 1: `Master_Mahasiswa` (Data Induk Asisten)
Struktur kolom dibuat sangat ramping dan esensial:

| Header Kolom | Tipe Data | Contoh Nilai | Keterangan |
|---|---|---|---|
| `Nama_Mahasiswa` | Text (Primary Key) | `Audrey Sabrina` | Nama unik mahasiswa asisten |
| `Program_Studi` | Text | `Pendidikan Fisika` | Program studi asisten |
| `Status_Aktif` | Text | `Aktif` | `Aktif` atau `Non-Aktif` |
| `Avatar_Initials`| Text | `AS` | Otomatis dibuat dari 2 huruf depan nama |

*Catatan: Form tambah asisten baru hanya memiliki 2 isian: **Nama Lengkap** dan pilihan **Program Studi**.*

---

### 2.2 Tab 2: `Presensi_Harian` (Catatan Presensi 8-Aksi)
Setiap asisten yang bertugas hari ini memiliki 1 baris catatan transaksi presensi:

| Header Kolom | Format | Contoh Data | Keterangan |
|---|---|---|---|
| `ID_Presensi` | Text | `PRS-20260919-Audrey` | Format: `PRS-YYYYMMDD-Nama` |
| `Tanggal` | Date | `2026-09-19` | Tanggal presensi (YYYY-MM-DD) |
| `Nama_Mahasiswa` | Text | `Audrey Sabrina` | Nama asisten |
| `Program_Studi` | Text | `Pendidikan Fisika` | Program studi |
| `Jam_Masuk` | Time | `07:55` | Waktu kedatangan di lab |
| `Sesi_Shift` | Text | `Pagi` | Shift Pagi / Shift Siang / Full |
| `Jam_Ke_Kelas` | Time | `-` | Waktu mulai izin kuliah |
| `Jam_Kembali_Kelas` | Time | `-` | Waktu selesai perkuliahan |
| `Nama_Mata_Kuliah` | Text | `-` | Rincian matkul & ruangan kelas |
| `Durasi_Kelas` | Text | `00:00` | Format durasi: `Xj Ym` atau `00:00` |
| `Jam_Tugas_Luar` | Time | `-` | Waktu mulai dinas luar lab |
| `Jam_Kembali_Tugas`| Time | `-` | Waktu kembali dinas luar |
| `Keterangan_Tugas`| Text | `-` | Deskripsi penugasan lab |
| `Jam_Izin_Keluar` | Time | `-` | Waktu izin sementara |
| `Jam_Kembali_Izin`| Time | `-` | Waktu kembali dari izin |
| `Durasi_Izin` | Text | `00:00` | Format durasi izin |
| `Jam_Keluar` | Time | `-` | Waktu selesai shift (pulang) |
| `Durasi_Shift` | Text | `5j 47m` | Total durasi kerja efektif di lab |
| `Status_Terkini` | Text | `Hadir di Lab` | `Hadir di Lab`, `Sedang di Kelas`, `Sedang Tugas`, `Pulang` |
| `Status_Ketepatan`| Text | `Tepat Waktu` | `Tepat Waktu` / `Terlambat` |

---

### 2.3 Tab 3: `Log_Aktivitas` (Untuk Live Feed Dashboard)
Mencatat riwayat peristiwa presensi secara kronologis:

| Header Kolom | Format | Contoh Data | Keterangan |
|---|---|---|---|
| `Timestamp` | DateTime | `2026-09-19 13:30:15` | Waktu kejadian aktivitas |
| `Nama_Mahasiswa` | Text | `Bintang Mahendra` | Nama asisten yang beraktivitas |
| `Aksi` | Text | `Tugas Keluar` | Jenis aksi (Masuk, Kelas, Tugas, Pulang, dll) |
| `Keterangan` | Text | `Ambil Modul Osiloskop di Lab Pusat` | Detail keterangan aktivitas |
| `Tipe_Ikon` | Text | `local_shipping` | Ikon Material Symbol |

---

### 2.4 Tab 4: `Pengaturan` (Konfigurasi Sistem)
Menyimpan parameter operasional lab dan keamanan:

| Parameter (`Kunci`) | Nilai (`Value`) | Keterangan |
|---|---|---|
| `lab_name` | `Lab Micro Teaching FisMat` | Nama instansi laboratorium |
| `lab_location` | `Kampus 3` | Gedung / ruangan lab |
| `jam_datang_standar` | `07:00` | Batas awal jam masuk shift |
| `jam_selesai_standar`| `18:00` | Batas penutupan shift |
| `toleransi_menit` | `15` | Toleransi keterlambatan (menit) |
| `admin_pin_hash` | `8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918` | Hash SHA-256 kata sandi admin (`admin123`) |

---

## 3. PENYESUAIAN ANTARMUKA 5 HALAMAN APLIKASI

Seluruh modul antarmuka kini berfokus secara murni pada nama asisten dan kegiatannya:

### 3.1 Halaman 1: Presensi Mahasiswa (`pages/1_presensi.py`)
1. **Live Telemetry Banner:** Tanggal Indonesia, status sinkronisasi Google Sheets (*Live Sync*), jam digital besar `HH:MM:SS WIB`.
2. **Langkah 1 (Pilih Mahasiswa):**
   * Input pencarian nama mahasiswa.
   * Dropdown nama asisten: `Audrey Sabrina • Pend. Fisika`, `Jasmin Putri • Pend. Matematika`, dsb.
   * **Kartu Profil Mahasiswa:**
     * Avatar inisial (misal: `AS` dalam lingkaran beraksen).
     * Nama mahasiswa dengan tipografi `Space Grotesk`.
     * Badge status keaktifan & status presensi hari ini (*Hadir di Lab* / *Sedang di Kelas* / *Belum Presensi*).
     * Jam Masuk dan Durasi Aktif hari ini.
3. **Langkah 2 (Matriks 8 Aksi Presensi):**
   * Grid 8 tombol interaktif:
     `Jam Masuk`, `Jam ke Kelas`, `Tugas Keluar`, `Izin Keluar`, `Jam Keluar`, `Kembali Kelas`, `Kembali Tugas`, `Kembali Shift`.
   * Feedback toast box interaktif dengan nama target mahasiswa.
4. **Tabel Riwayat Presensi Hari Ini:**
   * Kolom tabel: No, Nama Mahasiswa, Program Studi, Jam Masuk, Sesi Kelas, Durasi Kelas, Tugas Luar, Kembali Tugas, Izin Keluar, Durasi Izin, Jam Keluar, Durasi Shift, Status Terkini.

### 3.2 Halaman 2: Dashboard Live (`pages/2_dashboard.py`)
1. **Quick Control Bar:** Refresh button (interval 15 detik), filter status kehadiran.
2. **6 Bento Metric Cards:** Total Asisten, Hadir di Lab, Sedang di Kelas, Sedang Tugas, Izin/Sakit, Belum Hadir.
3. **Visual Analytics:**
   * Plotly Donut Chart (Persentase distribusi asisten saat ini).
   * Plotly Bar Chart Jam Sibuk Lab (Beban asisten per rentang waktu vs kuota lab).
4. **Live Activity Feed:** Log kronologis aktivitas asisten terbaru.
5. **Tabel Status Kehadiran Hari Ini:** Audit lengkap pergerakan asisten.

### 3.3 Halaman 3: Data Mahasiswa (`pages/3_data_mahasiswa.py`)
1. **Top Action Bar:** Tombol Tambah Asisten, Ekspor Excel, Hapus Terpilih.
2. **Form Tambah / Edit Asisten (Super Praktis):**
   * *Field 1:* Nama Lengkap Mahasiswa (Text Input)
   * *Field 2:* Program Studi (Pilihan: *Pendidikan Fisika* / *Pendidikan Matematika*)
   * *Field 3:* Status Keaktifan (Toggle/Pilihan: *Aktif* / *Non-Aktif*)
3. **4 Kartu Metrik Ringkas:** Total Asisten, Asisten Fisika, Asisten Matematika, Rata-rata Kehadiran.
4. **Tabel Master Asisten:**
   * Checkbox multi-select, No, Inisial Avatar, Nama Mahasiswa, Program Studi, Status Keaktifan (Pill Badge), Aksi (Edit / Hapus).

### 3.4 Halaman 4: Rekap & Laporan (`pages/4_rekap_laporan.py`)
1. **Suite Ekspor:** Ekspor Excel (.xlsx berformat rapi via `openpyxl`), Ekspor CSV, dan Cetak PDF (Print Preview formal).
2. **Filter Deck:** Rentang tanggal kalender, filter nama mahasiswa, dan filter status sesi.
3. **Tabel Rekapitulasi Presensi:** Menampilkan seluruh riwayat presensi dengan expander baris rincian kelas/tugas.

### 3.5 Halaman 5: Pengaturan Sistem (`pages/5_pengaturan.py`)
1. **Editor & Koreksi Catatan Admin:** Form koreksi jam presensi jika asisten salah memilih tombol.
2. **Profil Laboratorium & Shift:** Nama lab, lokasi, jam shift standar, toleransi keterlambatan.
3. **Keamanan:** Ganti PIN Admin (SHA-256).
4. **Google Sheets Tools:** Uji koneksi API, tombol buka spreadsheet langsung di browser, dan tombol backup data.

---

## 4. INTEGRASI GOOGLE SHEETS & STRUKTUR FILE STREAMLIT

### 4.1 Mekanisme Akses Google Sheets via `gspread`
Kredensial Service Account disimpan di `.streamlit/secrets.toml`:
```toml
[gcp_service_account]
type = "service_account"
project_id = "lab-fismat-presensi"
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "presensi-bot@lab-fismat-presensi.iam.gserviceaccount.com"

[spreadsheet_config]
spreadsheet_name = "Presensi_Mahasiswa_Lab_FisMat"
```

### 4.2 Struktur Direktori Proyek
```
lab_presensi_fismat/
├── .streamlit/
│   ├── config.toml               # Tema gelap Nocturne (#0f131d), port 8501
│   └── secrets.toml              # Kredensial Google Service Account
├── assets/
│   ├── logo_lab.png              # Logo FisMat
│   └── styles/
│       └── theme.css             # CSS Nocturne Lab, Google Fonts Space Grotesk & Manrope
├── pages/
│   ├── 1_Presensi_Mahasiswa.py   # Modul Presensi & Matriks 8 Aksi
│   ├── 2_Dashboard_Live.py       # Telemetri, Bento Cards, Plotly Donut & Bar Chart
│   ├── 3_Data_Mahasiswa.py       # Master Data Mahasiswa (Nama & Prodi saja)
│   ├── 4_Rekap_Laporan.py        # Filter tanggal, Ekspor Excel/CSV, Print PDF
│   └── 5_Pengaturan.py           # Editor data, Profil lab, Jam shift, PIN SHA-256
├── utils/
│   ├── gsheets_manager.py        # Engine CRUD gspread untuk 4 tab Google Sheets
│   ├── auth_helper.py            # Hashing SHA-256 & verifikasi PIN Admin
│   ├── time_calculator.py        # Logika durasi jam-menit & toleransi keterlambatan
│   ├── export_manager.py         # Generator Excel (.xlsx) & CSV
│   └── ui_components.py          # Render Header Global, Bento Cards & Table HTML
├── app.py                        # Router navigasi utama
├── requirements.txt              # Pustaka Python
└── README.md                     # Panduan setup akun Service Account
```

---

## 5. DEPENDENCIES PYTHON (`requirements.txt`)

```text
streamlit>=1.36.0
pandas>=2.1.0
gspread>=6.0.0
google-auth>=2.28.0
plotly>=5.20.0
openpyxl>=3.1.2
xlsxwriter>=3.2.0
streamlit-autorefresh>=1.0.1
```
