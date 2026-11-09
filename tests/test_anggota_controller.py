from controllers.anggota_controller import AnggotaController

def test_tambah_anggota_gagal_karena_bukan_admin():
    # Simulasikan user dengan role Petugas
    user_petugas = {"id_pengguna": 1, "role": "Petugas"}
    ctrl = AnggotaController(user_petugas)
    
    # Coba tambah anggota
    ok, pesan = ctrl.tambah(1, "1234567890123456", "Ibnaty Naeela ", "081122334455", "Jalan Merpati")
    
    assert ok is False
    assert "Hanya Admin" in pesan