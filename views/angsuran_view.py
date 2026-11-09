import customtkinter as ctk

from controllers.pinjaman_controller import PinjamanController
from utils.helpers import rupiah, tgl
from views.components import (DataTable, FormDialog, header_halaman, pilih_baris, CARD_BG, BORDER, TEXT,
                              MUTED, HIJAU)

STATUS_JADWAL = {"belum_dibayar": "Belum dibayar", "lunas": "Lunas", "terlambat": "Terlambat"}

# Mengubah 1 data pinjaman (dict) menjadi 1 baris tabel (tuple)
def baris_pinjaman(r):
    return (r['id_pinjaman'], r['nama_anggota'], tgl(r['tanggal_pencairan']), rupiah(r['total_pinjaman']),
            rupiah(r['sisa_pinjaman']), f"{r['terbayar']} / {r['jangka_waktu']}", r['status_pinjaman'])

# Definisi kolom tabel pinjaman (Nama Kolom, Lebar, Posisi Teks)
KOLOM_PINJAMAN = [("ID", 50, "center"), ("Anggota", 170, "w"), ("Pencairan", 90, "center"),
                  ("Total", 120, "e"), ("Sisa", 120, "e"), ("Terbayar", 80, "center"), ("Status", 90, "center")]

# Definisi kolom tabel jadwal angsuran
KOLOM_JADWAL = [("Ke", 50, "center"), ("Jatuh Tempo", 100, "center"), ("Tagihan", 120, "e"),
                ("Denda", 100, "e"), ("Status", 110, "center")]

# Mengubah 1 data jadwal (dict) menjadi 1 baris tabel (tuple)
def baris_jadwal(j):
    return (j['angsuran_ke'], tgl(j['tanggal_jatuh_tempo']), rupiah(j['jumlah_tagihan']),
            rupiah(j['denda']), STATUS_JADWAL.get(j['status_jadwal'], j['status_jadwal']))

# Role Petugas: Pembayaran angsuran
class AngsuranView(ctk.CTkFrame):
    def __init__(self, master, user):
        super().__init__(master, fg_color="transparent")
        self.ctrl = PinjamanController(user)
        
        # Header halaman + tombol "Bayar Angsuran"
        header_halaman(self, "Pembayaran Angsuran", "Pilih pinjaman, lalu terima pembayaran angsuran berikutnya",
                       [("Bayar Angsuran", self.bayar, HIJAU)])
        self.tabel = DataTable(self, KOLOM_PINJAMAN, baris=6, on_pilih=self.pilih)
        self.tabel.pack(fill="both", expand=True)
        self.lbl_info = ctk.CTkLabel(self, text="Pilih pinjaman untuk melihat tagihan berikutnya.",
                                     text_color=MUTED, anchor="w", justify="left")
        self.lbl_info.pack(fill="x", pady=8)
        
        # Tabel detail jadwal angsuran
        self.jadwal = DataTable(self, KOLOM_JADWAL, baris=6)
        self.jadwal.pack(fill="both", expand=True)
        self.refresh()

    def refresh(self):
        self.tabel.isi([baris_pinjaman(r) for r in self.ctrl.pinjaman(aktif_saja=True)])
        self.jadwal.isi([])
        self.lbl_info.configure(text="Pilih pinjaman untuk melihat tagihan berikutnya.")

    # Dipanggil saat Petugas mengklik salah satu baris pinjaman
    def pilih(self):
        v = self.tabel.terpilih()
        if not v:
            return
        id_pinjaman = int(v[0])
        
        # Isi tabel jadwal dengan detail cicilan pinjaman
        self.jadwal.isi([baris_jadwal(j) for j in self.ctrl.jadwal(id_pinjaman)])
        # Ambil data tagihan berikutnya
        b = self.ctrl.angsuran_berikut(id_pinjaman)
        if b:
            total = b['jumlah_tagihan'] + b['denda_hari_ini']
            self.lbl_info.configure(text=(
                f"Angsuran ke-{b['angsuran_ke']}  |  Jatuh tempo {tgl(b['tanggal_jatuh_tempo'])}  |  "
                f"Tagihan {rupiah(b['jumlah_tagihan'])}  |  Denda {rupiah(b['denda_hari_ini'])}  |  "
                f"Total bayar {rupiah(total)}"))
        else:
            self.lbl_info.configure(text="Semua angsuran sudah lunas.")
    
    # Dipanggil saat tombol "Bayar Angsuran" diklik
    def bayar(self):
        v = pilih_baris(self.tabel, "Pilih pinjaman yang akan dibayar angsurannya.")
        if not v:
            return
        id_pinjaman = int(v[0])
        b = self.ctrl.angsuran_berikut(id_pinjaman)
        if not b:
            self.lbl_info.configure(text="Semua angsuran sudah lunas.")
            return
        
        # Hitung total yang harus dibayar (tagihan + denda)
        total = b['jumlah_tagihan'] + b['denda_hari_ini']
        ringkas = (f"{v[1]} - angsuran ke-{b['angsuran_ke']}\nTagihan {rupiah(b['jumlah_tagihan'])} + "
                   f"denda {rupiah(b['denda_hari_ini'])}\nTotal diterima: {rupiah(total)}")

        def selesai():
            self.refresh()

        FormDialog(self, "Terima Pembayaran", [
            {"kind": "info", "value": ringkas},
            {"key": "ket", "label": "Keterangan (opsional):"},
        ], lambda d: self.ctrl.bayar(id_pinjaman, d['ket']), selesai, tombol="Konfirmasi Pembayaran")
