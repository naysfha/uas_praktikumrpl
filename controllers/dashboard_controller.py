import customtkinter as ctk
from views.dashboard import DashboardView

class DashboardController:
    def __init__(self, user_data):
        # Menyimpan data user yang berhasil login
        self.user_data = user_data  
        
        # Setup jendela utama dashboard
        self.root = ctk.CTk()
        self.root.geometry("1200x700")
        self.root.title(f"Aplikasi Koperasi Simpan Pinjam - Dashboard ({self.user_data.get('role')})")
        self.root.minsize(1050, 600)

        # Tampilan isi Dashboard
        self.view = DashboardView(master=self.root, controller=self, user_data=self.user_data)
        self.view.pack(fill="both", expand=True)

    def logout(self):
        # Menutup dashboard dan kembali ke halaman Login
        self.root.destroy()
        from controllers.auth_controller import AuthController
        
        # Kembali ke halaman login
        app_auth = AuthController()
        app_auth.run()

    def run(self):
        self.root.mainloop()