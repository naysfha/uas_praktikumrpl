import pytest
from datetime import date
from unittest.mock import MagicMock

# Import fungsi yang mau diuji
from utils.helpers import rupiah, validasi_nik, tambah_bulan
from controllers.anggota_controller import AnggotaController

# TEST 1: Pengujian Format Rupiah
def test_format_rupiah():
    # Menguji apakah angka diubah dengan benar ke format Rp dan pakai titik
    assert rupiah(50000) == "Rp 50.000"
    assert rupiah(1500000) == "Rp 1.500.000"
    assert rupiah(0) == "Rp 0"

# TEST 2: Pengujian Validasi NIK
def test_validasi_nik():
    # NIK yang benar (16 digit angka)
    assert validasi_nik("7271010101010001") is True
    
    # NIK yang salah (kurang dari 16 digit atau ada huruf)
    assert validasi_nik("12345") is False
    assert validasi_nik("727101010101000A") is False

# TEST 3: Pengujian Logika Tambah Bulan (Jatuh Tempo)
def test_tambah_bulan_jatuh_tempo():
    # Skenario: Pinjam tanggal 31 Januari 2024, jangka waktu 1 bulan.
    # Karena Februari 2024 hanya sampai tanggal 29 (kabisat), 
    # sistem harus pintar menyesuaikannya jadi 29 Februari.
    tanggal_pinjam = date(2024, 1, 31)
    jatuh_tempo = tambah_bulan(tanggal_pinjam, 1)
    assert jatuh_tempo == date(2024, 2, 29)

# TEST 4: Pengujian RBAC (Hak Akses) di Controller
def test_akses_tambah_anggota_ditolak():
    # Skenario: Seorang 'Petugas' mencoba menambah anggota (padahal hanya Admin yang boleh)
    user_petugas = {"id_pengguna": 1, "role": "Petugas"}
    ctrl = AnggotaController(user_petugas)
    
    # Panggil fungsi tambah dengan data dummy
    ok, pesan = ctrl.tambah(1, "7271010101010001", "Budi Santoso", "081122334455", "Jalan Karajalembah")
    
    # Pastikan sistem menolak (ok = False) dan mengembalikan pesan error yang tepat
    assert ok is False
    assert "Hanya Admin" in pesan

# TEST 5: Pengujian Model dengan Mocking Database
def test_get_anggota_by_id(monkeypatch):
    from models.anggota_model import AnggotaModel
    
    # Kita bohongi fungsi 'fetch_one' agar tidak benar-benar memanggil database MySQL
    mock_fetch = MagicMock(return_value={"id_anggota": 1, "nama_anggota": "Nayla"})
    monkeypatch.setattr("models.anggota_model.fetch_one", mock_fetch)

    model = AnggotaModel()
    hasil = model.by_id(1)

    # Pastikan hasilnya sesuai dengan data bohongan kita
    assert hasil["nama_anggota"] == "Nayla"
    # Pastikan fungsi database tadi benar-benar dipanggil oleh sistem
    mock_fetch.assert_called_once()