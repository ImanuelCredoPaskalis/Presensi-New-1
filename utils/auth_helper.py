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
    """Memverifikasi PIN input terhadap hash di pengaturan."""
    sm = get_sheets_manager()
    settings = sm.get_pengaturan()
    stored_hash = settings.get("admin_pin_hash", "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918")
    
    if hash_pin(input_pin) == stored_hash:
        st.session_state["is_admin_authenticated"] = True
        return True
    return False


def logout_admin():
    """Mengunci kembali hak akses admin."""
    st.session_state["is_admin_authenticated"] = False


def update_admin_pin(new_pin: str) -> bool:
    """Mengubah PIN admin dengan menyimpan hash barunya."""
    new_hash = hash_pin(new_pin)
    sm = get_sheets_manager()
    return sm.update_pengaturan("admin_pin_hash", new_hash)
