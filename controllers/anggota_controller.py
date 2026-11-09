from models.anggota_model import AnggotaModel
from utils.helpers import aksi, baca, validasi_nik, validasi_hp

# Fungsi bantuan untuk mengecek apakah inputan form sudah benar
def _validasi(nik, nama, hp):
    if not nik or not nama or not hp:
        return "NIK, nama, dan nomor HP wajib diisi."
    if not validasi_nik(nik):
        return "NIK harus 16 digit angka."
    if not validasi_hp(hp):
        return "No. HP tidak valid (contoh: 08123456789)."
    return None


class AnggotaController:
    def __init__(self, user):
        # Menyimpan data user yang sedang login (id, nama, role)
        self.user = user

    # Mengambil semua daftar anggota. @baca(list) artinya kalau DB error, kembalikan list kosong []
    @baca(list)
    def semua(self, keyword=""):
        return AnggotaModel.semua(keyword.strip())

    # Mengambil detail 1 anggota. @baca(lambda: None) artinya kalau error, kembalikan None
    @baca(lambda: None)
    def detail(self, id_anggota):
        return AnggotaModel.by_id(id_anggota)

    # Mengambil akun (role Anggota) yang belum punya data profil anggota
    @baca(list)
    def akun_tersedia(self):
        return AnggotaModel.pengguna_belum_terdaftar()

    # @aksi artinya proses simpan data (helpers)
    @aksi
    # Cek Hak Akses: Hanya Admin yang boleh menambah anggota
    def tambah(self, id_pengguna, nik, nama, hp, alamat):
        if self.user['role'] != 'Admin':
            return False, "Hanya Admin yang dapat menambah anggota."
        salah = _validasi(nik, nama, hp)
        if salah:
            return False, salah
        AnggotaModel.tambah(id_pengguna, nik, nama, hp, alamat or None)
        return True, "Anggota berhasil ditambahkan."

    @aksi
    # Cek Hak Akses: Hanya Admin yang boleh mengubah anggota
    def ubah(self, id_anggota, nik, nama, hp, alamat):
        if self.user['role'] not in ('Admin', 'Petugas'):
            return False, "Anda tidak berhak mengubah data anggota."
        salah = _validasi(nik, nama, hp)
        if salah:
            return False, salah
        AnggotaModel.ubah(id_anggota, nik, nama, hp, alamat or None)
        return True, "Data anggota berhasil diperbarui."

    @aksi
    # Cek Hak Akses: Hanya Admin dan Petugas yang boleh menghapus
    def hapus(self, id_anggota):
        if self.user['role'] not in ('Admin', 'Petugas'):
            return False, "Anda tidak berhak menghapus data anggota."
        AnggotaModel.hapus(id_anggota)
        return True, "Data anggota berhasil dihapus."

    # ---------- Data diri (role Anggota) ----------
    @baca(lambda: None)
    # Mengambil data profil milik anggota yang sedang login
    def profil(self):
        return AnggotaModel.by_pengguna(self.user['id_pengguna'])

    @aksi
    # Menyimpan/memperbarui profil diri sendiri (dilakukan oleh Anggota)
    def simpan_profil(self, nik, nama, hp, alamat):
        salah = _validasi(nik, nama, hp)
        if salah:
            return False, salah
        AnggotaModel.simpan_profil(self.user['id_pengguna'], nik, nama, hp, alamat or None)
        return True, "Data diri berhasil disimpan."
