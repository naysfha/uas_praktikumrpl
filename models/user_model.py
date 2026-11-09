import hashlib
from config.database import Database
from config.database import Database, fetch_all, fetch_one, execute
from utils.helpers import AturanBisnis

class UserModel:
    def __init__(self):
        self.db = Database()
        self.conn = self.db.get_connection()
        self.table_name = "pengguna"

    @staticmethod
    def hash_password(password):
    # Mengubah plain text password menjadi hash SHA-256
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
        
    def autentikasi(self, username, password):
        if self.conn:
            cursor = self.conn.cursor(dictionary=True)
            password_hash = self.hash_password(password)

            # Parameterized Query untuk mencegah SQL Injection
            query = f"SELECT id_pengguna, username, nama_pengguna, role FROM {self.table_name} WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password_hash))
            user = cursor.fetchone()
            cursor.close()
            return user
        return None
    
    # Menambahkan register
    def register_user(self, username, password, nama_pengguna, role):
        if self.conn:
            cursor = self.conn.cursor()
            password_hash = self.hash_password(password)

            # Parameterized Query untuk mencegah SQL Injection
            query = f"INSERT INTO {self.table_name} (username, password, nama_pengguna, role) VALUES (%s, %s, %s, %s)"
            
            # Excaption Handling
            try:
                cursor.execute(query, (username, password_hash, nama_pengguna, role))
                self.conn.commit()
                return True
            except Exception as e:
                print(f"Error: {e}")
                self.conn.rollback()
                return False
            finally:
                cursor.close()
        return False
    
    def semua(keyword=""):
        like = f"%{keyword}%"
        return fetch_all("""
            SELECT id_pengguna, username, nama_pengguna, role
            FROM pengguna
            WHERE %s = '' OR username LIKE %s OR nama_pengguna LIKE %s OR role LIKE %s
            ORDER BY id_pengguna""", (keyword, like, like, like))

    def by_id(id_pengguna):
        return fetch_one("SELECT id_pengguna, username, nama_pengguna, role "
                         "FROM pengguna WHERE id_pengguna=%s", (id_pengguna,))

    def tambah(username, password, nama, role):
        return execute("INSERT INTO pengguna (username, password, nama_pengguna, role) "
                       "VALUES (%s,%s,%s,%s)",
                       (username, UserModel.hash_password(password), nama, role))

    def ubah(id_pengguna, username, nama, role):
        return execute("UPDATE pengguna SET username=%s, nama_pengguna=%s, role=%s "
                       "WHERE id_pengguna=%s", (username, nama, role, id_pengguna))

    def reset_password(id_pengguna, password_baru):
        return execute("UPDATE pengguna SET password=%s WHERE id_pengguna=%s",
                       (UserModel.hash_password(password_baru), id_pengguna))

    def hapus(id_pengguna):
        return execute("DELETE FROM pengguna WHERE id_pengguna=%s", (id_pengguna,))

    def ganti_password(id_pengguna, lama, baru):
        row = fetch_one("SELECT password FROM pengguna WHERE id_pengguna=%s", (id_pengguna,))
        if not row or row['password'] != UserModel.hash_password(lama):
            raise AturanBisnis("Password lama salah.")
        return UserModel.reset_password(id_pengguna, baru)