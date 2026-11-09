from config.settings import BUNGA_TAHUNAN_DEFAULT
from models.anggota_model import AnggotaModel
from models.pinjaman_model import PinjamanModel
from models.simpanan_model import SimpananModel
from utils.helpers import aksi, baca, parse_nominal, rupiah


class PinjamanController:
    # Menyimpan data user yang sedang login
    def __init__(self, user): 
        self.user = user

    
    # Mengambil data anggota berdasarkan user yang login
    def _anggota(self):
        return AnggotaModel.by_pengguna(self.user['id_pengguna'])

    # ---------- Role Anggota ----------
    # Mengambil profil anggota yang sedang login
    @baca(lambda: None)
    def profil(self):
        return self._anggota()

    # Mengambil daftar pengajuan milik anggota yang login
    @baca(list)
    def pengajuan_saya(self):
        a = self._anggota()
        return PinjamanModel.pengajuan_list(id_anggota=a['id_anggota']) if a else []

    # Memproses pengajuan pinjaman baru dari anggota
    @aksi
    def ajukan(self, jumlah, jangka, tujuan):
        a = self._anggota()
        if not a:
            return False, "Lengkapi Data Diri terlebih dahulu sebelum mengajukan pinjaman."
        nominal = parse_nominal(jumlah)
        if nominal is None:
            return False, "Jumlah pinjaman harus berupa angka lebih dari 0."
        if not tujuan.strip():
            return False, "Tujuan pinjaman wajib diisi."
        PinjamanModel.ajukan(a['id_anggota'], nominal, int(jangka), tujuan.strip())
        return True, "Pengajuan berhasil dikirim, menunggu persetujuan Petugas."

    # Menghitung estimasi angsuran (simulasi sebelum pengajuan)
    @staticmethod
    def estimasi(jumlah, jangka):
        nominal = parse_nominal(jumlah)
        if nominal is None:
            return "Estimasi angsuran: -"
        
        # Hitung total pinjaman + bunga
        total = PinjamanModel.hitung_total(nominal, BUNGA_TAHUNAN_DEFAULT, int(jangka))
        return (f"Estimasi (bunga {BUNGA_TAHUNAN_DEFAULT:g}%/tahun flat): "
                f"{rupiah(total / int(jangka))} x {jangka} bulan = {rupiah(total)}")

    # ---------- Role Petugas ----------
    @baca(list)
    # Melihat semua pengajuan dari semua anggota 
    def pengajuan_semua(self, status=None):
        return PinjamanModel.pengajuan_list(status=status)

    @aksi
    # Menyetujui atau menolak pengajuan pinjama
    def proses(self, id_pengajuan, setuju, catatan, bunga=None):
        if self.user['role'] != 'Petugas':
            return False, "Hanya Petugas yang dapat memproses pengajuan."
        
        nilai_bunga = BUNGA_TAHUNAN_DEFAULT
        
        if setuju:
            # Jika disetujui, pastikan input bunga berupa angka
            try:
                nilai_bunga = float(str(bunga).replace(",", "."))
            except ValueError:
                return False, "Bunga harus berupa angka."
            if not 0 <= nilai_bunga <= 100:
                return False, "Bunga harus antara 0 dan 100."
        else:
            # Jika ditolak, catatan/alasan wajib diisi
            if not catatan.strip():
            
                return False, "Isi catatan alasan penolakan."
        PinjamanModel.proses_pengajuan(id_pengajuan, self.user['id_pengguna'], setuju,
                                       catatan.strip() or None, nilai_bunga)
        
        return True, "Pengajuan disetujui, pinjaman & jadwal angsuran dibuat." if setuju else "Pengajuan ditolak."

    @baca(list)
    # Mengambil daftar pinjaman yang sedang berjalan
    def pinjaman(self, status=None, aktif_saja=False):
        PinjamanModel.refresh_keterlambatan()
        return PinjamanModel.pinjaman_list(status=status, aktif_saja=aktif_saja)

    @baca(list)
    # Melihat jadwal angsuran berdasarkan ID Pinjaman
    def jadwal(self, id_pinjaman):
        PinjamanModel.refresh_keterlambatan()
        return PinjamanModel.jadwal(id_pinjaman)

    @baca(lambda: None)
    # Melihat tagihan angsuran yang harus dibayar berikutnya
    def angsuran_berikut(self, id_pinjaman):
        return PinjamanModel.angsuran_berikut(id_pinjaman)

    @aksi
    # Role Anggota: Memproses pembayaran angsuran 
    def bayar(self, id_pinjaman, keterangan):
        if self.user['role'] != 'Petugas':
            return False, "Hanya Petugas yang dapat menerima pembayaran angsuran."
        
        ke, tagihan, denda, lunas = PinjamanModel.bayar_angsuran(
            id_pinjaman, self.user['id_pengguna'], keterangan.strip() or None)
        
        # Struk pembayaran
        pesan = f"Angsuran ke-{ke} diterima: {rupiah(tagihan)}"
        if denda > 0:
            pesan += f" + denda {rupiah(denda)}"
        if lunas:
            pesan += "\nPinjaman sudah LUNAS."
        return True, pesan

    # ---------- Role Admin ----------
    @aksi
    # Mengubah status pinjaman secara manual
    def ubah_status(self, id_pinjaman, status):
        if self.user['role'] != 'Admin':
            return False, "Hanya Admin yang dapat mengubah status pinjaman."
        PinjamanModel.ubah_status(id_pinjaman, status)
        return True, f"Status pinjaman diubah menjadi '{status}'."

    # ---------- Role Petugas: riwayat anggota ----------
    @baca(list)
    # Mengambil semua data anggota 
    def daftar_anggota(self):
        return AnggotaModel.semua()

    @baca(list)
    # Melihat riwayat simpanan anggota tertentu berdasarkan ID Anggota
    def riwayat_simpanan(self, id_anggota):
        return SimpananModel.riwayat(id_anggota=id_anggota)

    @baca(list)
    # Melihat riwayat pinjaman anggota tertentu berdasarkan ID Anggota
    def riwayat_pinjaman(self, id_anggota):
        return PinjamanModel.pinjaman_list(id_anggota=id_anggota)

    @baca(list)
    # Melihat riwayat pembayaran angsuran anggota tertentu berdasarkan ID Anggota
    def riwayat_angsuran(self, id_anggota):
        return PinjamanModel.angsuran_riwayat(id_anggota=id_anggota)
