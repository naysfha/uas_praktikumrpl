from datetime import date
from decimal import Decimal

from config.database import fetch_all, fetch_one, execute, transaksi
from config.settings import DENDA_PER_HARI_PERSEN
from utils.helpers import AturanBisnis, tambah_bulan

_DUA = Decimal("0.01")


class PinjamanModel:

    # ---------- Pengajuan ----------
    @staticmethod
    def ajukan(id_anggota, jumlah, jangka, tujuan):
        with transaksi() as cur:
            cur.execute("""SELECT 1 FROM pengajuan_pinjaman
                           WHERE id_anggota=%s AND status_pengajuan='menunggu' LIMIT 1""", (id_anggota,))
            if cur.fetchone():
                raise AturanBisnis("Masih ada pengajuan yang menunggu persetujuan.")
            cur.execute("""SELECT 1 FROM pinjaman pj
                           JOIN pengajuan_pinjaman pg ON pg.id_pengajuan = pj.id_pengajuan
                           WHERE pg.id_anggota=%s AND pj.status_pinjaman IN ('berjalan','bermasalah') LIMIT 1""",
                        (id_anggota,))
            if cur.fetchone():
                raise AturanBisnis("Pinjaman sebelumnya belum lunas.")
            cur.execute("""INSERT INTO pengajuan_pinjaman
                           (id_anggota, tanggal_pengajuan, jumlah_pengajuan, jangka_waktu, tujuan_pinjaman)
                           VALUES (%s, CURDATE(), %s, %s, %s)""", (id_anggota, jumlah, jangka, tujuan))

    @staticmethod
    def pengajuan_list(id_anggota=None, status=None):
        return fetch_all("""
            SELECT pg.id_pengajuan, pg.tanggal_pengajuan, a.nama_anggota, pg.jumlah_pengajuan,
                   pg.jangka_waktu, pg.tujuan_pinjaman, pg.status_pengajuan, pg.catatan
            FROM pengajuan_pinjaman pg JOIN anggota a ON a.id_anggota = pg.id_anggota
            WHERE (%s IS NULL OR pg.id_anggota = %s) AND (%s IS NULL OR pg.status_pengajuan = %s)
            ORDER BY pg.id_pengajuan DESC""", (id_anggota, id_anggota, status, status))

    @staticmethod
    def hitung_total(jumlah, bunga_tahunan, jangka):
        jumlah = Decimal(jumlah)
        return (jumlah * (1 + Decimal(str(bunga_tahunan)) / 100 * Decimal(jangka) / 12)).quantize(_DUA)

    @staticmethod
    def proses_pengajuan(id_pengajuan, id_petugas, setuju, catatan, bunga):
        """Setujui (membuat pinjaman + jadwal angsuran) atau tolak pengajuan."""
        with transaksi() as cur:
            cur.execute("SELECT * FROM pengajuan_pinjaman WHERE id_pengajuan=%s FOR UPDATE", (id_pengajuan,))
            pg = cur.fetchone()
            if not pg:
                raise AturanBisnis("Pengajuan tidak ditemukan.")
            if pg['status_pengajuan'] != 'menunggu':
                raise AturanBisnis("Pengajuan ini sudah diproses.")
            status = 'disetujui' if setuju else 'ditolak'
            cur.execute("""UPDATE pengajuan_pinjaman SET status_pengajuan=%s, id_petugas=%s, catatan=%s
                           WHERE id_pengajuan=%s""", (status, id_petugas, catatan, id_pengajuan))
            if not setuju:
                return
            jumlah, n = pg['jumlah_pengajuan'], pg['jangka_waktu']
            total = PinjamanModel.hitung_total(jumlah, bunga, n)
            cur.execute("""INSERT INTO pinjaman (id_pengajuan, tanggal_pencairan, jumlah_pinjaman, bunga,
                                                 jangka_waktu, total_pinjaman, sisa_pinjaman)
                           VALUES (%s, CURDATE(), %s, %s, %s, %s, %s)""",
                        (id_pengajuan, jumlah, bunga, n, total, total))
            id_pinjaman = cur.lastrowid
            pokok = (total / n).quantize(_DUA)
            hari_ini = date.today()
            for k in range(1, n + 1):
                tagihan = pokok if k < n else total - pokok * (n - 1)
                cur.execute("""INSERT INTO jadwal_angsuran (id_pinjaman, angsuran_ke, tanggal_jatuh_tempo, jumlah_tagihan)
                               VALUES (%s,%s,%s,%s)""", (id_pinjaman, k, tambah_bulan(hari_ini, k), tagihan))

    # ---------- Pinjaman & jadwal ----------
    @staticmethod
    def refresh_keterlambatan():
        execute("""UPDATE jadwal_angsuran SET status_jadwal='terlambat'
                   WHERE status_jadwal='belum_dibayar' AND tanggal_jatuh_tempo < CURDATE()""")

    @staticmethod
    def pinjaman_list(status=None, id_anggota=None, aktif_saja=False):
        extra = "AND pj.status_pinjaman <> 'lunas'" if aktif_saja else ""
        return fetch_all(f"""
            SELECT pj.id_pinjaman, a.nama_anggota, pj.tanggal_pencairan, pj.jumlah_pinjaman, pj.bunga,
                   pj.jangka_waktu, pj.total_pinjaman, pj.sisa_pinjaman, pj.status_pinjaman,
                   (SELECT COUNT(*) FROM jadwal_angsuran j
                     WHERE j.id_pinjaman = pj.id_pinjaman AND j.status_jadwal = 'lunas') AS terbayar
            FROM pinjaman pj
            JOIN pengajuan_pinjaman pg ON pg.id_pengajuan = pj.id_pengajuan
            JOIN anggota a ON a.id_anggota = pg.id_anggota
            WHERE (%s IS NULL OR pj.status_pinjaman = %s) AND (%s IS NULL OR pg.id_anggota = %s) {extra}
            ORDER BY pj.id_pinjaman DESC""", (status, status, id_anggota, id_anggota))

    @staticmethod
    def jadwal(id_pinjaman):
        return fetch_all("""SELECT * FROM jadwal_angsuran WHERE id_pinjaman=%s ORDER BY angsuran_ke""",
                         (id_pinjaman,))

    @staticmethod
    def hitung_denda(tagihan, jatuh_tempo):
        hari = (date.today() - jatuh_tempo).days
        if hari <= 0:
            return Decimal("0.00")
        return (Decimal(tagihan) * Decimal(str(DENDA_PER_HARI_PERSEN)) / 100 * hari).quantize(_DUA)

    @staticmethod
    def angsuran_berikut(id_pinjaman):
        """Tagihan berikutnya beserta denda hari ini (None jika sudah lunas semua)."""
        j = fetch_one("""SELECT * FROM jadwal_angsuran WHERE id_pinjaman=%s AND status_jadwal <> 'lunas'
                         ORDER BY angsuran_ke LIMIT 1""", (id_pinjaman,))
        if j:
            j['denda_hari_ini'] = PinjamanModel.hitung_denda(j['jumlah_tagihan'], j['tanggal_jatuh_tempo'])
        return j

    @staticmethod
    def bayar_angsuran(id_pinjaman, id_petugas, keterangan):
        with transaksi() as cur:
            cur.execute("SELECT * FROM pinjaman WHERE id_pinjaman=%s FOR UPDATE", (id_pinjaman,))
            pj = cur.fetchone()
            if not pj or pj['status_pinjaman'] == 'lunas':
                raise AturanBisnis("Pinjaman tidak ditemukan atau sudah lunas.")
            cur.execute("""SELECT * FROM jadwal_angsuran WHERE id_pinjaman=%s AND status_jadwal <> 'lunas'
                           ORDER BY angsuran_ke LIMIT 1""", (id_pinjaman,))
            j = cur.fetchone()
            if not j:
                raise AturanBisnis("Semua angsuran sudah lunas.")
            denda = PinjamanModel.hitung_denda(j['jumlah_tagihan'], j['tanggal_jatuh_tempo'])
            cur.execute("""INSERT INTO angsuran (id_pinjaman, id_petugas, tanggal_bayar, angsuran_ke,
                                                 jumlah_bayar, denda, keterangan)
                           VALUES (%s,%s,CURDATE(),%s,%s,%s,%s)""",
                        (id_pinjaman, id_petugas, j['angsuran_ke'], j['jumlah_tagihan'], denda, keterangan))
            cur.execute("UPDATE jadwal_angsuran SET status_jadwal='lunas', denda=%s WHERE id_jadwal=%s",
                        (denda, j['id_jadwal']))
            sisa = max(pj['sisa_pinjaman'] - j['jumlah_tagihan'], Decimal("0"))
            lunas = sisa <= 0
            cur.execute("UPDATE pinjaman SET sisa_pinjaman=%s, status_pinjaman=%s WHERE id_pinjaman=%s",
                        (sisa, 'lunas' if lunas else pj['status_pinjaman'], id_pinjaman))
            return j['angsuran_ke'], j['jumlah_tagihan'], denda, lunas

    @staticmethod
    def angsuran_riwayat(id_anggota=None):
        return fetch_all("""
            SELECT an.id_angsuran, an.tanggal_bayar, an.id_pinjaman, an.angsuran_ke, an.jumlah_bayar,
                   an.denda, an.keterangan, pt.nama_pengguna AS petugas
            FROM angsuran an
            JOIN pinjaman pj ON pj.id_pinjaman = an.id_pinjaman
            JOIN pengajuan_pinjaman pg ON pg.id_pengajuan = pj.id_pengajuan
            JOIN pengguna pt ON pt.id_pengguna = an.id_petugas
            WHERE %s IS NULL OR pg.id_anggota = %s
            ORDER BY an.id_angsuran DESC""", (id_anggota, id_anggota))

    @staticmethod
    def ubah_status(id_pinjaman, status):
        pj = fetch_one("SELECT status_pinjaman FROM pinjaman WHERE id_pinjaman=%s", (id_pinjaman,))
        if not pj:
            raise AturanBisnis("Pinjaman tidak ditemukan.")
        if pj['status_pinjaman'] == 'lunas':
            raise AturanBisnis("Pinjaman yang sudah lunas tidak bisa diubah statusnya.")
        execute("UPDATE pinjaman SET status_pinjaman=%s WHERE id_pinjaman=%s", (status, id_pinjaman))
