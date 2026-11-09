import customtkinter as ctk
import tkinter.messagebox as messagebox

class RegisterView(ctk.CTkFrame):
    def __init__(self, master, controller, switch_to_login_callback):
        super().__init__(master)
        self.controller = controller
        self.switch_to_login_callback = switch_to_login_callback

        # Konfigurasi Grid Utama
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Container Frame di Tengah
        self.form_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.form_frame.grid(row=0, column=0, padx=20, pady=20)

        # Judul / Header
        self.lbl_title = ctk.CTkLabel(
            self.form_frame, 
            text="Pendaftaran Anggota Baru", 
            font=ctk.CTkFont(family="Helvetica", size=24, weight="bold")
        )
        self.lbl_title.pack(pady=(0, 5))

        self.lbl_subtitle = ctk.CTkLabel(
            self.form_frame, 
            text="Lengkapi data untuk mendaftar ke Koperasi", 
            text_color="gray",
            font=ctk.CTkFont(family="Helvetica", size=14)
        )
        self.lbl_subtitle.pack(pady=(0, 20))

        # Input Nama Lengkap (nama_pengguna)
        self.entry_nama = ctk.CTkEntry(
            self.form_frame, 
            placeholder_text="Nama Lengkap", 
            width=300, 
            height=38
        )
        self.entry_nama.pack(pady=8)

        # Input Username
        self.entry_username = ctk.CTkEntry(
            self.form_frame, 
            placeholder_text="Username", 
            width=300, 
            height=38
        )
        self.entry_username.pack(pady=8)

        # Input Password
        self.entry_password = ctk.CTkEntry(
            self.form_frame, 
            placeholder_text="Password", 
            show="*", 
            width=300, 
            height=38
        )
        self.entry_password.pack(pady=8)

        # Tombol Daftar (Role otomatis Anggota, tidak perlu option menu)
        self.btn_register = ctk.CTkButton(
            self.form_frame, 
            text="Daftar Sekarang", 
            width=300, 
            height=40,
            command=self.handle_register,
            font=ctk.CTkFont(weight="bold")
        )
        self.btn_register.pack(pady=(20, 10))

        # Tombol Kembali ke Login
        self.btn_to_login = ctk.CTkButton(
            self.form_frame, 
            text="Sudah punya akun? Masuk di sini", 
            fg_color="transparent", 
            text_color=["#1f6aa5", "#3b8ed0"],
            hover=False,
            command=self.switch_to_login_callback
        )
        self.btn_to_login.pack(pady=2)

    def handle_register(self):
        nama = self.entry_nama.get().strip()
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()

        if not nama or not username or not password:
            messagebox.showerror("Peringatan", "Semua kolom wajib diisi!")
            return

        # Panggil fungsi register dari AuthController (tanpa parameter role karena otomatis "Anggota")
        pesan, sukses = self.controller.register(username, password, nama)

        if sukses:
            messagebox.showinfo("Sukses", pesan)
            self.switch_to_login_callback()
        else:
            messagebox.showerror("Gagal", pesan)