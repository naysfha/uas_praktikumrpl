import functools
import re
from calendar import monthrange
from datetime import date, datetime
from decimal import Decimal

import mysql.connector

class AturanBisnis(Exception):
    # Jika pelanggaran aturan koperasi maka pesan langsung ditampilkan ke pengguna
    pass

# Mengubah angka menjadi format mata uang Rupiah (string)
def rupiah(n) -> str:
    n = Decimal(n or 0)
    return "Rp " + f"{n:,.0f}".replace(",", ".")

# Mengubah format tanggal database menjadi format Indonesia (string)
def tgl(d) -> str:
    return d.strftime("%d-%m-%Y") if d else "-"

# Mengubah input teks dari user menjadi angka desimal (Decimal)
def parse_nominal(teks):
    t = str(teks).strip().lower().replace("rp", "").replace(" ", "")
    t = t.replace(",", ".")     #  # Ganti koma jadi titik (kalau user ngetik desimal)
    v = Decimal(t)
    return v

# Mengubah input teks tanggal (YYYY-MM-DD) menjadi objek date Python.
def parse_tanggal(teks):
    return datetime.strptime(str(teks).strip(), "%Y-%m-%d").date()

# Memastikan NIK berisi tepat 16 digit angka
def validasi_nik(nik: str) -> bool:
    return bool(re.fullmatch(r"\d{16}", nik))

# Memastikan nomor HP diawali 08 dan panjangnya 12 atau 13 digit
def validasi_hp(hp: str) -> bool:
    return bool(re.fullmatch(r"08\d{10,11}", hp))

# Menambahkan n bulan ke tanggal d.
def tambah_bulan(d: date, n: int) -> date:
    total_bulan = d.month - 1 + n   # Menghitung total bulan
    y = d.year + total_bulan // 12  # Hitung tahun
    m = total_bulan % 12 + 1        # Bulan baru
    tanggal_akhir = monthrange(y, m)[1]
    return date(y, m, min(d.day,tanggal_akhir))

# Menerjemahkan error MySQL menjadi pesan yang ramah dibaca user
def pesan_error(err) -> str:
    if isinstance(err, mysql.connector.IntegrityError):
        if err.errno == 1062:
            return "Data sudah terdaftar (NIK / username tidak boleh sama)."
        if err.errno == 1451:
            return "Data tidak bisa dihapus karena masih dipakai data lain (transaksi/pinjaman)."
        if err.errno == 1452:
            return "Data referensi tidak valid."
    return f"Kesalahan database: {err}"

# Dekorator (pelindung fungsi dari crash (try...except agar tidak ditulis berulang))
def aksi(fn):
    @functools.wraps(fn)
    def bungkus(*a, **k):
        try:
            return fn(*a, **k)
        except AturanBisnis as e:
            return False, str(e)
        except (mysql.connector.Error, ConnectionError) as e:
            return False, pesan_error(e)
    return bungkus


def baca(default_factory):
    def deco(fn):
        @functools.wraps(fn)
        def bungkus(*a, **k):
            try:
                return fn(*a, **k)
            except (mysql.connector.Error, ConnectionError) as e:
                print(f"[DB] {fn.__name__}: {e}")
                return default_factory()
        return bungkus
    return deco
