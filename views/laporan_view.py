import customtkinter as ctk
from tkinter import filedialog, messagebox

from controllers.laporan_controller import LaporanController
from utils.helpers import rupiah
from views.components import (DataTable, header_halaman, CARD_BG, BORDER, TEXT, MUTED,
                              ACCENT, HIJAU, MERAH, KUNING, BIRU)


class LaporanView(ctk.CTkFrame):
    """Laporan koperasi (Admin) dengan ekspor CSV."""

    def __init__(self, master, user):
        super().__init__(master, fg_color="transparent")
        self.ctrl = LaporanController(user)
        header_halaman(self, "Laporan Koperasi", "Ringkasan keuangan koperasi",
                       [("Ekspor CSV", self.ekspor, ACCENT)])
        r = self.ctrl.ringkasan()
        kartu = [
            ("Total Anggota", f"{r.get('anggota', 0)} Orang", ACCENT),
            ("Total Simpanan", rupiah(r.get('simpanan')), HIJAU),
            ("Pokok / Wajib / Sukarela", " / ".join(rupiah(r.get(k)).replace("Rp ", "")
                                                    for k in ("simpanan_pokok", "simpanan_wajib", "simpanan_sukarela")), HIJAU),
            ("Total Pencairan Pinjaman", rupiah(r.get('pencairan')), BIRU),
            ("Sisa Pinjaman", rupiah(r.get('sisa')), MERAH),
            ("Angsuran Diterima", rupiah(r.get('angsuran')), HIJAU),
            ("Denda Terkumpul", rupiah(r.get('denda')), KUNING),
        ]
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="x")
        for i, (judul, nilai, warna) in enumerate(kartu):
            c = ctk.CTkFrame(grid, width=230, height=82, fg_color=CARD_BG, corner_radius=10,
                             border_width=1, border_color=BORDER)
            c.grid(row=i // 3, column=i % 3, padx=6, pady=6, sticky="nsew")
            c.pack_propagate(False)
            ctk.CTkFrame(c, height=4, fg_color=warna, corner_radius=0).pack(fill="x")
            ctk.CTkLabel(c, text=judul, text_color=MUTED, font=ctk.CTkFont(size=11, weight="bold")).pack(
                anchor="w", padx=12, pady=(8, 0))
            ctk.CTkLabel(c, text=nilai, text_color=TEXT, font=ctk.CTkFont(size=15, weight="bold")).pack(
                anchor="w", padx=12)
        ctk.CTkLabel(self, text="Rekap per anggota", font=ctk.CTkFont(weight="bold"), text_color=TEXT).pack(
            anchor="w", pady=(12, 4))
        self.tabel = DataTable(self, [("ID", 50, "center"), ("Nama Anggota", 220, "w"),
                                      ("Total Simpanan", 150, "e"), ("Sisa Pinjaman", 150, "e")], baris=6)
        self.tabel.pack(fill="both", expand=True)
        self.tabel.isi([(x['id_anggota'], x['nama_anggota'], rupiah(x['total_simpanan']),
                         rupiah(x['sisa_pinjaman'])) for x in self.ctrl.per_anggota()])

    def ekspor(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="laporan_koperasi.csv",
                                            filetypes=[("CSV", "*.csv")])
        if path:
            self.ctrl.ekspor_csv(path)
            messagebox.showinfo("Berhasil", f"Laporan disimpan di:\n{path}")
