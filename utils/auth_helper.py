"""
Module: auth_helper.py
Pengelolaan keamanan dan autentikasi Admin berbasis hash SHA-256.
"""

import hashlib
import streamlit as st
from utils.gsheets_manager import get_sheets_manager


def hash_pin(pin: str) -> str:
    """Mengembalikan hash SHA-256 dari string PIN."""
    return hashlib.sha256(pin.strip().encode("utf-8")).hexdigest()


def is_admin() -> bool:
    """Mengecek apakah sesi admin saat ini sedang aktif."""
    return st.session_state.get("is_admin_authenticated", False)


def verify_admin_pin(input_pin: str) -> bool:
    """Memverifikasi PIN input terhadap PIN di pengaturan (plain text)."""
    sm = get_sheets_manager()
    settings = sm.get_pengaturan()
    stored_pin = settings.get("admin_pin", "11223344")

    if input_pin.strip() == str(stored_pin):
        st.session_state["is_admin_authenticated"] = True
        return True
    return False


def logout_admin():
    """Mengunci kembali hak akses admin."""
    st.session_state["is_admin_authenticated"] = False


def update_admin_pin(new_pin: str) -> bool:
    """Mengubah PIN admin (plain text)."""
    sm = get_sheets_manager()
    return sm.update_pengaturan("admin_pin", new_pin.strip())
