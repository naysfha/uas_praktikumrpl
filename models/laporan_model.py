from config.database import fetch_all, fetch_one

# Ambil 1 angka dari database (COUNT/SUM). Kalau kosong, kembalikan 0.
def _val(sql, params=()):
    row = fetch_one(sql, params)
    return list(row.values())[0] if row else 0

# Query untuk menghitung berapa BANYAK anggota yang telat bayar
_TELAT = """SELECT COUNT(DISTINCT pg.id_anggota) FROM jadwal_angsuran j
            JOIN pinjaman pj ON pj.id_pinjaman = j.id_pinjaman
            JOIN pengajuan_pinjaman pg ON pg.id_pengajuan = pj.id_pengajuan
            WHERE j.status_jadwal <> 'lunas' AND j.tanggal_jatuh_tempo < CURDATE()"""


class LaporanModel:
    # Data statistik untuk halaman Dashboard Admin
    @staticmethod
    def stat_admin():
        return {
            "anggota": _val("SELECT COUNT(*) FROM anggota"),
            "simpanan": _val("SELECT COALESCE(SUM(saldo),0) FROM simpanan"),
            "pinjaman": _val("SELECT COALESCE(SUM(sisa_pinjaman),0) FROM pinjaman WHERE status_pinjaman <> 'lunas'"),
            "telat": _val(_TELAT),
        }

    # Data statistik untuk halaman Dashboard Petugas
    @staticmethod
    def stat_petugas():
        return {
            "anggota": _val("SELECT COUNT(*) FROM anggota"),
            "simpanan_bulan": _val("""SELECT COALESCE(SUM(saldo),0) FROM simpanan
                WHERE YEAR(tanggal_simpanan)=YEAR(CURDATE()) AND MONTH(tanggal_simpanan)=MONTH(CURDATE())"""),
            "menunggu": _val("SELECT COUNT(*) FROM pengajuan_pinjaman WHERE status_pengajuan='menunggu'"),
            "angsuran_hari": _val("SELECT COUNT(*) FROM angsuran WHERE tanggal_bayar = CURDATE()"),
        }

    # Data statistik untuk halaman Dashboard Anggota (melihat datanya sendiri)
    @staticmethod
    def stat_anggota(id_anggota):
        # Cari pinjaman aktif milik anggota ini
        pj = fetch_one("""
            SELECT pj.* FROM pinjaman pj
            JOIN pengajuan_pinjaman pg ON pg.id_pengajuan = pj.id_pengajuan
            WHERE pg.id_anggota=%s AND pj.status_pinjaman <> 'lunas'
            ORDER BY pj.id_pinjaman DESC LIMIT 1""", (id_anggota,))
        
        # Siapkan data default (0/kosong)
        hasil = {
            "simpanan": _val("SELECT COALESCE(SUM(saldo),0) FROM simpanan WHERE id_anggota=%s", (id_anggota,)),
            "sisa": 0, "tagihan": None, "jatuh_tempo": None, "terbayar": None, "jangka": None,
        }
        
        # Jika punya pinjaman aktif, isi detail cicilannya
        if pj:
            hasil["sisa"] = pj["sisa_pinjaman"]
            hasil["jangka"] = pj["jangka_waktu"]
            hasil["terbayar"] = _val("""SELECT COUNT(*) FROM jadwal_angsuran
                                        WHERE id_pinjaman=%s AND status_jadwal='lunas'""", (pj["id_pinjaman"],))  # Sudah bayar berapa kali
            
            j = fetch_one("""SELECT jumlah_tagihan, tanggal_jatuh_tempo FROM jadwal_angsuran
                             WHERE id_pinjaman=%s AND status_jadwal <> 'lunas'
                             ORDER BY angsuran_ke LIMIT 1""", (pj["id_pinjaman"],)) # Tagihan terdekat
            
            if j:
                hasil["tagihan"], hasil["jatuh_tempo"] = j["jumlah_tagihan"], j["tanggal_jatuh_tempo"]
        return hasil

    # Laporan total keseluruhan koperasi (untuk admin)
    @staticmethod
    def ringkasan():
        return {
            "anggota": _val("SELECT COUNT(*) FROM anggota"),
            "simpanan_pokok": _val("SELECT COALESCE(SUM(saldo),0) FROM simpanan WHERE jenis_simpanan='Pokok'"),
            "simpanan_wajib": _val("SELECT COALESCE(SUM(saldo),0) FROM simpanan WHERE jenis_simpanan='Wajib'"),
            "simpanan_sukarela": _val("SELECT COALESCE(SUM(saldo),0) FROM simpanan WHERE jenis_simpanan='Sukarela'"),
            "simpanan": _val("SELECT COALESCE(SUM(saldo),0) FROM simpanan"),            # Total semua simpanan
            "pencairan": _val("SELECT COALESCE(SUM(jumlah_pinjaman),0) FROM pinjaman"), # Total uang dipinjamkan
            "sisa": _val("SELECT COALESCE(SUM(sisa_pinjaman),0) FROM pinjaman WHERE status_pinjaman <> 'lunas'"),
            "angsuran": _val("SELECT COALESCE(SUM(jumlah_bayar),0) FROM angsuran"),     # Total uang cicilan masuk
            "denda": _val("SELECT COALESCE(SUM(denda),0) FROM angsuran"),               # Total uang denda masuk
        }

    # Laporan rincian simpanan dan pinjaman per anggota
    @staticmethod
    def per_anggota():
        return fetch_all("""
            SELECT a.id_anggota, a.nama_anggota,
              COALESCE((SELECT SUM(s.saldo) FROM simpanan s WHERE s.id_anggota = a.id_anggota), 0) AS total_simpanan,
              COALESCE((SELECT SUM(pj.sisa_pinjaman) FROM pinjaman pj
                        JOIN pengajuan_pinjaman pg ON pg.id_pengajuan = pj.id_pengajuan
                        WHERE pg.id_anggota = a.id_anggota AND pj.status_pinjaman <> 'lunas'), 0) AS sisa_pinjaman
            FROM anggota a ORDER BY a.nama_anggota""")
