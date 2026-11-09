# Aplikasi Sistem Manajemen Koperasi Simpan Pinjam

Dibuat oleh:

1. Kinanty Putri Aulia	F5212510004
2. Fathur Rahman	F5212510011
3. Cliff Sebastiaan Wellem B. F5212510014
4. Ingel Laura	F5212510015
5. Nayla Syafha Nurwahyuddin	F5212510020
6. Saiful	F5212510026
7. Muhammad Alfaizan Rifatullah F5212520036
8. Stevalia Bindi Rahmania	F5212520040

## Deskripsi Aplikasi

Aplikasi desktop berbasis Python untuk mengelola **anggota**, **simpanan**, **pinjaman**, dan **angsuran** koperasi.
Dibangun dengan pola arsitektur **Model-View-Controller (MVC)**, menggunakan **Tkinter / CustomTkinter**
untuk antarmuka dan **MySQL** (melalui Laragon) sebagai basis data.

Fitur utama:

- **Login dan Registrasi** dengan password ter-hash SHA-256 dan pembatasan hak akses berbasis peran (Role-Based Access Control). Akun yang mendaftar sendiri otomatis berperan `Anggota`.
  - `Admin`: mengelola anggota, pengguna, status pinjaman, dan melihat laporan koperasi
  - `Petugas`: mencatat simpanan, memproses pengajuan pinjaman, menerima pembayaran angsuran, dan melihat riwayat anggota
  - `Anggota`: mengajukan pinjaman, melihat dashboard pribadi, dan mengelola data diri
- **Dashboard** dengan kartu statistik yang berbeda untuk setiap peran
- **Manajemen anggota** (CRUD) dengan validasi NIK (16 digit) dan nomor HP
- **Transaksi simpanan** (Pokok, Wajib, Sukarela) beserta pencarian riwayat
- **Pengajuan dan persetujuan pinjaman**: pinjaman yang disetujui otomatis membuat jadwal angsuran
- **Pembayaran angsuran** dengan perhitungan denda keterlambatan otomatis
- **Manajemen pengguna**: tambah, ubah, reset password, hapus (khusus Admin), dan ganti password sendiri
- **Laporan koperasi** per anggota dengan ekspor ke **CSV**
- **Logout** (tombol **Keluar**) untuk kembali ke halaman login
- **Unit test** dengan pytest dan **CI otomatis** dengan GitHub Actions

### Hak Akses per Peran

| Menu | Admin | Petugas | Anggota |
|---|:---:|:---:|:---:|
| Dashboard | ✔ | ✔ | ✔ |
| Data / Kelola Anggota | ✔ (tambah, ubah, hapus) | ✔ (ubah, hapus) | — |
| Transaksi Simpanan | — | ✔ (catat) | — |
| Pengajuan Pinjaman | — | ✔ (setujui / tolak) | ✔ (mengajukan) |
| Pembayaran Angsuran | — | ✔ | — |
| Riwayat Anggota | — | ✔ | — |
| Kelola Pinjaman (ubah status) | ✔ | — | — |
| Manajemen Pengguna | ✔ | — | — |
| Laporan Koperasi (CSV) | ✔ | — | — |
| Data Diri / Profil | — | — | ✔ |

### Aturan Bisnis

Parameter bisnis diatur di `config/settings.py`:

| Pengaturan | Nilai bawaan | Keterangan |
|---|---|---|
| `BUNGA_TAHUNAN_DEFAULT` | `12.0` | Bunga pinjaman per tahun (%) |
| `DENDA_PER_HARI_PERSEN` | `0.1` | Denda per hari keterlambatan, dihitung dari tagihan angsuran (%) |
| `JANGKA_WAKTU_PILIHAN` | `[3, 6, 12, 18, 24, 36]` | Pilihan jangka waktu pinjaman (bulan) |

- Total pinjaman = `jumlah × (1 + bunga/100 × jangka/12)`, dibagi rata ke setiap angsuran (angsuran terakhir menyerap sisa pembulatan).
- Anggota tidak dapat mengajukan pinjaman baru jika masih ada pengajuan berstatus `menunggu` atau pinjaman yang belum lunas.
- Angsuran yang melewati tanggal jatuh tempo otomatis berstatus `terlambat` dan dikenai denda saat dibayar.

## Struktur Direktori MVC

