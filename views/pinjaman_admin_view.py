import customtkinter as ctk
from tkinter import messagebox

from controllers.pinjaman_controller import PinjamanController
from views.angsuran_view import baris_pinjaman, baris_jadwal, KOLOM_PINJAMAN, KOLOM_JADWAL
from views.components import DataTable, header_halaman, pilih_baris, tampilkan_hasil, KUNING, BIRU


class PinjamanAdminView(ctk.CTkFrame):
    """Kelola Pinjaman (Admin): pantau semua pinjaman, jadwal, dan ubah status."""

    def __init__(self, master, user):
        super().__init__(master, fg_color="transparent")
        self.ctrl = PinjamanController(user)
        header_halaman(self, "Kelola Pinjaman", "Pantau seluruh pinjaman anggota",
                       [("Tandai Bermasalah", lambda: self.ubah("bermasalah"), KUNING),
                        ("Tandai Berjalan", lambda: self.ubah("berjalan"), BIRU)])
        self.v_filter = ctk.StringVar(value="semua")
        ctk.CTkSegmentedButton(self, values=["semua", "berjalan", "bermasalah", "lunas"],
                               variable=self.v_filter, command=lambda _: self.refresh()).pack(anchor="w", pady=(0, 10))
        self.tabel = DataTable(self, KOLOM_PINJAMAN, baris=7, on_pilih=self.pilih)
        self.tabel.pack(fill="both", expand=True)
        ctk.CTkLabel(self, text="Jadwal angsuran pinjaman terpilih", font=ctk.CTkFont(weight="bold")).pack(
            anchor="w", pady=(10, 4))
        self.jadwal = DataTable(self, KOLOM_JADWAL, baris=6)
        self.jadwal.pack(fill="both", expand=True)
        self.refresh()

    def refresh(self):
        f = self.v_filter.get()
        self.tabel.isi([baris_pinjaman(r) for r in self.ctrl.pinjaman(None if f == "semua" else f)])
        self.jadwal.isi([])

    def pilih(self):
        v = self.tabel.terpilih()
        if v:
            self.jadwal.isi([baris_jadwal(j) for j in self.ctrl.jadwal(int(v[0]))])

    def ubah(self, status):
        v = pilih_baris(self.tabel)
        if v and messagebox.askyesno("Konfirmasi", f"Ubah status pinjaman #{v[0]} ({v[1]}) menjadi '{status}'?"):
            if tampilkan_hasil(*self.ctrl.ubah_status(int(v[0]), status)):
                self.refresh()
