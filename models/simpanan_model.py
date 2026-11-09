from config.database import fetch_all, execute

class SimpananModel:
    # Menyimpan transaksi baru ke db
    @staticmethod
    def tambah(id_anggota, id_petugas, jenis, tanggal, jumlah, keterangan):
        return execute("""
            INSERT INTO simpanan (id_anggota, id_petugas, jenis_simpanan, tanggal_simpanan, saldo, keterangan)
            VALUES (%s,%s,%s,%s,%s,%s)""", (id_anggota, id_petugas, jenis, tanggal, jumlah, keterangan))

    # Menampilkan riwayat simpanan
    @staticmethod
    def riwayat(id_anggota=None, keyword=""):
        like = f"%{keyword}%" # Format pencarian LIKE
        return fetch_all("""
            SELECT s.id_simpanan, s.tanggal_simpanan, a.nama_anggota, s.jenis_simpanan,
                   s.saldo, s.keterangan, pt.nama_pengguna AS petugas
            FROM simpanan s
            JOIN anggota a ON a.id_anggota = s.id_anggota       
            JOIN pengguna pt ON pt.id_pengguna = s.id_petugas   
            WHERE (%s IS NULL OR s.id_anggota = %s)             
            AND (%s = '' OR a.nama_anggota LIKE %s OR s.jenis_simpanan LIKE %s) 
            ORDER BY s.tanggal_simpanan DESC, s.id_simpanan DESC""", 
            (id_anggota, id_anggota, keyword, like, like))

    # Catatan:
    # Join anggota a = mengambil nama anggota
    # Join pengguna pt = mengambil nama pengguna
    # WHERE IS NULL = Kalau id_anggota kosong, tampilkan semua (role: admin)