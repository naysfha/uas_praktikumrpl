from models.anggota_model import AnggotaModel
from models.simpanan_model import SimpananModel
from utils.helpers import aksi, baca, parse_nominal, parse_tanggal

# Daftar jenis simpanan yang diizinkan di koperasi
JENIS = ["Pokok", "Wajib", "Sukarela"]


class SimpananController:
    # Menyimpan data user yang sedang login
    def __init__(self, user):
        self.user = user

    @baca(list)
    # Melihat riwayat simpanan (semua atau berdasarkan pencarian)
    def riwayat(self, keyword=""):
        return SimpananModel.riwayat(keyword=keyword.strip())

    @baca(list)
    # Mengambil daftar semua anggota (dropdown)
    def daftar_anggota(self):
        return AnggotaModel.semua()

    @aksi
    # Role Petugas: Mencatat transaksi simpanan baru 
    def catat(self, id_anggota, jenis, tanggal, jumlah, keterangan):
        if self.user['role'] != 'Petugas':
            return False, "Hanya Petugas yang dapat mencatat simpanan."
        
        # Validasi input tanggal (harus format YYYY-MM-DD)
        tgl = parse_tanggal(tanggal)
        
        # Validasi nominal (harus angka > 0)
        nominal = parse_nominal(jumlah)
        
        # Validasi jenis simpanan (harus salah satu dari Pokok/Wajib/Sukarela)
        if jenis not in JENIS:
            return False, "Jenis simpanan tidak valid."
        if tgl is None:
            return False, "Format tanggal harus YYYY-MM-DD."
        if nominal is None:
            return False, "Jumlah harus berupa angka lebih dari 0."
        SimpananModel.tambah(id_anggota, self.user['id_pengguna'], jenis, tgl, nominal, keterangan or None)
        return True, "Simpanan berhasil dicatat."
