from models.user_model import UserModel
from utils.helpers import aksi, baca

# Daftar role yang diizinkan di sistem
ROLES = ["Admin", "Petugas", "Anggota"]

class PenggunaController:
    def __init__(self, user):
        # Menyimpan data admin yang sedang login (untuk cek hak akses)
        self.user = user

    @baca(list)
    def semua(self, keyword=""):
        # Ambil semua daftar pengguna (dengan fitur pencarian)
        return UserModel.semua(keyword.strip())

    @baca(lambda: None)
    # Ambil data pengguna berdasarkan ID
    def detail(self, id_pengguna):
        return UserModel.by_id(id_pengguna)

    # Mengecek apakah yang login benar-benar Admin
    def _admin(self):
        return self.user['role'] == 'Admin'

    @aksi
    # Role Admin: Menambah pengguna baru 
    def tambah(self, username, password, nama, role):
        if not self._admin():
            return False, "Hanya Admin yang dapat mengelola pengguna."
        if not username or not password or not nama:
            return False, "Semua kolom wajib diisi."
        if len(password) < 6:
            return False, "Password minimal 6 karakter."
        if role not in ROLES:
            return False, "Role tidak valid."
        UserModel.tambah(username, password, nama, role)
        return True, "Pengguna berhasil ditambahkan."

    @aksi
    # Role Admin: Mengubah data pengguna 
    def ubah(self, id_pengguna, username, nama, role):
        if not self._admin():
            return False, "Hanya Admin yang dapat mengelola pengguna."
        if not username or not nama:
            return False, "Username dan nama wajib diisi."
        if id_pengguna == self.user['id_pengguna'] and role != 'Admin':
            return False, "Anda tidak bisa menurunkan role akun Anda sendiri."
        UserModel.ubah(id_pengguna, username, nama, role)
        return True, "Data pengguna berhasil diperbarui."

    @aksi
    # Role Admin: Mengganti password/mereset pengguna 
    def reset_password(self, id_pengguna, password_baru):
        if not self._admin():
            return False, "Hanya Admin yang dapat mereset password."
        if len(password_baru) < 6:
            return False, "Password minimal 6 karakter."
        UserModel.reset_password(id_pengguna, password_baru)
        return True, "Password berhasil direset."

    @aksi
    # Role Admin: Menghapus pengguna
    def hapus(self, id_pengguna):
        if not self._admin():
            return False, "Hanya Admin yang dapat mengelola pengguna."
        
        # Mencegah admin menghapus akunnya sendiri yang sedang dipakai
        if id_pengguna == self.user['id_pengguna']:
            return False, "Anda tidak bisa menghapus akun yang sedang dipakai."
        UserModel.hapus(id_pengguna)
        return True, "Pengguna berhasil dihapus."

    @aksi
    # Semua Role dapat mengganti passwordnya sendiri
    def ganti_password(self, lama, baru, konfirmasi):
        if not lama or not baru:
            return False, "Semua kolom wajib diisi."
        if len(baru) < 6:
            return False, "Password baru minimal 6 karakter."
        if baru != konfirmasi:
            return False, "Konfirmasi password tidak sama."
        UserModel.ganti_password(self.user['id_pengguna'], lama, baru)
        return True, "Password berhasil diganti."
