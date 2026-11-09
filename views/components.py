import customtkinter as ctk
from tkinter import ttk, messagebox

BG = "#f8f9fb"
TEXT = "#1f2937"
MUTED = "#6b7280"
CARD_BG = "#ffffff"
BORDER = "#e5e7eb"
ACCENT = "#4f46e5"
BIRU = "#2563eb"
HIJAU = "#16a34a"
MERAH = "#dc2626"
KUNING = "#d97706"

_style_siap = False


def _siapkan_style():
    global _style_siap
    if _style_siap:
        return
    st = ttk.Style()
    try:
        st.theme_use("clam")
    except Exception:
        pass
    st.configure("Treeview", rowheight=28, font=("Segoe UI", 10), background="white",
                 fieldbackground="white", borderwidth=0)
    st.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#eef0f6",
                 foreground=TEXT, relief="flat")
    st.map("Treeview", background=[("selected", ACCENT)], foreground=[("selected", "white")])
    _style_siap = True


def header_halaman(parent, judul, subjudul=None, tombol=()):
    """tombol: daftar (teks, command, warna)."""
    bar = ctk.CTkFrame(parent, fg_color="transparent")
    bar.pack(fill="x", pady=(0, 12))
    kiri = ctk.CTkFrame(bar, fg_color="transparent")
    kiri.pack(side="left")
    ctk.CTkLabel(kiri, text=judul, text_color=TEXT,
                 font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w")
    if subjudul:
        ctk.CTkLabel(kiri, text=subjudul, text_color=MUTED, font=ctk.CTkFont(size=12)).pack(anchor="w")
    kanan = ctk.CTkFrame(bar, fg_color="transparent")
    kanan.pack(side="right")
    for teks, cmd, warna in tombol:
        ctk.CTkButton(kanan, text=teks, command=cmd, fg_color=warna, width=110).pack(side="left", padx=4)
    return bar


def kotak_cari(parent, command, placeholder="Cari..."):
    entry = ctk.CTkEntry(parent, placeholder_text=placeholder, width=320)
    entry.pack(anchor="w", pady=(0, 10))
    entry.bind("<KeyRelease>", lambda e: command())
    return entry


class DataTable(ctk.CTkFrame):
    """Tabel (Treeview) dengan scrollbar. kolom: daftar (nama, lebar, anchor)."""

    def __init__(self, master, kolom, baris=10, on_pilih=None):
        super().__init__(master, fg_color=CARD_BG, corner_radius=8, border_width=1, border_color=BORDER)
        _siapkan_style()
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.tree = ttk.Treeview(self, columns=[k[0] for k in kolom], show="headings",
                                 selectmode="browse", height=baris)
        for nama, lebar, anchor in kolom:
            self.tree.heading(nama, text=nama)
            self.tree.column(nama, width=lebar, anchor=anchor, stretch=True)
        sb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(8, 0), pady=8)
        sb.grid(row=0, column=1, sticky="ns", pady=8, padx=(0, 4))
        if on_pilih:
            self.tree.bind("<<TreeviewSelect>>", lambda e: on_pilih())

    def isi(self, baris):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in baris:
            self.tree.insert("", "end", values=["" if v is None else v for v in row])

    def terpilih(self):
        sel = self.tree.selection()
        return self.tree.item(sel[0], "values") if sel else None


def pilih_baris(tabel, pesan="Pilih satu baris pada tabel terlebih dahulu."):
    v = tabel.terpilih()
    if not v:
        messagebox.showwarning("Pilih Data", pesan)
    return v


def tampilkan_hasil(ok, pesan):
    if ok:
        messagebox.showinfo("Berhasil", pesan)
    else:
        messagebox.showerror("Gagal", pesan)
    return ok


class FormDialog(ctk.CTkToplevel):
    """Dialog form generik.
    fields: list dict {key, label, kind: entry|password|option|info, value, opsi, placeholder}
    on_submit(dict) -> (ok, pesan)."""

    def __init__(self, master, judul, fields, on_submit, on_success=None, tombol="Simpan", lebar=440):
        super().__init__(master)
        self.title(judul)
        self.resizable(False, False)
        self.on_submit, self.on_success = on_submit, on_success
        self.getters = {}
        ctk.CTkLabel(self, text=judul, font=ctk.CTkFont(size=18, weight="bold")).pack(
            padx=24, pady=(20, 8), anchor="w")
        isi = lebar - 48
        for f in fields:
            kind = f.get("kind", "entry")
            if kind == "info":
                ctk.CTkLabel(self, text=f["value"], justify="left", wraplength=isi,
                             text_color=MUTED).pack(padx=24, pady=(4, 4), anchor="w")
                continue
            ctk.CTkLabel(self, text=f["label"], font=ctk.CTkFont(size=12, weight="bold")).pack(
                padx=24, pady=(6, 0), anchor="w")
            if kind == "option":
                var = ctk.StringVar(value=f.get("value") or f["opsi"][0])
                ctk.CTkOptionMenu(self, values=f["opsi"], variable=var, width=isi).pack(padx=24, pady=(0, 4))
                self.getters[f["key"]] = var.get
            else:
                e = ctk.CTkEntry(self, width=isi, placeholder_text=f.get("placeholder", ""),
                                 show="*" if kind == "password" else "")
                if f.get("value") not in (None, ""):
                    e.insert(0, str(f["value"]))
                e.pack(padx=24, pady=(0, 4))
                self.getters[f["key"]] = (lambda w=e: w.get().strip())
        self.lbl_status = ctk.CTkLabel(self, text="", text_color=MERAH, wraplength=isi, justify="left")
        self.lbl_status.pack(padx=24, pady=(6, 0), anchor="w")
        ctk.CTkButton(self, text=tombol, command=self._kirim, width=isi, fg_color=HIJAU,
                      hover_color="#15803d").pack(padx=24, pady=(8, 20))
        self.transient(master.winfo_toplevel())
        self.after(150, self._modal)

    def _modal(self):
        try:
            self.grab_set()
            self.focus()
        except Exception:
            pass

    def _kirim(self):
        data = {k: g() for k, g in self.getters.items()}
        ok, pesan = self.on_submit(data)
        if ok:
            if pesan:
                messagebox.showinfo("Berhasil", pesan, parent=self)
            self.destroy()
            if self.on_success:
                self.on_success()
        else:
            self.lbl_status.configure(text=pesan)
