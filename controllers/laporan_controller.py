import csv
from models.anggota_model import AnggotaModel
from models.laporan_model import LaporanModel
from models.pinjaman_model import PinjamanModel
from utils.helpers import baca, rupiah, tgl

# Kode warna untuk kartu statistik di Dashboard
HIJAU, MERAH, KUNING, UNGU, BIRU = "#16a34a", "#dc2626", "#d97706", "#4f46e5", "#0284c7"

class LaporanController:
    def __init__(self, user):
        # Menyimpan data user yang sedang login
        self.user = user

    @baca(list)
    def kartu_dashboard(self):
        
        # Perbarui status telat dulu sebelum menampilkan data
        PinjamanModel.refresh_keterlambatan()
        
        # Role Admin
        role = self.user['role']
        if role == 'Admin':
            s = LaporanModel.stat_admin()
            return [("Total Anggota", f"{s['anggota']} Orang", UNGU),
                    ("Total Simpanan", rupiah(s['simpanan']), HIJAU),
                    ("Pinjaman Berjalan", rupiah(s['pinjaman']), MERAH),
                    ("Angsuran Terlambat", f"{s['telat']} Anggota", KUNING)]
        
        # Role Petugas
        if role == 'Petugas':
            s = LaporanModel.stat_petugas()
            return [("Total Anggota", f"{s['anggota']} Orang", UNGU),
                    ("Simpanan Bulan Ini", rupiah(s['simpanan_bulan']), HIJAU),
                    ("Pengajuan Menunggu", f"{s['menunggu']} Pending", KUNING),
                    ("Angsuran Hari Ini", f"{s['angsuran_hari']} Pembayaran", BIRU)]
        
        # Role Anggota
        a = AnggotaModel.by_pengguna(self.user['id_pengguna'])
        
        # Kalau belum isi data diri
        if not a:
            return [("Data Diri", "Belum dilengkapi", KUNING)]
        s = LaporanModel.stat_anggota(a['id_anggota'])
        terbayar = f"{s['terbayar']} / {s['jangka']} Bulan" if s['jangka'] else "-"
        
        # Mengembalikan card setelah isi data diri
        return [("Total Simpanan", rupiah(s['simpanan']), HIJAU),
                ("Sisa Pinjaman", rupiah(s['sisa']), MERAH),
                ("Angsuran Berikutnya", rupiah(s['tagihan']) if s['tagihan'] else "-", KUNING),
                ("Jatuh Tempo", tgl(s['jatuh_tempo']), UNGU),
                ("Angsuran Terbayarkan", terbayar, BIRU)]

    @baca(dict)
    # Mengambil ringkasan total koperasi untuk halaman laporan
    def ringkasan(self):
        return LaporanModel.ringkasan()

    @baca(list)
    # Mengambil data rincian simpanan & pinjaman per anggota
    def per_anggota(self):
        return LaporanModel.per_anggota()

    # Mengekspor laporan ke file CSV
    def ekspor_csv(self, path):
        r, rows = self.ringkasan(), self.per_anggota()
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["LAPORAN KOPERASI"])
            for label, kunci in [("Total Anggota", "anggota"), ("Simpanan Pokok", "simpanan_pokok"),
                                 ("Simpanan Wajib", "simpanan_wajib"), ("Simpanan Sukarela", "simpanan_sukarela"),
                                 ("Total Simpanan", "simpanan"), ("Total Pencairan Pinjaman", "pencairan"),
                                 ("Sisa Pinjaman", "sisa"), ("Angsuran Diterima", "angsuran"),
                                 ("Denda Terkumpul", "denda")]:
                w.writerow([label, r.get(kunci, 0)])
            w.writerow([])
            w.writerow(["ID", "Nama Anggota", "Total Simpanan", "Sisa Pinjaman"])
            for x in rows:
                w.writerow([x['id_anggota'], x['nama_anggota'], x['total_simpanan'], x['sisa_pinjaman']])
