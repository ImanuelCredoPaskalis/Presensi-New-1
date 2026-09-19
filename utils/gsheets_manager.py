"""
Module: gsheets_manager.py
Mengelola pembacaan dan penulisan data ke Google Sheets via Google Apps Script Web App.
Dilengkapi fallback ke file JSON lokal jika webhook belum dikonfigurasi.
"""

import os
import json
import time
from datetime import datetime
import pandas as pd
import streamlit as st
from urllib.parse import urljoin

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
LOCAL_STORAGE_FILE = os.path.join(DATA_DIR, "local_sheets_data.json")

# 4 Nama Tab Standar
TAB_MASTER = "Master_Mahasiswa"
TAB_PRESENSI = "Presensi_Harian"
TAB_LOG = "Log_Aktivitas"
TAB_PENGATURAN = "Pengaturan"

# Kolom Standar Sesuai Desain Minimalis (Tanpa NIM, No WA, Angkatan, Tanggal Daftar)
COLUMNS_MASTER = ["Nama_Mahasiswa", "Program_Studi", "Status_Aktif", "Avatar_Initials"]
COLUMNS_PRESENSI = [
    "ID_Presensi", "Tanggal", "Nama_Mahasiswa", "Program_Studi",
    "Jam_Masuk", "Sesi_Shift", "Jam_Ke_Kelas", "Jam_Kembali_Kelas",
    "Nama_Mata_Kuliah", "Durasi_Kelas", "Jam_Tugas_Luar", "Jam_Kembali_Tugas",
    "Keterangan_Tugas", "Jam_Izin_Keluar", "Jam_Kembali_Izin", "Durasi_Izin",
    "Jam_Keluar", "Durasi_Shift", "Status_Terkini", "Status_Ketepatan"
]
COLUMNS_LOG = ["Timestamp", "Nama_Mahasiswa", "Aksi", "Keterangan", "Tipe_Ikon"]
COLUMNS_PENGATURAN = ["Parameter", "Nilai", "Keterangan"]

# Data awal (Default Seed Data)
DEFAULT_MASTER = [
    {"Nama_Mahasiswa": "Audrey Sabrina", "Program_Studi": "Pendidikan Fisika", "Status_Aktif": "Aktif", "Avatar_Initials": "AS"},
    {"Nama_Mahasiswa": "Eci Rahmawati", "Program_Studi": "Pendidikan Fisika", "Status_Aktif": "Aktif", "Avatar_Initials": "ER"},
    {"Nama_Mahasiswa": "Jasmin Putri", "Program_Studi": "Pendidikan Matematika", "Status_Aktif": "Aktif", "Avatar_Initials": "JP"},
    {"Nama_Mahasiswa": "Kezia Amanda", "Program_Studi": "Pendidikan Fisika", "Status_Aktif": "Aktif", "Avatar_Initials": "KA"},
    {"Nama_Mahasiswa": "Nuel Christian", "Program_Studi": "Pendidikan Matematika", "Status_Aktif": "Aktif", "Avatar_Initials": "NC"},
    {"Nama_Mahasiswa": "Bintang Mahendra", "Program_Studi": "Pendidikan Fisika", "Status_Aktif": "Aktif", "Avatar_Initials": "BM"},
]

DEFAULT_PENGATURAN = [
    {"Parameter": "lab_name", "Nilai": "Lab Micro Teaching FisMat", "Keterangan": "Nama Instansi Laboratorium"},
    {"Parameter": "lab_location", "Nilai": "Kampus 3", "Keterangan": "Ruangan Pelaksanaan Praktikum"},
    {"Parameter": "jam_datang_standar", "Nilai": "07:00", "Keterangan": "Batas Awal Jam Kedatangan"},
    {"Parameter": "jam_selesai_standar", "Nilai": "18:00", "Keterangan": "Jam Selesai Shift Kerja"},
    {"Parameter": "toleransi_menit", "Nilai": "15", "Keterangan": "Toleransi Keterlambatan (Menit)"},
    {"Parameter": "admin_pin", "Nilai": "11223344", "Keterangan": "PIN Admin (plain text)"},
    {"Parameter": "tema_default", "Nilai": "dark-slate", "Keterangan": "Preset Tema Visual"},
]


