import customtkinter as ctk

from controllers.pinjaman_controller import PinjamanController
from utils.helpers import rupiah, tgl
from views.angsuran_view import baris_pinjaman, KOLOM_PINJAMAN
from views.components import DataTable, header_halaman, MUTED


class RiwayatView(ctk.CTkFrame):
    """Riwayat simpanan, pinjaman, dan angsuran per anggota (Petugas)."""

    def __init__(self, master, user):
        super().__init__(master, fg_color="transparent")
        self.ctrl = PinjamanController(user)
        header_halaman(self, "Riwayat Anggota", "Rekap transaksi per anggota")
        self.anggota = self.ctrl.daftar_anggota()
        if not self.anggota:
            ctk.CTkLabel(self, text="Belum ada data anggota.", text_color=MUTED).pack(anchor="w")
            return
        self.opsi = {f"{a['id_anggota']} - {a['nama_anggota']}": a['id_anggota'] for a in self.anggota}
        self.v_anggota = ctk.StringVar(value=next(iter(self.opsi)))
        ctk.CTkOptionMenu(self, values=list(self.opsi), variable=self.v_anggota, width=320,
                          command=lambda _: self.refresh()).pack(anchor="w", pady=(0, 10))
        tab = ctk.CTkTabview(self)
        tab.pack(fill="both", expand=True)
        for nama in ("Simpanan", "Pinjaman", "Angsuran"):
            tab.add(nama)
        self.t_simpanan = DataTable(tab.tab("Simpanan"), [
            ("ID", 50, "center"), ("Tanggal", 90, "center"), ("Jenis", 90, "center"),
            ("Jumlah", 130, "e"), ("Keterangan", 220, "w"), ("Petugas", 130, "w")])
        self.t_pinjaman = DataTable(tab.tab("Pinjaman"), KOLOM_PINJAMAN)
        self.t_angsuran = DataTable(tab.tab("Angsuran"), [
            ("ID", 50, "center"), ("Tanggal", 90, "center"), ("Pinjaman", 70, "center"), ("Ke", 50, "center"),
            ("Dibayar", 120, "e"), ("Denda", 100, "e"), ("Petugas", 130, "w"), ("Keterangan", 160, "w")])
        for t in (self.t_simpanan, self.t_pinjaman, self.t_angsuran):
            t.pack(fill="both", expand=True)
        self.refresh()

    def refresh(self):
        ida = self.opsi[self.v_anggota.get()]
        self.t_simpanan.isi([(r['id_simpanan'], tgl(r['tanggal_simpanan']), r['jenis_simpanan'],
                              rupiah(r['saldo']), r['keterangan'], r['petugas'])
                             for r in self.ctrl.riwayat_simpanan(ida)])
        self.t_pinjaman.isi([baris_pinjaman(r) for r in self.ctrl.riwayat_pinjaman(ida)])
        self.t_angsuran.isi([(r['id_angsuran'], tgl(r['tanggal_bayar']), r['id_pinjaman'], r['angsuran_ke'],
                              rupiah(r['jumlah_bayar']), rupiah(r['denda']), r['petugas'], r['keterangan'])
                             for r in self.ctrl.riwayat_angsuran(ida)])