```
uas_praktikumrpl/
├── main.py                      # Titik masuk aplikasi (menjalankan AuthController)
├── requirements.txt             # Daftar dependensi
├── .gitignore
├── config/
│   ├── database.py              # Koneksi MySQL dan fungsi bantu query (fetch_all, fetch_one, execute, transaksi)
│   └── settings.py              # Parameter bisnis (bunga, denda, jangka waktu)
├── utils/
│   └── helpers.py               # Validasi, format rupiah/tanggal, dekorator @aksi dan @baca
├── models/                      # MODEL: akses data dan logika bisnis
│   ├── user_model.py
│   ├── anggota_model.py
│   ├── simpanan_model.py
│   ├── pinjaman_model.py
│   └── laporan_model.py
├── views/                       # VIEW: tampilan antarmuka (pasif, tanpa logika bisnis)
│   ├── login_view.py
│   ├── register_view.py
│   ├── dashboard.py
│   ├── components.py
│   ├── anggota_view.py
│   ├── simpanan_view.py
│   ├── pengajuan_view.py
│   ├── angsuran_view.py
│   ├── pinjaman_admin_view.py
│   ├── pengguna_view.py
│   ├── riwayat_view.py
│   ├── laporan_view.py
│   └── profil_view.py
├── controllers/                 # CONTROLLER: penghubung View dan Model
│   ├── auth_controller.py
│   ├── dashboard_controller.py
│   ├── anggota_controller.py
│   ├── simpanan_controller.py
│   ├── pinjaman_controller.py
│   ├── pengguna_controller.py
│   └── laporan_controller.py
├── tests/                       # Unit test (pytest)
│   └── test_anggota_controller.py
└── .github/workflows/
    └── ci_pipeline.yml          # Pipeline CI GitHub Actions
```

Pembagian tanggung jawab:

| Komponen | Tanggung jawab |
|---|---|
| **Model** | Menjalankan kueri SQL (CRUD, autentikasi, hitung pinjaman dan angsuran) ke MySQL |
| **View** | Menampilkan form, tabel, kartu, dan tombol; tidak berisi logika bisnis |
| **Controller** | Menerima aksi pengguna dari View, memeriksa hak akses dan validasi, memanggil Model, lalu memperbarui View |

## Panduan Instalasi dan Konfigurasi Database MySQL

### 1. Prasyarat

