from config.database import fetch_all, fetch_one, execute, transaksi
class AnggotaModel:
    
    # Fetch_all : Mengambil semua baris data dari database dan mengubahnya menjadi daftar (list)
    @staticmethod
    def semua(keyword=""):
        like = f"%{keyword}%" # Format pencarian LIKE
        return fetch_all("""
            SELECT a.id_anggota, a.nik, a.nama_anggota, a.no_hp, a.alamat, p.username
            FROM anggota a JOIN pengguna p ON p.id_pengguna = a.id_pengguna
            WHERE %s = '' OR a.nama_anggota LIKE %s OR a.nik LIKE %s OR p.username LIKE %s
            ORDER BY a.id_anggota""", (keyword, like, like, like))
    
    # Fetch_one : Mengambil hanya satu baris
    @staticmethod
    def by_id(id_anggota):
        return fetch_one("SELECT * FROM anggota WHERE id_anggota=%s", (id_anggota,))

    @staticmethod
    def by_pengguna(id_pengguna):
        return fetch_one("SELECT * FROM anggota WHERE id_pengguna=%s", (id_pengguna,))

    # Akun role Anggota yang belum punya data anggota.
    @staticmethod
    def pengguna_belum_terdaftar():
        return fetch_all("""
            SELECT p.id_pengguna, p.username, p.nama_pengguna FROM pengguna p
            LEFT JOIN anggota a ON a.id_pengguna = p.id_pengguna
            WHERE p.role = 'Anggota' AND a.id_anggota IS NULL
            ORDER BY p.id_pengguna""")

    # Menambahkan data Anggota 
    @staticmethod
    def tambah(id_pengguna, nik, nama, no_hp, alamat, id_petugas=None):
        return execute("""
            INSERT INTO anggota (id_petugas, id_pengguna, nik, nama_anggota, alamat, no_hp)
            VALUES (%s,%s,%s,%s,%s,%s)""", (id_petugas, id_pengguna, nik, nama, alamat, no_hp))

    # Mengubah data Anggota
    @staticmethod
    def ubah(id_anggota, nik, nama, no_hp, alamat):
        execute("""UPDATE anggota SET nik=%s, nama_anggota=%s, no_hp=%s, alamat=%s
                   WHERE id_anggota=%s""", (nik, nama, no_hp, alamat, id_anggota))

    # Menghapus data Anggota 
    @staticmethod
    def hapus(id_anggota):
        execute("DELETE FROM anggota WHERE id_anggota=%s", (id_anggota,))

    # Anggota mengisi / memperbarui data dirinya sendiri.
    @staticmethod
    def simpan_profil(id_pengguna, nik, nama, no_hp, alamat):
        with transaksi() as cur:
            # Cek apakah profil sudah ada
            cur.execute("SELECT id_anggota FROM anggota WHERE id_pengguna=%s", (id_pengguna,))
            ada = cur.fetchone()
            if ada:
                # Jika ada, update
                cur.execute("""UPDATE anggota SET nik=%s, nama_anggota=%s, no_hp=%s, alamat=%s
                               WHERE id_pengguna=%s""", (nik, nama, no_hp, alamat, id_pengguna))
            else:
                # Jika tidak, menambahkan 
                cur.execute("""INSERT INTO anggota (id_pengguna, nik, nama_anggota, alamat, no_hp)
                               VALUES (%s,%s,%s,%s,%s)""", (id_pengguna, nik, nama, alamat, no_hp))
