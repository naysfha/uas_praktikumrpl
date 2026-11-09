import tkinter.messagebox as messagebox
import customtkinter as ctk
from models.user_model import UserModel
from views.login_view import LoginView
from views.register_view import RegisterView
from controllers.dashboard_controller import DashboardController

class AuthController:
    # Setup jendela utama aplikasi 
    def __init__(self):
        self.root = ctk.CTk()
        self.root.geometry("800x500")
        self.root.title("Sistem Manajemen Koperasi")
        self.root.resizable(False, False)

        self.user_model = UserModel()   # buat sekali, dipakai ulang

        # Mulai dengan menampilkan halaman Login
        self.tampilkan_login()

    def tampilkan_login(self):
        # Menampilkan halaman Login ke dalam window utama
        self._bersihkan_window()
        self.view = LoginView(
            master=self.root, 
            controller=self, 
            switch_to_register_callback=self.tampilkan_register
        )
        self.view.pack(fill="both", expand=True)

    def tampilkan_register(self):
        # Menampilkan halaman Register
        self._bersihkan_window()
        self.view = RegisterView(
            master=self.root, 
            controller=self, 
            switch_to_login_callback=self.tampilkan_login
        )
        self.view.pack(fill="both", expand=True)

    def _bersihkan_window(self):
        # Menghapus widget sebelumnya
        for widget in self.root.winfo_children():
            widget.destroy()

    def proses_login(self, username, password):
        if not username or not password:
            return "Username dan password wajib diisi!", None

        user = self.user_model.autentikasi(username, password)
        if user:
            messagebox.showinfo("Login Berhasil", f"Selamat datang, {user['nama_pengguna']} ({user['role']})!")
            self.root.withdraw()   # sembunyikan window login, jangan destroy

            app_dashboard = DashboardController(user_data=user)
            app_dashboard.run()
            return None, user
        else:
            return "Username atau password salah!", None
            
    def register(self, username, password, nama_pengguna):
        # Role otomatis diset menjadi "Anggota" untuk setiap pendaftaran baru
        role = "Anggota"
        sukses = self.user_model.register_user(username, password, nama_pengguna, role)
        if sukses:
            return "Registrasi berhasil! Silakan login.", True
        else:
            return "Username sudah terpakai, silakan gunakan yang lain.", False

    def run(self):
        self.root.mainloop()