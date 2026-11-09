import customtkinter as ctk

from controllers.laporan_controller import LaporanController
from views.anggota_view import AnggotaView
from views.angsuran_view import AngsuranView
from views.components import BG, TEXT, MUTED, CARD_BG
from views.laporan_view import LaporanView
from views.pengajuan_view import PengajuanAnggotaView, PengajuanPetugasView
from views.pengguna_view import PenggunaView
from views.pinjaman_admin_view import PinjamanAdminView
from views.profil_view import ProfilView
from views.riwayat_view import RiwayatView
from views.simpanan_view import SimpananView

# Warna khusus untuk sidebar
SIDEBAR = "#1f1f2e"
ACCENT = "#4f46e5"

class DashboardView(ctk.CTkFrame):
    def __init__(self, master, controller, user_data):
        super().__init__(master, fg_color=BG, corner_radius=0)
        self.controller = controller
        self.user_data = user_data  # Berisi info role, nama_pengguna, dll.
        self.laporan = LaporanController(user_data)

        # Setup layout grid: kolom 0 (sidebar), kolom 1 (konten utama)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._buat_sidebar()
        self._buat_area_konten()

    def _menu_role(self):
        role = self.user_data.get('role', 'Anggota')
        buka = lambda kelas: (lambda: self.tampilkan(kelas))
        
        # Menu khusus Petugas
        if role == 'Petugas':
            return [
                ("Dashboard", self.tampilkan_dashboard),
                ("Data Anggota", buka(AnggotaView)),
                ("Transaksi Simpanan", buka(SimpananView)),
                ("Pengajuan Pinjaman", buka(PengajuanPetugasView)),
                ("Pembayaran Angsuran", buka(AngsuranView)),
                ("Riwayat Anggota", buka(RiwayatView)),
            ]
            
        # Menu khusus Anggota
        if role == 'Anggota':
            return [
                ("Dashboard", self.tampilkan_dashboard),
                ("Pengajuan Peminjaman", buka(PengajuanAnggotaView)),
                ("Data Diri / Profil", buka(ProfilView)),
            ]
            
        # Menu khusus Admin 
        return [
            ("Dashboard", self.tampilkan_dashboard),
            ("Kelola Anggota", buka(AnggotaView)),
            ("Kelola Pinjaman", buka(PinjamanAdminView)),
            ("Manajemen Pengguna", buka(PenggunaView)),
            ("Laporan Koperasi", buka(LaporanView)),
        ]
        
    # Frame sidebar di sebelah kiri
    def _buat_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=260, fg_color=SIDEBAR, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        # Judul & Info User di sidebar
        ctk.CTkLabel(sidebar, text="Koperasi Simpan", text_color="white",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(25, 5), padx=20, anchor="w")
        ctk.CTkLabel(sidebar, text="Sistem Manajemen Koperasi", text_color="#a5a7b8",
                     font=ctk.CTkFont(size=11)).pack(padx=20, anchor="w")
        ctk.CTkLabel(sidebar, text=f"{self.user_data.get('nama_pengguna')} ({self.user_data.get('role')})",
                     text_color="#a5a7b8", font=ctk.CTkFont(size=11)).pack(padx=20, pady=(10, 0), anchor="w")

        ctk.CTkLabel(sidebar, text="MENU UTAMA", text_color="#6b6d80",
                     font=ctk.CTkFont(size=10, weight="bold")).pack(pady=(20, 5), padx=20, anchor="w")

        for teks, perintah in self._menu_role():
            ctk.CTkButton(sidebar, text=teks, fg_color="transparent", text_color="white",
                          anchor="w", hover_color="#2d2d44", height=38,
                          font=ctk.CTkFont(size=13), command=perintah).pack(fill="x", padx=12, pady=2)
        
        # Tombol Logout di paling bawah
        ctk.CTkButton(sidebar, text="Keluar", fg_color="#dc2626", hover_color="#b91c1c",
                      text_color="white", anchor="center", height=36,
                      command=self.controller.logout).pack(side="bottom", padx=20, pady=25, fill="x")

    # Frame utama di sebelah kanan 
    def _buat_area_konten(self):
        self.konten_utama = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self.konten_utama.grid(row=0, column=1, sticky="nsew", padx=30, pady=25)
        self.tampilkan_dashboard()

    def bersihkan_konten(self):
        for widget in self.konten_utama.winfo_children():
            widget.destroy()

    def tampilkan(self, kelas_halaman):
        """Menampilkan halaman (frame) modul ke area konten."""
        self.bersihkan_konten()
        kelas_halaman(self.konten_utama, self.user_data).pack(fill="both", expand=True)

    def tampilkan_dashboard(self):
        self.bersihkan_konten()
        ctk.CTkLabel(self.konten_utama, text="Dashboard", text_color=TEXT,
                     font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(self.konten_utama, text=f"Selamat datang, {self.user_data.get('nama_pengguna')}",
                     text_color=MUTED, font=ctk.CTkFont(size=12)).pack(anchor="w")

        grid_card = ctk.CTkFrame(self.konten_utama, fg_color="transparent")
        grid_card.pack(fill="x", pady=10)

        for i, (judul, nilai, warna_aksen) in enumerate(self.laporan.kartu_dashboard()):
            card = ctk.CTkFrame(grid_card, width=240, height=110, fg_color=CARD_BG,
                                corner_radius=10, border_width=1, border_color="#e5e7eb")
            card.grid(row=i // 3, column=i % 3, padx=8, pady=8, sticky="nsew")
            card.pack_propagate(False)
            ctk.CTkFrame(card, height=4, fg_color=warna_aksen, corner_radius=0).pack(fill="x", side="top")
            ctk.CTkLabel(card, text=judul, text_color=MUTED,
                         font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=14, pady=(12, 2))
            ctk.CTkLabel(card, text=nilai, text_color=TEXT,
                         font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=14)
