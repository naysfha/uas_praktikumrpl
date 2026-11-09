import hashlib
from config.database import Database

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