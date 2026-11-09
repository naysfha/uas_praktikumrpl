import customtkinter as ctk
from tkinter import messagebox

from controllers.anggota_controller import AnggotaController
from views.components import (DataTable, FormDialog, header_halaman, kotak_cari, pilih_baris,
                             tampilkan_hasil, BIRU, MERAH)

class AnggotaView(ctk.CTkFrame):
    # Admin: tambah/ubah/hapus
    # Petugas: hanya tampil tabel + ubah + hapus (tanpa tambah)
    def __init__(self, master, user):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self.ctrl = AnggotaController(user) # Hubungkan ke controller
        admin = user['role'] == 'Admin'
        tombol = [("Ubah", self.form_ubah, BIRU), ("Hapus", self.hapus, MERAH)]
        
        # Tampilkan judul halaman + tombol aksi
        header_halaman(self, "Kelola Anggota" if admin else "Data Anggota",
                       "Daftar anggota koperasi" if admin else "Lihat, ubah, dan hapus data anggota",
                       tombol)
        
        # Kolom pencarian
        self.cari = kotak_cari(self, self.refresh, "Cari nama / NIK / username")
        
        # Tabel data anggota
        self.tabel = DataTable(self, [
            ("ID", 50, "center"), ("NIK", 150, "center"), ("Nama Lengkap", 190, "w"),
            ("No. Telepon", 120, "center"), ("Alamat", 220, "w"), ("Username", 120, "w")])
        self.tabel.pack(fill="both", expand=True)
        self.refresh()

    # Ambil data dari controller, lalu masukkan ke tabel
    def refresh(self):
        rows = self.ctrl.semua(self.cari.get())
        self.tabel.isi([(r['id_anggota'], r['nik'], r['nama_anggota'], r['no_hp'], r['alamat'], r['username'])
                        for r in rows])

    #  Menyusun daftar isian form (dipakai untuk tambah & ubah)
    def _fields(self, a=None):
        a = a or {}
        return [
            {"key": "nik", "label": "NIK:", "placeholder": "16 digit NIK", "value": a.get('nik')},
            {"key": "nama", "label": "Nama Lengkap:", "value": a.get('nama_anggota')},
            {"key": "hp", "label": "No. Telepon / HP:", "placeholder": "08123456789", "value": a.get('no_hp')},
            {"key": "alamat", "label": "Alamat:", "value": a.get('alamat')},
        ]

    # Ambil akun pengguna yang belum punya data anggota
    def form_tambah(self):
        akun = self.ctrl.akun_tersedia()
        if not akun:
            messagebox.showinfo("Tidak Ada Akun",
                                "Semua akun Anggota sudah terdaftar.\nMinta calon anggota registrasi akun dulu.")
            return
        
        # Ubah list akun jadi format pilihan (dropdown)
        opsi = [f"{x['id_pengguna']} - {x['username']} ({x['nama_pengguna']})" for x in akun]
        fields = [{"key": "akun", "label": "Akun Pengguna:", "kind": "option", "opsi": opsi}] + self._fields()

        # Fungsi yang dijalankan saat tombol Simpan diklik
        def kirim(d):
            return self.ctrl.tambah(int(d['akun'].split(" - ")[0]), d['nik'], d['nama'], d['hp'], d['alamat'])
        FormDialog(self, "Tambah Anggota", fields, kirim, self.refresh)

    def form_ubah(self):
        v = pilih_baris(self.tabel)
        if not v:
            return
        
        # Ambil data detail anggota
        id_anggota = int(v[0])
        a = self.ctrl.detail(id_anggota)
        if not a:
            return
        
        # Buka form ubah dengan data lama terisi otomatis
        FormDialog(self, "Ubah Data Anggota", self._fields(a),
                   lambda d: self.ctrl.ubah(id_anggota, d['nik'], d['nama'], d['hp'], d['alamat']),
                   self.refresh)

    def hapus(self):
        v = pilih_baris(self.tabel)
        if not v:
            return
        # Menampilkan pop up, konfirmasi ulang
        if messagebox.askyesno("Konfirmasi", f"Hapus data anggota '{v[2]}'?"):
           # Hapus dari database
            if tampilkan_hasil(*self.ctrl.hapus(int(v[0]))):
                self.refresh()