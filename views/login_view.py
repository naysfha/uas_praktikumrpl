import customtkinter as ctk
import tkinter.messagebox as messagebox

class LoginView(ctk.CTkFrame):
    def __init__(self, master, controller, switch_to_register_callback):
        super().__init__(master)
        self.controller = controller
        self.switch_to_register_callback = switch_to_register_callback

        # Konfigurasi Grid Utama
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Container Frame di Tengah
        self.form_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.form_frame.grid(row=0, column=0, padx=20, pady=20)

        # Judul / Header
        self.lbl_title = ctk.CTkLabel(
            self.form_frame, 
            text="Sistem Manajemen Koperasi", 
            font=ctk.CTkFont(family="Helvetica", size=24, weight="bold")
        )
        self.lbl_title.pack(pady=(0, 5))

        self.lbl_subtitle = ctk.CTkLabel(
            self.form_frame, 
            text="Silakan masuk ke akun Anda", 
            text_color="gray",
            font=ctk.CTkFont(family="Helvetica", size=14)
        )
        self.lbl_subtitle.pack(pady=(0, 25))

        # Input Username
        self.entry_username = ctk.CTkEntry(
            self.form_frame, 
            placeholder_text="Username", 
            width=300, 
            height=40
        )
        self.entry_username.pack(pady=10)

        # Input Password
        self.entry_password = ctk.CTkEntry(
            self.form_frame, 
            placeholder_text="Password", 
            show="*", 
            width=300, 
            height=40
        )
        self.entry_password.pack(pady=10)

        # Tombol Login
        self.btn_login = ctk.CTkButton(
            self.form_frame, 
            text="Masuk", 
            width=300, 
            height=40,
            command=self.handle_login,
            font=ctk.CTkFont(weight="bold")
        )
        self.btn_login.pack(pady=(20, 10))

        # Tombol Pindah ke Register
        self.btn_to_register = ctk.CTkButton(
            self.form_frame, 
            text="Belum punya akun? Daftar di sini", 
            fg_color="transparent", 
            text_color=["#1f6aa5", "#3b8ed0"],
            hover=False,
            command=self.switch_to_register_callback
        )
        self.btn_to_register.pack(pady=5)

    def handle_login(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()

        # Panggil fungsi proses_login dari AuthController
        err_msg, user = self.controller.proses_login(username, password)
        
        if err_msg:
            messagebox.showerror("Gagal Login", err_msg)
        else:
            # Login sukses, controller akan menghandle perpindahan window/dashboard
            pass