- Python 3.11 atau lebih baru (diuji dengan Python 3.13)
- [Laragon](https://laragon.org/) (menyediakan MySQL)
- Git

### 2. Unduh proyek dan siapkan virtual environment

```bash
git clone https://github.com/naysfha/uas_praktikumrpl.git
cd uas_praktikumrpl
python -m venv env
```

Aktifkan virtual environment:

```powershell
# PowerShell
.\env\Scripts\Activate.ps1
```

```bash
# Git Bash
source env/Scripts/activate
```

Instal seluruh dependensi:

```bash
pip install -r requirements.txt
```

### 3. Konfigurasi database MySQL

1. Buka **Laragon**, lalu klik **Start All** agar layanan MySQL berjalan.
2. Buka **Terminal** pada Laragon dan masuk ke MySQL:

```bash
mysql -u root -p
```

3. Jalankan skrip berikut untuk membuat database, tabel, dan akun uji coba:

```sql
CREATE DATABASE IF NOT EXISTS koperasi;
USE koperasi;

CREATE TABLE pengguna (
    id_pengguna INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    nama_pengguna VARCHAR(100) NOT NULL,
    role ENUM('Admin', 'Petugas', 'Anggota') NOT NULL
);

CREATE TABLE anggota (
    id_anggota INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    id_petugas INT NULL,
    id_pengguna INT NOT NULL UNIQUE,
    nik CHAR(16) NOT NULL UNIQUE,
    nama_anggota VARCHAR(100) NOT NULL,
    alamat TEXT NULL,
    no_hp VARCHAR(20) NOT NULL,
    FOREIGN KEY (id_petugas) REFERENCES pengguna(id_pengguna),
    FOREIGN KEY (id_pengguna) REFERENCES pengguna(id_pengguna)
);

CREATE TABLE simpanan (
    id_simpanan INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    id_anggota INT NOT NULL,
    id_petugas INT NOT NULL,
    jenis_simpanan ENUM('pokok', 'wajib', 'sukarela') NOT NULL,
    tanggal_simpanan DATE NOT NULL,
    saldo DECIMAL(15,2) NOT NULL,
    keterangan VARCHAR(1000) NULL,
    INDEX (tanggal_simpanan),
    FOREIGN KEY (id_anggota) REFERENCES anggota(id_anggota),
    FOREIGN KEY (id_petugas) REFERENCES pengguna(id_pengguna)
);

CREATE TABLE pengajuan_pinjaman (
    id_pengajuan INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    id_anggota INT NOT NULL,
    id_petugas INT NULL,
    tanggal_pengajuan DATE NOT NULL,
    jumlah_pengajuan DECIMAL(15,2) NOT NULL,
    jangka_waktu SMALLINT NOT NULL,
    tujuan_pinjaman VARCHAR(1000) NULL,
    status_pengajuan ENUM('menunggu', 'disetujui', 'ditolak') NOT NULL DEFAULT 'menunggu',
    catatan VARCHAR(255) NULL,
    FOREIGN KEY (id_anggota) REFERENCES anggota(id_anggota),
    FOREIGN KEY (id_petugas) REFERENCES pengguna(id_pengguna)
);

CREATE TABLE pinjaman (
    id_pinjaman INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    id_pengajuan INT NOT NULL UNIQUE,
    tanggal_pencairan DATE NOT NULL,
    jumlah_pinjaman DECIMAL(15,2) NOT NULL,
    bunga DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    jangka_waktu SMALLINT NOT NULL,
    total_pinjaman DECIMAL(15,2) NOT NULL,
    sisa_pinjaman DECIMAL(15,2) NOT NULL,
    status_pinjaman ENUM('berjalan', 'lunas', 'bermasalah') NOT NULL DEFAULT 'berjalan',
    FOREIGN KEY (id_pengajuan) REFERENCES pengajuan_pinjaman(id_pengajuan)
);

CREATE TABLE jadwal_angsuran (
    id_jadwal INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    id_pinjaman INT NOT NULL,
    angsuran_ke SMALLINT NOT NULL,
    tanggal_jatuh_tempo DATE NOT NULL,
    jumlah_tagihan DECIMAL(15,2) NOT NULL,
    denda DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    status_jadwal ENUM('belum_dibayar', 'lunas', 'terlambat') NOT NULL DEFAULT 'belum_dibayar',
    FOREIGN KEY (id_pinjaman) REFERENCES pinjaman(id_pinjaman)
);

CREATE TABLE angsuran (
    id_angsuran INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    id_pinjaman INT NOT NULL,
    id_petugas INT NOT NULL,
    tanggal_bayar DATE NOT NULL,
    angsuran_ke SMALLINT NOT NULL,
    jumlah_bayar DECIMAL(15,2) NOT NULL,
    denda DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    keterangan VARCHAR(1000) NULL,
    FOREIGN KEY (id_pinjaman) REFERENCES pinjaman(id_pinjaman),
    FOREIGN KEY (id_petugas) REFERENCES pengguna(id_pengguna)
);

-- Akun uji coba (password disimpan sebagai hash SHA-256)
INSERT INTO pengguna (username, password, nama_pengguna, role) VALUES
('admin',   SHA2('admin123',   256), 'Administrator',  'Admin'),
('petugas', SHA2('petugas123', 256), 'Petugas Koperasi', 'Petugas'),
('anggota', SHA2('anggota123', 256), 'Anggota Uji',    'Anggota');
```

4. Pengaturan koneksi berada di `config/database.py`. Nilai bawaannya sudah sesuai dengan Laragon:

| Pengaturan | Nilai |
|---|---|
| host | `localhost` |
| database | `koperasi` |
| username | `root` |
| password | *(kosong)* |

Jika MySQL kamu memakai username atau password yang berbeda, ubah nilai tersebut pada file `config/database.py`.

### 4. Struktur Database

Database `koperasi` terdiri dari **7 tabel**:

| Tabel | Fungsi | Kolom utama |
|---|---|---|
| `pengguna` | Akun login dan peran | `id_pengguna`, `username` (unik), `password` (SHA-256), `nama_pengguna`, `role` (`Admin` / `Petugas` / `Anggota`) |
| `anggota` | Data diri anggota koperasi | `id_anggota`, `id_pengguna` (unik), `id_petugas`, `nik` (unik, 16 karakter), `nama_anggota`, `alamat`, `no_hp` |
| `simpanan` | Transaksi simpanan anggota | `id_simpanan`, `id_anggota`, `id_petugas`, `jenis_simpanan` (`pokok` / `wajib` / `sukarela`), `tanggal_simpanan`, `saldo`, `keterangan` |
| `pengajuan_pinjaman` | Pengajuan pinjaman dari anggota | `id_pengajuan`, `id_anggota`, `id_petugas`, `tanggal_pengajuan`, `jumlah_pengajuan`, `jangka_waktu`, `tujuan_pinjaman`, `status_pengajuan` (`menunggu` / `disetujui` / `ditolak`), `catatan` |
| `pinjaman` | Pinjaman aktif hasil pengajuan yang disetujui | `id_pinjaman`, `id_pengajuan` (unik), `tanggal_pencairan`, `jumlah_pinjaman`, `bunga`, `jangka_waktu`, `total_pinjaman`, `sisa_pinjaman`, `status_pinjaman` (`berjalan` / `lunas` / `bermasalah`) |
| `jadwal_angsuran` | Jadwal tagihan setiap bulan | `id_jadwal`, `id_pinjaman`, `angsuran_ke`, `tanggal_jatuh_tempo`, `jumlah_tagihan`, `denda`, `status_jadwal` (`belum_dibayar` / `lunas` / `terlambat`) |
| `angsuran` | Catatan pembayaran angsuran | `id_angsuran`, `id_pinjaman`, `id_petugas`, `tanggal_bayar`, `angsuran_ke`, `jumlah_bayar`, `denda`, `keterangan` |

Relasi antartabel:

```
pengguna 1 ── 1 anggota 1 ── N simpanan
                   │
                   └── 1 ── N pengajuan_pinjaman 1 ── 1 pinjaman 1 ── N jadwal_angsuran
                                                           │
                                                           └── 1 ── N angsuran
```

`pengguna` juga menjadi acuan `id_petugas` pada tabel `anggota`, `simpanan`, `pengajuan_pinjaman`, dan `angsuran`.

## Cara Menjalankan Aplikasi

Pastikan MySQL di Laragon sudah menyala (**Start All**), lalu dari folder proyek dengan virtual environment aktif:

```bash
python main.py
```

Jendela **Login** akan muncul. Masuk menggunakan akun uji coba (sesuai skrip SQL di atas):

| Username | Password | Role | Hak akses |
|---|---|---|---|
| `admin` | `admin123` | Admin | Kelola anggota, pinjaman, pengguna, dan laporan |
| `petugas` | `petugas123` | Petugas | Simpanan, proses pengajuan, angsuran, riwayat anggota |
| `anggota` | `anggota123` | Anggota | Ajukan pinjaman, dashboard pribadi, data diri |

Alur penggunaan yang disarankan:

1. Login sebagai **Admin**, lalu daftarkan data anggota (satu akun `Anggota` hanya dapat memiliki satu data anggota).
2. Login sebagai **Petugas**, lalu catat transaksi simpanan anggota.
3. Login sebagai **Anggota**, lalu ajukan pinjaman (pilih nominal dan jangka waktu).
4. Login sebagai **Petugas**, lalu setujui atau tolak pengajuan. Jika disetujui, pinjaman dan jadwal angsuran dibuat otomatis.
5. Petugas menerima pembayaran angsuran setiap bulan pada menu **Pembayaran Angsuran**.
6. Admin melihat ringkasan di menu **Laporan Koperasi** dan dapat mengekspornya ke CSV.

Gunakan tombol **Keluar** di bagian bawah sidebar untuk kembali ke halaman login. Pengguna baru juga dapat mendaftar lewat halaman **Register** (otomatis berperan `Anggota`).

## Menjalankan Pengujian

```bash
pytest -v
```

## Membuat Berkas Eksekusi (.exe)

```bash
pyinstaller --noconfirm --onefile --windowed --name "AplikasiKoperasi" main.py
```

Hasilnya berada di `dist/AplikasiKoperasi.exe`. MySQL (Laragon) harus tetap menyala saat aplikasi dibuka.

## Continuous Integration

Setiap `push` atau `pull request` ke branch `main` menjalankan pipeline GitHub Actions
(`.github/workflows/ci_pipeline.yml`): checkout kode, menyiapkan Python 3.11, instalasi dependensi, lalu menjalankan **pytest**.
