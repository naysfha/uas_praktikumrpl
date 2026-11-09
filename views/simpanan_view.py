from datetime import date
import customtkinter as ctk

from controllers.simpanan_controller import SimpananController, JENIS
from utils.helpers import rupiah, tgl
from views.components import (DataTable, FormDialog, header_halaman, kotak_cari, ACCENT, MUTED)
from tkinter import messagebox


class SimpananView(ctk.CTkFrame):
    """Transaksi simpanan (Petugas)."""

    def __init__(self, master, user):
        super().__init__(master, fg_color="transparent")
        self.ctrl = SimpananController(user)
        header_halaman(self, "Transaksi Simpanan", "Catat setoran simpanan anggota",
                       [("+ Catat Simpanan", self.form_catat, ACCENT)])
        self.cari = kotak_cari(self, self.refresh, "Cari nama anggota / jenis simpanan")
        self.tabel = DataTable(self, [
            ("ID", 50, "center"), ("Tanggal", 90, "center"), ("Anggota", 170, "w"), ("Jenis", 80, "center"),
            ("Jumlah", 120, "e"), ("Keterangan", 180, "w"), ("Petugas", 120, "w")])
        self.tabel.pack(fill="both", expand=True)
        self.lbl_total = ctk.CTkLabel(self, text="", text_color=MUTED)
        self.lbl_total.pack(anchor="e", pady=(6, 0))
        self.refresh()

    def refresh(self):
        rows = self.ctrl.riwayat(self.cari.get())
        self.tabel.isi([(r['id_simpanan'], tgl(r['tanggal_simpanan']), r['nama_anggota'], r['jenis_simpanan'],
                         rupiah(r['saldo']), r['keterangan'], r['petugas']) for r in rows])
        self.lbl_total.configure(text=f"{len(rows)} transaksi  |  Total: {rupiah(sum(r['saldo'] for r in rows))}")

    def form_catat(self):
        anggota = self.ctrl.daftar_anggota()
        if not anggota:
            messagebox.showinfo("Belum Ada Anggota", "Belum ada data anggota yang terdaftar.")
            return
        opsi = [f"{a['id_anggota']} - {a['nama_anggota']}" for a in anggota]
        fields = [
            {"key": "anggota", "label": "Anggota:", "kind": "option", "opsi": opsi},
            {"key": "jenis", "label": "Jenis Simpanan:", "kind": "option", "opsi": JENIS, "value": "Wajib"},
            {"key": "tanggal", "label": "Tanggal (YYYY-MM-DD):", "value": date.today().isoformat()},
            {"key": "jumlah", "label": "Jumlah (Rp):", "placeholder": "contoh: 100000 atau 100.000"},
            {"key": "ket", "label": "Keterangan (opsional):"},
        ]
        FormDialog(self, "Catat Simpanan", fields,
                   lambda d: self.ctrl.catat(int(d['anggota'].split(" - ")[0]), d['jenis'], d['tanggal'],
                                             d['jumlah'], d['ket']), self.refresh)
