"""
Module: time_calculator.py
Kalkulasi waktu WIB, format tanggal bahasa Indonesia, durasi shift, dan keterlambatan.
"""

from datetime import datetime, timedelta

DAYS_ID = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
MONTHS_ID = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]


def get_current_date_id() -> str:
    """Mengembalikan tanggal hari ini dalam format bahasa Indonesia."""
    now = datetime.now()
    day_name = DAYS_ID[now.weekday()]
    month_name = MONTHS_ID[now.month - 1]
    return f"{day_name}, {now.day} {month_name} {now.year}"


def get_current_time_wib() -> str:
    """Mengembalikan waktu saat ini dalam format HH:MM:SS WIB."""
    return datetime.now().strftime("%H:%M:%S WIB")


def minutes_to_duration_str(minutes: int) -> str:
    """Konversi integer menit menjadi string 'Xj Ym'."""
    if minutes <= 0:
        return "0j 0m"
    hours = minutes // 60
    rem_m = minutes % 60
    if hours > 0:
        return f"{hours}j {rem_m}m"
    return f"{rem_m}m"


def calculate_diff_minutes(start_str: str, end_str: str) -> int:
    """Menghitung selisih menit antara 2 string jam HH:MM."""
    try:
        s = start_str.replace(" WIB", "").strip()
        e = end_str.replace(" WIB", "").strip()
        t1 = datetime.strptime(s, "%H:%M")
        t2 = datetime.strptime(e, "%H:%M")
        diff = (t2 - t1).total_seconds() / 60
        return max(0, int(diff))
    except Exception:
        return 0


def is_late(check_in_str: str, standard_str: str = "07:00", tolerance_m: int = 15) -> bool:
    """Cek apakah jam masuk melebihi jam standar + toleransi."""
    try:
        ci = check_in_str.replace(" WIB", "").strip()
        t_ci = datetime.strptime(ci, "%H:%M")
        t_std = datetime.strptime(standard_str.strip(), "%H:%M")
        limit = t_std + timedelta(minutes=tolerance_m)
        return t_ci > limit
    except Exception:
        return False
