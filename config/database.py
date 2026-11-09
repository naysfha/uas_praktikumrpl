import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager

class Database:
    @staticmethod
    def get_connection():
        try:
            connection = mysql.connector.connect(
                host='localhost',
                database='koperasi',
                user='root',
                password=''
            )
            if connection.is_connected():
                return connection
        except Error as e:
            print(f"Gagal terhubung ke database: {e}")
            return None

def get_connection():
    return Database.get_connection()

def _koneksi():
    conn = get_connection()
    if conn is None:
        raise ConnectionError("Tidak dapat terhubung ke database. Pastikan MySQL aktif.")
    return conn

# Ambil BANYAK baris data (SELECT). Mengembalikan list of dict.
def fetch_all(sql, params=()):
    conn = _koneksi()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        return cur.fetchall()
    finally:
        conn.close()

# Ambil SATU baris data (SELECT). Mengembalikan dict atau None.
def fetch_one(sql, params=()):
    conn = _koneksi()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        return cur.fetchone()
    finally:
        conn.close()

# Menjalankan perintah yang mengubah data.
def execute(sql, params=()):
    conn = _koneksi()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()
        
# Menjalankan beberapa perintah dalam satu transaksi (commit otomatis, rollback jika error).
@contextmanager
def transaksi():
    conn = _koneksi()
    try:
        cur = conn.cursor(dictionary=True)
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    conn = Database.get_connection()
    if conn and conn.is_connected():
        print("Koneksi ke database berhasil dan aktif!")
        conn.close()
