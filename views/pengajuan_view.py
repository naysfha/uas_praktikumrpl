import customtkinter as ctk
from tkinter import messagebox

from config.settings import BUNGA_TAHUNAN_DEFAULT, JANGKA_WAKTU_PILIHAN
from controllers.pinjaman_controller import PinjamanController
from utils.helpers import rupiah, tgl
from views.components import (DataTable, FormDialog, header_halaman, pilih_baris, tampilkan_hasil,
                              CARD_BG, BORDER, TEXT, MUTED, HIJAU, MERAH, KUNING, ACCENT)


class PengajuanAnggotaView(ctk.CTkFrame):
    """Anggota: mengajukan pinjaman & melihat status pengajuannya."""

    def __init__(self, master, user):
        super().__init__(master, fg_color="transparent")
        self.ctrl = PinjamanController(user)
        header_halaman(self, "Pengajuan Peminjaman", "Ajukan pinjaman dan pantau statusnya")

        if not self.ctrl.profil():
            ctk.CTkLabel(self, text="Lengkapi menu 'Data Diri / Profil' terlebih dahulu sebelum mengajukan pinjaman.",
                         text_color=KUNING, font=ctk.CTkFont(size=13)).pack(anchor="w", pady=10)
            return

        form = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=10, border_width=1, border_color=BORDER)
        form.pack(fill="x", pady=(0, 14))
        baris = ctk.CTkFrame(form, fg_color="transparent")
        baris.pack(fill="x", padx=16, pady=(14, 4))

        ctk.CTkLabel(baris, text="Jumlah (Rp)", text_color=MUTED).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(baris, text="Jangka Waktu (bulan)", text_color=MUTED).grid(row=0, column=1, sticky="w", padx=12)
        ctk.CTkLabel(baris, text="Tujuan Pinjaman", text_color=MUTED).grid(row=0, column=2, sticky="w")
        self.e_jumlah = ctk.CTkEntry(baris, width=170, placeholder_text="5.000.000")
        self.e_jumlah.grid(row=1, column=0)
        self.v_jangka = ctk.StringVar(value="12")
        ctk.CTkOptionMenu(baris, values=[str(x) for x in JANGKA_WAKTU_PILIHAN], variable=self.v_jangka,
                          width=140, command=lambda _: self.hitung()).grid(row=1, column=1, padx=12)
        self.e_tujuan = ctk.CTkEntry(baris, width=260, placeholder_text="Modal usaha, biaya sekolah, dll")
        self.e_tujuan.grid(row=1, column=2)
        ctk.CTkButton(baris, text="Ajukan", fg_color=ACCENT, width=100, command=self.kirim).grid(
            row=1, column=3, padx=(12, 0))
        self.e_jumlah.bind("<KeyRelease>", lambda e: self.hitung())

        self.lbl_est = ctk.CTkLabel(form, text="Estimasi angsuran: -", text_color=MUTED)
        self.lbl_est.pack(anchor="w", padx=16, pady=(2, 12))

        self.tabel = DataTable(self, [
            ("ID", 50, "center"), ("Tanggal", 90, "center"), ("Jumlah", 120, "e"), ("Jangka", 70, "center"),
            ("Tujuan", 200, "w"), ("Status", 90, "center"), ("Catatan Petugas", 200, "w")])
        self.tabel.pack(fill="both", expand=True)
        self.refresh()

    def hitung(self):
        self.lbl_est.configure(text=self.ctrl.estimasi(self.e_jumlah.get(), self.v_jangka.get()))

    def refresh(self):
        self.tabel.isi([(r['id_pengajuan'], tgl(r['tanggal_pengajuan']), rupiah(r['jumlah_pengajuan']),
                         f"{r['jangka_waktu']} bln", r['tujuan_pinjaman'], r['status_pengajuan'], r['catatan'])
                        for r in self.ctrl.pengajuan_saya()])

    def kirim(self):
        ok, pesan = self.ctrl.ajukan(self.e_jumlah.get(), self.v_jangka.get(), self.e_tujuan.get())
        if tampilkan_hasil(ok, pesan):
            self.e_jumlah.delete(0, "end")
            self.e_tujuan.delete(0, "end")
            self.hitung()
            self.refresh()


class PengajuanPetugasView(ctk.CTkFrame):
    """Petugas: menyetujui / menolak pengajuan pinjaman."""

    def __init__(self, master, user):
        super().__init__(master, fg_color="transparent")
        self.ctrl = PinjamanController(user)
        header_halaman(self, "Pengajuan Pinjaman", "Tinjau pengajuan pinjaman anggota",
                       [("Setujui", self.setujui, HIJAU), ("Tolak", self.tolak, MERAH)])
        self.v_filter = ctk.StringVar(value="menunggu")
        ctk.CTkSegmentedButton(self, values=["menunggu", "disetujui", "ditolak", "semua"],
                               variable=self.v_filter, command=lambda _: self.refresh()).pack(anchor="w", pady=(0, 10))
        self.tabel = DataTable(self, [
            ("ID", 50, "center"), ("Tanggal", 90, "center"), ("Anggota", 160, "w"), ("Jumlah", 120, "e"),
            ("Jangka", 70, "center"), ("Tujuan", 170, "w"), ("Status", 90, "center"), ("Catatan", 160, "w")])
        self.tabel.pack(fill="both", expand=True)
        self.refresh()

    def refresh(self):
        f = self.v_filter.get()
        rows = self.ctrl.pengajuan_semua(None if f == "semua" else f)
        self.tabel.isi([(r['id_pengajuan'], tgl(r['tanggal_pengajuan']), r['nama_anggota'],
                         rupiah(r['jumlah_pengajuan']), f"{r['jangka_waktu']} bln", r['tujuan_pinjaman'],
                         r['status_pengajuan'], r['catatan']) for r in rows])

    def _pilih_menunggu(self):
        v = pilih_baris(self.tabel)
        if v and v[6] != "menunggu":
            messagebox.showinfo("Sudah Diproses", "Pengajuan ini sudah diproses.")
            return None
        return v

    def setujui(self):
        v = self._pilih_menunggu()
        if not v:
            return
        fields = [
            {"kind": "info", "value": f"{v[2]} mengajukan {v[3]} selama {v[4]}."},
            {"key": "bunga", "label": "Bunga flat per tahun (%):", "value": f"{BUNGA_TAHUNAN_DEFAULT:g}"},
            {"key": "catatan", "label": "Catatan (opsional):"},
        ]
        FormDialog(self, "Setujui Pengajuan", fields,
                   lambda d: self.ctrl.proses(int(v[0]), True, d['catatan'], d['bunga']),
                   self.refresh, tombol="Setujui & Cairkan")

    def tolak(self):
        v = self._pilih_menunggu()
        if not v:
            return
        fields = [
            {"kind": "info", "value": f"Tolak pengajuan {v[2]} sebesar {v[3]}?"},
            {"key": "catatan", "label": "Alasan penolakan:"},
        ]
        FormDialog(self, "Tolak Pengajuan", fields,
                   lambda d: self.ctrl.proses(int(v[0]), False, d['catatan']), self.refresh, tombol="Tolak")