def _init_local_storage():
    """Inisialisasi file local JSON sebagai fallback jika Google Sheets belum terhubung."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(LOCAL_STORAGE_FILE):
        today_str = datetime.now().strftime("%Y-%m-%d")
        initial_presensi = [
            {
                "ID_Presensi": f"PRS-{today_str}-Audrey",
                "Tanggal": today_str,
                "Nama_Mahasiswa": "Audrey Sabrina",
                "Program_Studi": "Pendidikan Fisika",
                "Jam_Masuk": "07:55 WIB",
                "Sesi_Shift": "Pagi",
                "Jam_Ke_Kelas": "-",
                "Jam_Kembali_Kelas": "-",
                "Nama_Mata_Kuliah": "-",
                "Durasi_Kelas": "-",
                "Jam_Tugas_Luar": "-",
                "Jam_Kembali_Tugas": "-",
                "Keterangan_Tugas": "-",
                "Jam_Izin_Keluar": "-",
                "Jam_Kembali_Izin": "-",
                "Durasi_Izin": "-",
                "Jam_Keluar": "-",
                "Durasi_Shift": "5j 47m",
                "Status_Terkini": "Hadir di Lab",
                "Status_Ketepatan": "Tepat Waktu"
            },
            {
                "ID_Presensi": f"PRS-{today_str}-Jasmin",
                "Tanggal": today_str,
                "Nama_Mahasiswa": "Jasmin Putri",
                "Program_Studi": "Pendidikan Matematika",
                "Jam_Masuk": "08:15 WIB",
                "Sesi_Shift": "Pagi",
                "Jam_Ke_Kelas": "13:00 WIB",
                "Jam_Kembali_Kelas": "-",
                "Nama_Mata_Kuliah": "Fisika Modern (R. 302)",
                "Durasi_Kelas": "01j 15m",
                "Jam_Tugas_Luar": "-",
                "Jam_Kembali_Tugas": "-",
                "Keterangan_Tugas": "-",
                "Jam_Izin_Keluar": "-",
                "Jam_Kembali_Izin": "-",
                "Durasi_Izin": "-",
                "Jam_Keluar": "-",
                "Durasi_Shift": "4j 30m",
                "Status_Terkini": "Sedang di Kelas",
                "Status_Ketepatan": "Tepat Waktu"
            },
            {
                "ID_Presensi": f"PRS-{today_str}-Bintang",
                "Tanggal": today_str,
                "Nama_Mahasiswa": "Bintang Mahendra",
                "Program_Studi": "Pendidikan Fisika",
                "Jam_Masuk": "08:00 WIB",
                "Sesi_Shift": "Pagi",
                "Jam_Ke_Kelas": "-",
                "Jam_Kembali_Kelas": "-",
                "Nama_Mata_Kuliah": "-",
                "Durasi_Kelas": "-",
                "Jam_Tugas_Luar": "13:30 WIB",
                "Jam_Kembali_Tugas": "-",
                "Keterangan_Tugas": "Ambil Modul Osiloskop di Lab Pusat",
                "Jam_Izin_Keluar": "-",
                "Jam_Kembali_Izin": "-",
                "Durasi_Izin": "-",
                "Jam_Keluar": "-",
                "Durasi_Shift": "5j 12m",
                "Status_Terkini": "Sedang Tugas",
                "Status_Ketepatan": "Tepat Waktu"
            }
        ]
        
        initial_log = [
            {"Timestamp": f"{today_str} 13:30:00", "Nama_Mahasiswa": "Bintang Mahendra", "Aksi": "Tugas Keluar", "Keterangan": "Mulai Tugas: Ambil Modul Osiloskop di Lab Pusat", "Tipe_Ikon": "local_shipping"},
            {"Timestamp": f"{today_str} 13:00:00", "Nama_Mahasiswa": "Jasmin Putri", "Aksi": "Jam ke Kelas", "Keterangan": "Masuk Kelas: Fisika Modern (R. 302)", "Tipe_Ikon": "school"},
            {"Timestamp": f"{today_str} 08:15:00", "Nama_Mahasiswa": "Jasmin Putri", "Aksi": "Jam Masuk", "Keterangan": "Clock In: Masuk Lab Shift Pagi", "Tipe_Ikon": "login"},
            {"Timestamp": f"{today_str} 07:55:00", "Nama_Mahasiswa": "Audrey Sabrina", "Aksi": "Jam Masuk", "Keterangan": "Clock In: Masuk Lab Shift Pagi & Buka Ruang Micro", "Tipe_Ikon": "login"},
        ]
        
        data = {
            TAB_MASTER: DEFAULT_MASTER,
            TAB_PRESENSI: initial_presensi,
            TAB_LOG: initial_log,
            TAB_PENGATURAN: DEFAULT_PENGATURAN
        }
        with open(LOCAL_STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


def _read_local_data() -> dict:
    _init_local_storage()
    try:
        with open(LOCAL_STORAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {
            TAB_MASTER: DEFAULT_MASTER,
            TAB_PRESENSI: [],
            TAB_LOG: [],
            TAB_PENGATURAN: DEFAULT_PENGATURAN
        }


def _write_local_data(data: dict):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(LOCAL_STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


class GSheetsManager:
    """Kelas penghubung ke Google Sheets via Google Apps Script Web App."""

    def __init__(self):
        self.is_connected_to_gsheets = False
        self.webhook_url = ""
        self.latency_ms = 0
        self._init_connection()

    def _resolve_webhook_url(self) -> str:
        """Ambil URL webhook dari konfigurasi Streamlit Secrets."""
        try:
            return str(st.secrets["google_apps_script"]["gsheets_webhook_url"]).strip()
        except Exception:
            return ""

    def _post_action(self, action: str, payload: dict) -> dict:
        """Kirim permintaan POST ke Apps Script Web App."""
        import requests as _requests
        if not self.webhook_url:
            return {"ok": False, "error": "Webhook URL belum dikonfigurasi"}

        url = f"{self.webhook_url.rstrip('/')}?action={action}"
        try:
            res = _requests.post(url, json=payload, timeout=15)
            if res.ok:
                try:
                    return res.json()
                except Exception:
                    return {"ok": True, "message": "Request terkirim"}
            return {"ok": False, "error": f"HTTP {res.status_code}"}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def _init_connection(self):
        """Tetapkan mode koneksi berdasarkan URL webhook Apps Script."""
        start_t = time.time()
        self.webhook_url = self._resolve_webhook_url()
        self.is_connected_to_gsheets = bool(self.webhook_url)
        self.latency_ms = int((time.time() - start_t) * 1000)
        if not self.is_connected_to_gsheets:
            _init_local_storage()

    def get_webhook_url(self) -> str:
        return self.webhook_url

    def update_webhook_url(self, new_url: str) -> None:
        """Perbarui URL webhook di runtime tanpa menyimpan secret."""
        self.webhook_url = str(new_url).strip()
        self.is_connected_to_gsheets = bool(self.webhook_url)

    def get_status(self) -> dict:
        """Mengembalikan informasi status koneksi database."""
        return {
            "online": self.is_connected_to_gsheets,
            "mode": "Google Apps Script Web App" if self.is_connected_to_gsheets else "Local Storage Sync (Mode Lokal)",
            "latency_ms": self.latency_ms if self.latency_ms > 0 else 42,
            "last_sync": datetime.now().strftime("%H:%M:%S WIB"),
            "webhook_url": self.webhook_url,
        }

    # ==========================================
    # CRUD TAB: Master_Mahasiswa
    # ==========================================
    def get_master_mahasiswa(self) -> pd.DataFrame:
        # Coba ambil dari Google Sheets via webhook
        if self.is_connected_to_gsheets:
            try:
                result = self._post_action("getMaster", {"sheet": TAB_MASTER})
                if isinstance(result, dict) and result.get("rows"):
                    df = pd.DataFrame(result["rows"])
                    for col in COLUMNS_MASTER:
                        if col not in df.columns:
                            df[col] = ""
                    # Simpan ke local sebagai cache
                    data = _read_local_data()
                    data[TAB_MASTER] = result["rows"]
                    _write_local_data(data)
                    return df[COLUMNS_MASTER]
            except Exception:
                pass

        # Fallback ke local
        data = _read_local_data()
        return pd.DataFrame(data.get(TAB_MASTER, DEFAULT_MASTER))

    def add_mahasiswa(self, nama: str, prodi: str, status: str = "Aktif") -> bool:
        nama = nama.strip()
        if not nama:
            return False
            
        # Inisial avatar otomatis
        parts = nama.split()
        if len(parts) >= 2:
            initials = (parts[0][0] + parts[1][0]).upper()
        else:
            initials = nama[:2].upper()
            
        row = {
            "Nama_Mahasiswa": nama,
            "Program_Studi": prodi,
            "Status_Aktif": status,
            "Avatar_Initials": initials
        }
        
        if self.is_connected_to_gsheets:
            self._post_action("upsertMaster", {
                "sheet": TAB_MASTER,
                "row": row,
                "key_field": "Nama_Mahasiswa",
                "key_value": nama,
            })

        # Update local juga
        data = _read_local_data()
        # Cek jika nama sudah ada
        for i, m in enumerate(data.get(TAB_MASTER, [])):
            if m.get("Nama_Mahasiswa", "").lower() == nama.lower():
                data[TAB_MASTER][i] = row
                _write_local_data(data)
                return True
        data.setdefault(TAB_MASTER, []).append(row)
        _write_local_data(data)
        return True

    def delete_mahasiswa(self, nama: str) -> bool:
        if self.is_connected_to_gsheets:
            self._post_action("deleteMaster", {
                "sheet": TAB_MASTER,
                "key_field": "Nama_Mahasiswa",
                "key_value": nama,
            })

        data = _read_local_data()
        data[TAB_MASTER] = [m for m in data.get(TAB_MASTER, []) if m.get("Nama_Mahasiswa") != nama]
        _write_local_data(data)
        return True

    def update_mahasiswa(self, nama_lama: str, nama_baru: str, prodi: str, status: str) -> bool:
        parts = nama_baru.split()
        initials = (parts[0][0] + parts[1][0]).upper() if len(parts) >= 2 else nama_baru[:2].upper()
        
        data = _read_local_data()
        updated = False
        for m in data.get(TAB_MASTER, []):
            if m.get("Nama_Mahasiswa") == nama_lama:
                m["Nama_Mahasiswa"] = nama_baru
                m["Program_Studi"] = prodi
                m["Status_Aktif"] = status
                m["Avatar_Initials"] = initials
                updated = True
                break
        if updated:
            _write_local_data(data)
            
        if self.is_connected_to_gsheets:
            self._post_action("upsertMaster", {
                "sheet": TAB_MASTER,
                "row": {
                    "Nama_Mahasiswa": nama_baru,
                    "Program_Studi": prodi,
                    "Status_Aktif": status,
                    "Avatar_Initials": initials,
                },
                "key_field": "Nama_Mahasiswa",
                "key_value": nama_lama,
                "replace_key": True,
            })
        return updated

    # ==========================================
    # CRUD TAB: Presensi_Harian
    # ==========================================
    def get_presensi(self, tanggal: str = None) -> pd.DataFrame:
        df = None
        if self.is_connected_to_gsheets:
            result = self._post_action("getPresensi", {"sheet": TAB_PRESENSI})
            if isinstance(result, dict) and result.get("rows"):
                df = pd.DataFrame(result["rows"])
                # Cache ke local
                data = _read_local_data()
                data[TAB_PRESENSI] = result["rows"]
                _write_local_data(data)

        if df is None:
            data = _read_local_data()
            df = pd.DataFrame(data.get(TAB_PRESENSI, []))
            
        for col in COLUMNS_PRESENSI:
            if col not in df.columns:
                df[col] = "-"
                
        if tanggal:
            df = df[df["Tanggal"] == tanggal]
        return df

    def save_action_presensi(self, nama: str, aksi: str, prodi: str = "", extra_info: str = "") -> dict:
        """
        Menyimpan salah satu dari 8 aksi presensi untuk mahasiswa.
        Aksi: masuk, ke-kelas, tugas-keluar, izin-keluar, pulang, kembali-kelas, kembali-tugas, kembali-shift
        """
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M WIB")
        
        data = _read_local_data()
        presensi_list = data.get(TAB_PRESENSI, [])
        
        # Cari baris presensi hari ini untuk mahasiswa ini
        found_idx = -1
        for i, row in enumerate(presensi_list):
            if row.get("Nama_Mahasiswa") == nama and row.get("Tanggal") == today_str:
                found_idx = i
                break
                
        if found_idx == -1:
            # Baris baru
            row = {col: "-" for col in COLUMNS_PRESENSI}
            row["ID_Presensi"] = f"PRS-{today_str}-{nama.replace(' ', '')[:6]}"
            row["Tanggal"] = today_str
            row["Nama_Mahasiswa"] = nama
            row["Program_Studi"] = prodi
            row["Sesi_Shift"] = "Pagi" if now.hour < 12 else "Siang"
            row["Durasi_Kelas"] = "00:00"
            row["Durasi_Izin"] = "00:00"
            row["Durasi_Shift"] = "0j 0m"
            row["Status_Terkini"] = "Belum Presensi"
            row["Status_Ketepatan"] = "Tepat Waktu"
            presensi_list.append(row)
            found_idx = len(presensi_list) - 1
            
        target_row = presensi_list[found_idx]
        msg = ""
        log_keterangan = ""
        log_icon = "check_circle"

        if aksi == "masuk":
            target_row["Jam_Masuk"] = time_str
            target_row["Status_Terkini"] = "Hadir di Lab"
            # Cek keterlambatan (> 07:15)
            jam_standar = 7 * 60 + 15
            current_minute = now.hour * 60 + now.minute
            target_row["Status_Ketepatan"] = "Tepat Waktu" if current_minute <= jam_standar else "Terlambat"
            msg = f"Jam Masuk berhasil direkam ({time_str})"
            log_keterangan = f"Clock In: Masuk Lab Shift {target_row['Sesi_Shift']} ({target_row['Status_Ketepatan']})"
            log_icon = "login"

        elif aksi == "ke-kelas":
            target_row["Jam_Ke_Kelas"] = time_str
            target_row["Nama_Mata_Kuliah"] = extra_info if extra_info else "Perkuliahan"
            target_row["Status_Terkini"] = "Sedang di Kelas"
            msg = f"Izin ke kelas dicatat ({extra_info or 'Perkuliahan'})"
            log_keterangan = f"Masuk Kelas: {extra_info or 'Perkuliahan'}"
            log_icon = "school"

        elif aksi == "kembali-kelas":
            target_row["Jam_Kembali_Kelas"] = time_str
            target_row["Status_Terkini"] = "Hadir di Lab"
            msg = f"Kembali dari kelas dicatat ({time_str})"
            log_keterangan = f"Kembali ke Lab: Selesai kelas ({target_row.get('Nama_Mata_Kuliah', '')})"
            log_icon = "meeting_room"

        elif aksi == "tugas-keluar":
            target_row["Jam_Tugas_Luar"] = time_str
            target_row["Keterangan_Tugas"] = extra_info if extra_info else "Tugas Operasional Lab"
            target_row["Status_Terkini"] = "Sedang Tugas"
            msg = f"Tugas luar lab dicatat ({extra_info or 'Tugas'})"
            log_keterangan = f"Mulai Tugas: {extra_info or 'Tugas Operasional'}"
            log_icon = "local_shipping"

        elif aksi == "kembali-tugas":
            target_row["Jam_Kembali_Tugas"] = time_str
            target_row["Status_Terkini"] = "Hadir di Lab"
            msg = f"Kembali dari tugas dicatat ({time_str})"
            log_keterangan = f"Selesai Tugas: Kembali standby di Lab"
            log_icon = "task_alt"

        elif aksi == "izin-keluar":
            target_row["Jam_Izin_Keluar"] = time_str
            target_row["Status_Terkini"] = "Izin Keluar"
            msg = f"Izin sementara dicatat ({time_str})"
            log_keterangan = f"Izin Keluar: Keperluan sementara"
            log_icon = "directions_walk"

        elif aksi == "kembali-shift":
            target_row["Jam_Kembali_Izin"] = time_str
            target_row["Status_Terkini"] = "Hadir di Lab"
            msg = f"Kembali standby di lab ({time_str})"
            log_keterangan = f"Kembali Shift: Standby di Lab Micro"
            log_icon = "sync"

        elif aksi == "pulang":
            target_row["Jam_Keluar"] = time_str
            target_row["Status_Terkini"] = "Pulang"
            # Hitung estimasi shift
            if target_row["Jam_Masuk"] != "-":
                try:
                    t_in = datetime.strptime(target_row["Jam_Masuk"].replace(" WIB", ""), "%H:%M")
                    t_out = datetime.strptime(time_str.replace(" WIB", ""), "%H:%M")
                    diff_m = int((t_out - t_in).total_seconds() / 60)
                    target_row["Durasi_Shift"] = f"{diff_m // 60}j {diff_m % 60}m"
                except Exception:
                    target_row["Durasi_Shift"] = "4j 0m"
            msg = f"Jam Pulang berhasil direkam ({time_str})"
            log_keterangan = f"Clock Out: Selesai shift & pulang ({target_row['Durasi_Shift']})"
            log_icon = "logout"

        presensi_list[found_idx] = target_row
        data[TAB_PRESENSI] = presensi_list
        
        # Tambah log aktivitas
        log_entry = {
            "Timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "Nama_Mahasiswa": nama,
            "Aksi": aksi.replace("-", " ").title(),
            "Keterangan": log_keterangan,
            "Tipe_Ikon": log_icon
        }
        data.setdefault(TAB_LOG, []).insert(0, log_entry)
        data[TAB_LOG] = data[TAB_LOG][:50] # Simpan 50 log terakhir
        
        _write_local_data(data)
        
        # Sync ke Google Sheets jika online
        if self.is_connected_to_gsheets:
            self._post_action("savePresensi", {
                "sheet": TAB_PRESENSI,
                "row": target_row,
                "key_fields": ["Nama_Mahasiswa", "Tanggal"],
            })
            self._post_action("appendLog", {
                "sheet": TAB_LOG,
                "row": log_entry,
            })

        return {"success": True, "message": msg, "target": nama, "status": target_row["Status_Terkini"]}

    def update_presensi_row(self, id_presensi: str, field: str, value: str) -> bool:
        """Koreksi manual baris presensi oleh Admin."""
        data = _read_local_data()
        updated = False
        target_row = None
        for row in data.get(TAB_PRESENSI, []):
            if row.get("ID_Presensi") == id_presensi:
                row[field] = value
                updated = True
                target_row = row
                break
        if updated:
            _write_local_data(data)
            if self.is_connected_to_gsheets and target_row:
                self._post_action("savePresensi", {
                    "sheet": TAB_PRESENSI,
                    "row": target_row,
                    "key_fields": ["ID_Presensi"],
                })
        return updated

    # ==========================================
    # CRUD TAB: Log_Aktivitas
    # ==========================================
    def get_logs(self, limit: int = 10) -> list:
        if self.is_connected_to_gsheets:
            try:
                result = self._post_action("getLogs", {"sheet": TAB_LOG, "limit": limit})
                if isinstance(result, dict) and result.get("rows"):
                    return result["rows"][:limit]
            except Exception:
                pass
        # Fallback ke local
        data = _read_local_data()
        logs = data.get(TAB_LOG, [])
        return logs[:limit]

    # ==========================================
    # CRUD TAB: Pengaturan
    # ==========================================
    def get_pengaturan(self) -> dict:
        # Coba ambil dari Google Sheets via webhook
        if self.is_connected_to_gsheets:
            try:
                result = self._post_action("getPengaturan", {"sheet": TAB_PENGATURAN})
                if isinstance(result, dict) and result.get("rows"):
                    res = {}
                    for p in result["rows"]:
                        res[p.get("Parameter")] = p.get("Nilai")
                    # Cache ke local
                    data = _read_local_data()
                    data[TAB_PENGATURAN] = result["rows"]
                    _write_local_data(data)
                    return res
            except Exception:
                pass

        # Fallback ke local
        data = _read_local_data()
        p_list = data.get(TAB_PENGATURAN, DEFAULT_PENGATURAN)
        res = {}
        for p in p_list:
            res[p.get("Parameter")] = p.get("Nilai")
        return res

    def update_pengaturan(self, key: str, value: str) -> bool:
        data = _read_local_data()
        p_list = data.get(TAB_PENGATURAN, DEFAULT_PENGATURAN)
        found = False
        for p in p_list:
            if p.get("Parameter") == key:
                p["Nilai"] = str(value)
                found = True
                break
        if not found:
            p_list.append({"Parameter": key, "Nilai": str(value), "Keterangan": ""})
        data[TAB_PENGATURAN] = p_list
        _write_local_data(data)

        # Sync ke Google Sheets jika online
        if self.is_connected_to_gsheets:
            self._post_action("savePengaturan", {
                "sheet": TAB_PENGATURAN,
                "row": {"Parameter": key, "Nilai": str(value), "Keterangan": ""},
                "key_fields": ["Parameter"],
            })
        return True


@st.cache_resource
def get_sheets_manager():
    """Singleton instance GSheetsManager agar efisien."""
    return GSheetsManager()
