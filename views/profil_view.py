import customtkinter as ctk

from controllers.anggota_controller import AnggotaController
from controllers.pengguna_controller import PenggunaController
from views.components import (FormDialog, header_halaman, ACCENT, BIRU, CARD_BG, BORDER, TEXT, MUTED, KUNING)


class ProfilView(ctk.CTkFrame):
    """Data diri untuk role Anggota (pengganti menu Data Anggota)."""

    def __init__(self, master, user):
        super().__init__(master, fg_color="transparent")
        self.user = user
        self.ctrl = AnggotaController(user)
        self.pw = PenggunaController(user)
        header_halaman(self, "Data Diri / Profil", "Informasi pribadi Anda sebagai anggota koperasi")
        self.kartu = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=10, border_width=1, border_color=BORDER)
        self.kartu.pack(fill="x")
        self.render()

    def _baris(self, label, nilai):
        r = ctk.CTkFrame(self.kartu, fg_color="transparent")
        r.pack(fill="x", padx=24, pady=5)
        ctk.CTkLabel(r, text=label, width=140, anchor="w", text_color=MUTED,
                     font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
        ctk.CTkLabel(r, text=nilai or "-", anchor="w", text_color=TEXT, wraplength=520,
                     justify="left").pack(side="left")

    def render(self):
        for w in self.kartu.winfo_children():
            w.destroy()
        a = self.ctrl.profil()
        ctk.CTkFrame(self.kartu, height=1, fg_color="transparent").pack(pady=6)
        self._baris("Username", self.user['username'])
        if a:
            self._baris("NIK", a['nik'])
            self._baris("Nama Lengkap", a['nama_anggota'])
            self._baris("No. Telepon", a['no_hp'])
            self._baris("Alamat", a['alamat'])
        else:
            ctk.CTkLabel(self.kartu, text="Data diri belum dilengkapi. Lengkapi dulu agar bisa mengajukan pinjaman.",
                         text_color=KUNING).pack(anchor="w", padx=24, pady=10)
        tombol = ctk.CTkFrame(self.kartu, fg_color="transparent")
        tombol.pack(anchor="w", padx=24, pady=(12, 20))
        ctk.CTkButton(tombol, text="Ubah Data Diri" if a else "Lengkapi Data Diri", fg_color=ACCENT,
                      command=lambda: self.form_profil(a)).pack(side="left", padx=(0, 8))
        ctk.CTkButton(tombol, text="Ganti Password", fg_color=BIRU, command=self.form_password).pack(side="left")

    def form_profil(self, a):
        a = a or {}
        fields = [
            {"key": "nik", "label": "NIK:", "placeholder": "16 digit NIK", "value": a.get('nik')},
            {"key": "nama", "label": "Nama Lengkap:", "value": a.get('nama_anggota') or self.user['nama_pengguna']},
            {"key": "hp", "label": "No. Telepon / HP:", "placeholder": "08123456789", "value": a.get('no_hp')},
            {"key": "alamat", "label": "Alamat:", "value": a.get('alamat')},
        ]
        FormDialog(self, "Data Diri", fields,
                   lambda d: self.ctrl.simpan_profil(d['nik'], d['nama'], d['hp'], d['alamat']), self.render)

    def form_password(self):
        fields = [
            {"key": "lama", "label": "Password Lama:", "kind": "password"},
            {"key": "baru", "label": "Password Baru (min. 6 karakter):", "kind": "password"},
            {"key": "konf", "label": "Konfirmasi Password Baru:", "kind": "password"},
        ]
        FormDialog(self, "Ganti Password", fields,
                   lambda d: self.pw.ganti_password(d['lama'], d['baru'], d['konf']))
