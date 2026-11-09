import customtkinter as ctk
from tkinter import messagebox

from controllers.pengguna_controller import PenggunaController, ROLES
from views.components import (DataTable, FormDialog, header_halaman, kotak_cari, pilih_baris,
                              tampilkan_hasil, ACCENT, BIRU, KUNING, MERAH)


class PenggunaView(ctk.CTkFrame):
    """Manajemen akun pengguna (Admin)."""

    def __init__(self, master, user):
        super().__init__(master, fg_color="transparent")
        self.ctrl = PenggunaController(user)
        header_halaman(self, "Manajemen Pengguna", "Kelola akun Admin, Petugas, dan Anggota",
                       [("Ubah", self.form_ubah, BIRU),
                        ("Reset PW", self.form_reset, KUNING), ("Hapus", self.hapus, MERAH)])
        self.cari = kotak_cari(self, self.refresh, "Cari username / nama / role")
        self.tabel = DataTable(self, [("ID", 50, "center"), ("Username", 200, "w"),
                                      ("Nama Pengguna", 240, "w"), ("Role", 100, "center")])
        self.tabel.pack(fill="both", expand=True)
        self.refresh()

    def refresh(self):
        self.tabel.isi([(r['id_pengguna'], r['username'], r['nama_pengguna'], r['role'])
                        for r in self.ctrl.semua(self.cari.get())])

    def form_tambah(self):
        fields = [
            {"key": "username", "label": "Username:", "placeholder": "@username"},
            {"key": "nama", "label": "Nama Pengguna:"},
            {"key": "password", "label": "Password (min. 6 karakter):", "kind": "password"},
            {"key": "role", "label": "Role:", "kind": "option", "opsi": ROLES, "value": "Petugas"},
        ]
        FormDialog(self, "Tambah Pengguna", fields,
                   lambda d: self.ctrl.tambah(d['username'], d['password'], d['nama'], d['role']), self.refresh)

    def form_ubah(self):
        v = pilih_baris(self.tabel)
        if not v:
            return
        idp = int(v[0])
        fields = [
            {"key": "username", "label": "Username:", "value": v[1]},
            {"key": "nama", "label": "Nama Pengguna:", "value": v[2]},
            {"key": "role", "label": "Role:", "kind": "option", "opsi": ROLES, "value": v[3]},
        ]
        FormDialog(self, "Ubah Pengguna", fields,
                   lambda d: self.ctrl.ubah(idp, d['username'], d['nama'], d['role']), self.refresh)

    def form_reset(self):
        v = pilih_baris(self.tabel)
        if not v:
            return
        FormDialog(self, f"Reset Password - {v[1]}", [
            {"key": "pw", "label": "Password Baru (min. 6 karakter):", "kind": "password"}],
            lambda d: self.ctrl.reset_password(int(v[0]), d['pw']), tombol="Reset Password")

    def hapus(self):
        v = pilih_baris(self.tabel)
        if v and messagebox.askyesno("Konfirmasi", f"Hapus pengguna '{v[1]}'?"):
            if tampilkan_hasil(*self.ctrl.hapus(int(v[0]))):
                self.refresh()
