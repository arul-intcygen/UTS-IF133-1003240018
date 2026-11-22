"""
Generator laporan UTS IF133 -> DOCX (lalu dikonversi ke PDF).

Cara pakai:
    1. Taruh screenshot di folder screenshots/ dengan nama file yang sesuai
       (lihat daftar SHOTS di bawah).
    2. Jalankan: py -3.13 buat-laporan.py
    3. DOCX dan PDF dihasilkan di folder ini.

Kalau sebuah screenshot belum ada, laporan tetap dibuat dan bagian itu diisi
kotak placeholder supaya jelas mana yang masih kosong.
"""

import os
import glob
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = os.path.dirname(os.path.abspath(__file__))
SHOT_DIR = os.path.join(BASE, "screenshots")
OUT_DOCX = os.path.join(BASE, "UTS_IF133_1003240018_SahrulSolihin.docx")

NAMA = "Sahrul Solihin"
NIM = "1003240018"
MK = "Pemrograman .NET"
KODE_MK = "IF133"
DOSEN = "Taufik Iqbal Ramdhani, S.Kom., M.Sc."

# (nama file, judul keterangan gambar)
SHOTS = [
    ("01_swagger_home.png", "Halaman Swagger menampilkan seluruh endpoint API"),
    ("02_get_list_kosong.png", "GET /api/products saat database masih kosong"),
    ("03_post_201.png", "POST /api/products berhasil dengan status 201 Created"),
    ("04_post_409.png", "POST /api/products dengan Code duplikat ditolak 409"),
    ("05_post_400.png", "POST /api/products dengan payload tidak valid"),
    ("06_get_200.png", "GET /api/products/{id} mengembalikan 200 OK"),
    ("07_get_404.png", "GET /api/products/100 mengembalikan 404 Not Found"),
    ("08_put_204.png", "PUT /api/products/{id} berhasil dengan 204 No Content"),
    ("09_delete_204.png", "DELETE /api/products/{id} berhasil dengan 204"),
    ("10_delete_404.png", "DELETE ulang pada id yang sama menghasilkan 404"),
    ("11_error_500.png", "Respons 500 tanpa stack trace"),
    ("12_log_server.png", "Log server mencatat detail exception"),
    ("13_migration.png", "Hasil dotnet ef migrations list"),
    ("14_db_tabel.png", "Isi tabel Products pada database SQLite"),
]

FONT = "Times New Roman"

THEME_ATTRS = (
    "w:asciiTheme",
    "w:hAnsiTheme",
    "w:eastAsiaTheme",
    "w:cstheme",
)


def force_font(rpr):
    """Hapus atribut theme font supaya setting eksplisit benar-benar dipakai.

    Tanpa ini, w:asciiTheme="majorHAnsi" pada style Heading membuat Word dan
    LibreOffice tetap memakai Calibri walaupun w:ascii sudah diset.
    """
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.insert(0, rf)
    for attr in THEME_ATTRS:
        if rf.get(qn(attr)) is not None:
            del rf.attrib[qn(attr)]
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rf.set(qn(attr), FONT)
    return rf


def fix_doc_defaults(doc):
    """Bersihkan theme font pada rPrDefault di styles.xml."""
    styles_el = doc.styles.element
    rpr_default = styles_el.find(qn("w:docDefaults") + "/" + qn("w:rPrDefault"))
    if rpr_default is None:
        rpr_default = styles_el.find(qn("w:docDefaults"))
    if rpr_default is not None:
        rpr = rpr_default.find(qn("w:rPr"))
        if rpr is not None:
            force_font(rpr)


# --------------------------------------------------------------------------
# Helper format
# --------------------------------------------------------------------------
def set_doc_defaults(doc):
    st = doc.styles["Normal"]
    st.font.name = FONT
    st.font.size = Pt(12)
    rpr = st.element.get_or_add_rPr()
    force_font(rpr)
    pf = st.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)


def style_heading(doc, level, size, bold=True, space_before=12, space_after=6):
    st = doc.styles[f"Heading {level}"]
    st.font.name = FONT
    st.font.size = Pt(size)
    st.font.bold = bold
    st.font.color.rgb = RGBColor(0, 0, 0)
    rpr = st.element.get_or_add_rPr()
    force_font(rpr)
    # buang border bawah bawaan heading
    ppr = st.element.get_or_add_pPr()
    for bd in ppr.findall(qn("w:pBdr")):
        ppr.remove(bd)
    pf = st.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    pf.first_line_indent = Cm(0)


def para(doc, text="", bold=False, italic=False, size=12, align=None,
         indent=True, space_after=0, space_before=0):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    pf.space_after = Pt(space_after)
    pf.space_before = Pt(space_before)
    if indent:
        pf.first_line_indent = Cm(1.27)
    else:
        pf.first_line_indent = Cm(0)
    if align is not None:
        p.alignment = align
    r = p.add_run(text)
    r.font.name = FONT
    r.font.size = Pt(size)
    r.bold = bold
    r.italic = italic
    r.font.color.rgb = RGBColor(0, 0, 0)
    return p


def rich_para(doc, parts, indent=True, align=WD_ALIGN_PARAGRAPH.JUSTIFY,
              space_after=0):
    """parts = list of (text, bold, italic, mono)"""
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    pf.space_after = Pt(space_after)
    pf.first_line_indent = Cm(1.27) if indent else Cm(0)
    p.alignment = align
    for text, bold, italic, mono in parts:
        r = p.add_run(text)
        r.font.name = "Consolas" if mono else FONT
        r.font.size = Pt(11 if mono else 12)
        r.bold = bold
        r.italic = italic
        r.font.color.rgb = RGBColor(0, 0, 0)
    return p


def bullet(doc, text):
    """Template kampus tanpa style List Bullet -> pakai tab + indent negatif."""
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    pf.left_indent = Cm(1.27)
    pf.first_line_indent = Cm(-0.5)
    pf.space_after = Pt(0)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r = p.add_run("-\t" + text)
    r.font.name = FONT
    r.font.size = Pt(12)
    r.font.color.rgb = RGBColor(0, 0, 0)
    # tab stop supaya teks rata setelah tanda -
    pPr = p._p.get_or_add_pPr()
    tabs = OxmlElement("w:tabs")
    tab = OxmlElement("w:tab")
    tab.set(qn("w:val"), "left")
    tab.set(qn("w:pos"), str(int(Cm(1.27).twips)))
    tabs.append(tab)
    pPr.append(tabs)
    return p


def code_block(doc, lines):
    """Blok kode: Consolas 9.5pt, satu spasi, latar abu tipis."""
    for line in lines:
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
        pf.space_after = Pt(0)
        pf.space_before = Pt(0)
        pf.left_indent = Cm(0.75)
        pf.first_line_indent = Cm(0)
        r = p.add_run(line if line else " ")
        r.font.name = "Consolas"
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(0, 0, 0)
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:fill"), "F2F2F2")
        p._p.get_or_add_pPr().append(shd)
    # beri jarak setelah blok
    doc.paragraphs[-1].paragraph_format.space_after = Pt(6)


def set_cell_borders(table):
    tbl = table._tbl
    tblPr = tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "6")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), "000000")
        borders.append(el)
    tblPr.append(borders)


def make_table(doc, headers, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = True
    set_cell_borders(t)

    hdr = t.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        r = p.add_run(h)
        r.font.name = FONT
        r.font.size = Pt(11)
        r.bold = True
        r.font.color.rgb = RGBColor(0, 0, 0)
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:fill"), "D9E2F3")
        hdr[i]._tc.get_or_add_tcPr().append(shd)

    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
            r = p.add_run(str(val))
            r.font.name = FONT
            r.font.size = Pt(11)
            r.font.color.rgb = RGBColor(0, 0, 0)

    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)

    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    return t


def caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf = p.paragraph_format
    pf.space_before = Pt(6)
    pf.space_after = Pt(3)
    pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
    pf.first_line_indent = Cm(0)
    r = p.add_run(text)
    r.font.name = FONT
    r.font.size = Pt(10)
    r.italic = True
    r.font.color.rgb = RGBColor(0, 0, 0)
    return p


def add_image_or_placeholder(doc, filename, title, index):
    path = os.path.join(SHOT_DIR, filename)
    caption_text = f"Gambar {index}. {title}"

    if os.path.exists(path):
        # Ukuran gambar harus dihitung: screenshot Swagger tinggi (rasio bisa
        # 1:2,6) akan melebihi tinggi halaman kalau hanya lebar yang dipatok.
        # Batas aman: lebar 15 cm, tinggi maksimum 20 cm (area teks A4 dengan
        # margin 2,5 cm adalah 16 cm x 24,7 cm, dikurangi ruang caption).
        from PIL import Image

        MAX_W_CM = 15.0
        MAX_H_CM = 20.0

        with Image.open(path) as im:
            px_w, px_h = im.size

        ratio = px_h / px_w
        width_cm = MAX_W_CM
        height_cm = width_cm * ratio

        if height_cm > MAX_H_CM:
            height_cm = MAX_H_CM
            width_cm = height_cm / ratio

        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.first_line_indent = Cm(0)
        # Jangan pisahkan gambar dari captionnya ke halaman berikutnya.
        p.paragraph_format.keep_with_next = True
        p.add_run().add_picture(path, width=Cm(width_cm), height=Cm(height_cm))
        cap = caption(doc, caption_text)
        cap.paragraph_format.keep_together = True
    else:
        # Placeholder dan caption ditaruh dalam SATU tabel dua baris, sehingga
        # keduanya tidak mungkin terpisah ke halaman berbeda.
        t = doc.add_table(rows=2, cols=1)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_cell_borders(t)

        trPr = t.rows[0]._tr.get_or_add_trPr()
        trPr.append(OxmlElement("w:cantSplit"))
        trPr2 = t.rows[1]._tr.get_or_add_trPr()
        trPr2.append(OxmlElement("w:cantSplit"))

        box = t.rows[0].cells[0]
        box.width = Cm(15)
        p = box.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(18)
        r = p.add_run(f"[Screenshot belum diisi: {filename}]")
        r.font.name = FONT
        r.font.size = Pt(10)
        r.italic = True
        r.font.color.rgb = RGBColor(0x80, 0x80, 0x80)

        cap_cell = t.rows[1].cells[0]
        cap_cell.width = Cm(15)
        cp = cap_cell.paragraphs[0]
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cp.paragraph_format.space_before = Pt(3)
        cp.paragraph_format.space_after = Pt(3)
        cp.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        cr = cp.add_run(caption_text)
        cr.font.name = FONT
        cr.font.size = Pt(10)
        cr.italic = True
        cr.font.color.rgb = RGBColor(0, 0, 0)

        # beri jarak antargambar
        spacer = doc.add_paragraph()
        spacer.paragraph_format.space_after = Pt(6)
        spacer.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE


# --------------------------------------------------------------------------
# Dokumen
# --------------------------------------------------------------------------
doc = Document()
set_doc_defaults(doc)
fix_doc_defaults(doc)
style_heading(doc, 1, 14, space_before=18, space_after=8)
style_heading(doc, 2, 12, space_before=12, space_after=4)

sec = doc.sections[0]
sec.page_width = Cm(21)
sec.page_height = Cm(29.7)
sec.left_margin = Cm(2.5)
sec.right_margin = Cm(2.5)
sec.top_margin = Cm(2.5)
sec.bottom_margin = Cm(2.5)

# ---------------- COVER ----------------
for _ in range(2):
    doc.add_paragraph()

p = para(doc, "LAPORAN UJIAN TENGAH SEMESTER", bold=True, size=16,
         align=WD_ALIGN_PARAGRAPH.CENTER, indent=False)
para(doc, "MATA KULIAH PEMROGRAMAN .NET", bold=True, size=14,
     align=WD_ALIGN_PARAGRAPH.CENTER, indent=False)
para(doc, "IF133", bold=True, size=14,
     align=WD_ALIGN_PARAGRAPH.CENTER, indent=False)
doc.add_paragraph()

para(doc, "INVENTORY PRODUCT API", bold=True, size=13,
     align=WD_ALIGN_PARAGRAPH.CENTER, indent=False)

for _ in range(3):
    doc.add_paragraph()

para(doc, "Dosen Pengampu :", align=WD_ALIGN_PARAGRAPH.CENTER, indent=False)
para(doc, DOSEN, align=WD_ALIGN_PARAGRAPH.CENTER, indent=False)

for _ in range(3):
    doc.add_paragraph()

para(doc, "Disusun Oleh :", align=WD_ALIGN_PARAGRAPH.CENTER, indent=False)
para(doc, f"{NAMA.upper()} ({NIM})", bold=True,
     align=WD_ALIGN_PARAGRAPH.CENTER, indent=False)

for _ in range(4):
    doc.add_paragraph()

para(doc, "PROGRAM STUDI INFORMATIKA", bold=True,
     align=WD_ALIGN_PARAGRAPH.CENTER, indent=False)
para(doc, "FAKULTAS ILMU KOMPUTER", bold=True,
     align=WD_ALIGN_PARAGRAPH.CENTER, indent=False)
para(doc, "INSTITUT TEKNOLOGI TANGERANG SELATAN", bold=True,
     align=WD_ALIGN_PARAGRAPH.CENTER, indent=False)
para(doc, "2026", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, indent=False)

doc.add_page_break()

# ---------------- IDENTITAS ----------------
doc.add_heading("Identitas Mahasiswa", level=1)
make_table(doc,
    ["Keterangan", "Isi"],
    [
        ["Nama", NAMA],
        ["NIM", NIM],
        ["Program Studi", "Informatika"],
        ["Semester", "5 (Lima)"],
        ["Mata Kuliah", f"{MK} ({KODE_MK})"],
        ["Dosen Pengampu", DOSEN],
        ["Tanggal Ujian", "23 November 2026"],
        ["Nama Project", "UTS_IF133_1003240018"],
    ], widths=[5, 10])

# ---------------- RINGKASAN ----------------
doc.add_heading("Ringkasan Pekerjaan", level=1)
para(doc,
     "Laporan ini memuat hasil pengerjaan UTS mata kuliah Pemrograman .NET "
     "yang terdiri dari tiga bagian. Soal 1 membahas pemahaman konsep dan "
     "arsitektur ASP.NET Core Web API. Soal 2 berupa praktik membangun "
     "REST API inventori produk dengan Entity Framework Core dan SQLite. "
     "Soal 3 berupa studi kasus validasi, pemilihan status code, serta "
     "rancangan centralized error handling dan logging.")
para(doc,
     "Project yang dibangun bernama UTS_IF133_1003240018 dan menyediakan "
     "operasi CRUD lengkap pada endpoint /api/products. Seluruh endpoint "
     "diuji dengan 21 skenario yang mencakup kasus berhasil maupun gagal, "
     "dan semua skenario menghasilkan status code sesuai harapan.")

# ---------------- SOAL 1 ----------------
doc.add_page_break()
doc.add_heading("Soal 1 — Pemahaman Konsep dan Arsitektur", level=1)

doc.add_heading("1a. Fungsi dan hubungan antar komponen", level=2)

rich_para(doc, [
    ("Program.cs", True, False, True),
    (" adalah titik masuk aplikasi sekaligus tempat merakit seluruh "
     "komponen. Berkas ini mengumpulkan service ke dalam container "
     "Dependency Injection dan menyusun urutan middleware yang dilewati "
     "setiap request. Urutan middleware menentukan perilaku aplikasi, "
     "misalnya penanganan error harus dipasang paling depan agar dapat "
     "menangkap kesalahan dari middleware berikutnya, dan pemeriksaan "
     "otorisasi harus berjalan setelah autentikasi. Program.cs tidak "
     "menyimpan data dan tidak memproses request; tugasnya hanya "
     "konfigurasi dan perakitan.", False, False, False),
])

rich_para(doc, [
    ("appsettings.json", True, False, True),
    (" menyimpan konfigurasi yang dapat diubah tanpa mengompilasi ulang, "
     "seperti connection string dan level logging. Nilainya dibaca melalui "
     "configuration builder dan dapat ditimpa oleh berkas "
     "appsettings.{Environment}.json, environment variable, atau "
     "user-secrets. Karena itu connection string diletakkan di sini dan "
     "bukan ditulis langsung di dalam kode, supaya lingkungan development "
     "dan production dapat memakai database berbeda tanpa mengubah source "
     "code.", False, False, False),
])

rich_para(doc, [
    ("Controller", True, False, True),
    (" adalah lapisan yang menerima HTTP request dan mengembalikan HTTP "
     "response. Controller tidak mengakses database secara langsung, "
     "melainkan meminta data melalui DbContext lalu mengubah hasilnya "
     "menjadi DTO sebelum dikirim ke client. Atribut ApiController "
     "mengaktifkan pengikatan otomatis body JSON ke parameter dan "
     "validasi model, sedangkan atribut Route menentukan alamat endpoint. "
     "Controller juga bertanggung jawab memilih status code yang tepat.", False, False, False),
])

rich_para(doc, [
    ("DbContext", True, False, True),
    (" adalah jembatan antara kode C# dan database. Di dalamnya terdapat "
     "DbSet yang merepresentasikan tabel, konfigurasi model melalui "
     "OnModelCreating seperti panjang kolom dan unique index, serta "
     "penerjemahan query LINQ menjadi SQL. DbContext didaftarkan pada "
     "Program.cs dengan provider SQLite lalu disuntikkan ke controller "
     "melalui constructor. DbContext bersifat scoped, yaitu satu instance "
     "per request dan dibuang setelah request selesai.", False, False, False),
])

rich_para(doc, [
    ("Swagger/OpenAPI", True, False, True),
    (" menghasilkan dokumentasi endpoint yang dapat dicoba langsung dari "
     "browser. AddEndpointsApiExplorer mengumpulkan metadata endpoint, "
     "AddSwaggerGen menyusunnya menjadi dokumen OpenAPI, sedangkan "
     "UseSwagger dan UseSwaggerUI menyajikannya pada alamat /swagger. "
     "Swagger membaca atribut route dan tipe parameter dari controller "
     "sehingga dokumentasi otomatis sinkron dengan kode. Karena hanya "
     "didaftarkan pada environment Development, dokumentasi ini tidak "
     "aktif di production.", False, False, False),
])

para(doc,
     "Hubungan kelima komponen tersebut dalam satu alur dapat dijelaskan "
     "sebagai berikut: Program.cs merakit seluruh komponen dan menentukan "
     "urutan middleware, appsettings.json memasok nilai konfigurasi yang "
     "dipakai Program.cs, request masuk melewati middleware lalu "
     "diteruskan ke controller yang cocok dengan route, controller memakai "
     "DbContext untuk mengambil atau menyimpan data, hasilnya diubah "
     "menjadi DTO dan dikembalikan sebagai JSON, sementara Swagger "
     "mendokumentasikan seluruh proses itu dari sisi luar tanpa ikut "
     "mengeksekusi request.")

doc.add_heading("1b. Alur request–response GET /api/products/5", level=2)

para(doc,
     "Alur permintaan untuk mengambil satu produk dengan id 5 dapat "
     "diuraikan dalam tujuh tahap berikut.")

rich_para(doc, [("Tahap 1 — Client mengirim request. ", True, False, False),
                ("Client seperti Swagger, Postman, atau browser mengirim "
                 "GET http://localhost:5070/api/products/5 dengan header "
                 "Accept: application/json. Tidak ada body karena metode "
                 "GET tidak membawa payload.", False, False, False)])

rich_para(doc, [("Tahap 2 — Middleware berjalan berurutan. ", True, False, False),
                ("Request masuk ke pipeline. UseExceptionHandler membungkus "
                 "sisa pipeline agar exception apa pun dapat ditangkap. "
                 "UseHttpsRedirection memastikan koneksi memakai HTTPS. "
                 "Karena project ini tidak memakai autentikasi, request "
                 "langsung melewati UseAuthorization, lalu MapControllers "
                 "meneruskan request ke proses routing.", False, False, False)])

rich_para(doc, [("Tahap 3 — Routing mencocokkan endpoint. ", True, False, False),
                ("Routing memeriksa tabel route yang dibangun saat startup. "
                 "Template api/[controller] dengan nama class "
                 "ProductsController menghasilkan prefix api/Products. "
                 "Method GetProduct memakai atribut HttpGet(\"{id:int}\") "
                 "sehingga alamat /api/products/5 cocok dan nilai 5 diikat "
                 "ke parameter id. Constraint {id:int} memastikan hanya "
                 "angka yang diterima; bila client mengirim /api/products/abc, "
                 "route tidak cocok dan server langsung membalas 404 tanpa "
                 "menyentuh controller.", False, False, False)])

rich_para(doc, [("Tahap 4 — Model binding dan validasi. ", True, False, False),
                ("Atribut ApiController mengikat id menjadi 5. Karena id "
                 "merupakan parameter sederhana dari route, tidak ada "
                 "validasi body yang dijalankan. Bila terdapat body yang "
                 "tidak valid, ApiController akan otomatis membalas 400 "
                 "sebelum action dijalankan.", False, False, False)])

rich_para(doc, [("Tahap 5 — Controller memanggil DbContext. ", True, False, False),
                ("Action GetProduct dijalankan dengan DbContext yang "
                 "disuntikkan melalui constructor. Pemanggilan "
                 "FirstOrDefaultAsync membuat EF Core menerjemahkan "
                 "ekspresi LINQ menjadi SQL berikut.", False, False, False)])

code_block(doc, [
    'SELECT "p"."Id", "p"."Code", "p"."Name", "p"."Price",',
    '       "p"."Stock", "p"."IsActive"',
    'FROM "Products" AS "p"',
    'WHERE "p"."Id" = @__id_0',
    'LIMIT 1',
])

para(doc,
     "Karena memakai await, thread tidak diblokir selama query berjalan; "
     "thread dikembalikan ke pool sampai hasil dari database siap. "
     "Pemakaian AsNoTracking mematikan change tracker karena data hanya "
     "dibaca sehingga lebih hemat memori.")

rich_para(doc, [("Tahap 6a — Jalur 200 OK. ", True, False, False),
                ("Bila baris dengan Id 5 ditemukan, EF Core memetakan kolom "
                 "hasil query ke objek Product. Controller mengubah entity "
                 "tersebut menjadi ProductReadDto lalu memanggil Ok(dto). "
                 "Hasilnya status 200 OK dengan body JSON berikut.", False, False, False)])

code_block(doc, [
    '{',
    '  "id": 5,',
    '  "code": "PRD-005",',
    '  "name": "Keyboard Mechanical",',
    '  "price": 750000,',
    '  "stock": 12,',
    '  "isActive": true',
    '}',
])

para(doc,
     "Serialisasi JSON dilakukan oleh System.Text.Json yang sudah "
     "terpasang pada ASP.NET Core. Karena response memakai DTO, hanya "
     "field yang ada pada DTO yang dikirim keluar.")

rich_para(doc, [("Tahap 6b — Jalur 404 Not Found. ", True, False, False),
                ("Bila query mengembalikan nilai null karena tidak ada baris "
                 "dengan Id 5, controller mencatat peringatan ke log lalu "
                 "mengembalikan NotFound berisi ProblemDetails. Hasilnya "
                 "status 404 Not Found dengan body berikut.", False, False, False)])

code_block(doc, [
    '{',
    '  "title": "Product not found",',
    '  "status": 404,',
    '  "detail": "Produk dengan id 5 tidak ditemukan."',
    '}',
])

para(doc,
     "Status 404 dipilih dan bukan 500 karena request client sebenarnya "
     "valid dan server berjalan normal; yang tidak ada hanyalah resource "
     "yang diminta. Status 500 hanya dipakai bila terjadi kesalahan di "
     "sisi server, misalnya database tidak dapat dihubungi.")

rich_para(doc, [("Tahap 7 — Response kembali ke client. ", True, False, False),
                ("Response melewati middleware dalam urutan terbalik lalu "
                 "dikirim ke client. DbContext kemudian dibuang bersama "
                 "berakhirnya scope request.", False, False, False)])

# ---------------- SOAL 2 ----------------
doc.add_page_break()
doc.add_heading("Soal 2 — Praktik Implementasi Backend", level=1)

doc.add_heading("Struktur project", level=2)
para(doc,
     "Project dibuat dengan nama UTS_IF133_1003240018 sesuai ketentuan soal, "
     "memakai ASP.NET Core Web API pada .NET 8 dengan pola yang sama seperti "
     "hands-on pertemuan sebelumnya.")

code_block(doc, [
    "UTS_IF133_1003240018/",
    "├── UTS_IF133_1003240018.sln",
    "├── global.json",
    "├── README.md",
    "├── screenshots/",
    "└── src/UTS_IF133_1003240018/",
    "    ├── Program.cs",
    "    ├── appsettings.json",
    "    ├── Entities/Product.cs",
    "    ├── Data/",
    "    │   ├── AppDbContext.cs",
    "    │   └── Migrations/",
    "    ├── Dtos/",
    "    │   ├── CreateProductDto.cs",
    "    │   ├── UpdateProductDto.cs",
    "    │   └── ProductReadDto.cs",
    "    └── Controllers/",
    "        ├── ProductsController.cs",
    "        └── DiagnosticsController.cs",
])

doc.add_heading("Entity dan konfigurasi database", level=2)
para(doc,
     "Entity Product memiliki enam properti sesuai permintaan soal. "
     "Konfigurasi tambahan diberikan pada OnModelCreating untuk memastikan "
     "aturan panjang kolom dan keunikan Code juga ditegakkan di level "
     "database, bukan hanya di aplikasi.")

make_table(doc,
    ["Properti", "Tipe", "Aturan"],
    [
        ["Id", "int", "primary key, auto increment"],
        ["Code", "string", "wajib, maksimal 20 karakter, unique index"],
        ["Name", "string", "wajib, maksimal 100 karakter"],
        ["Price", "decimal", "lebih besar dari 0, decimal(18,2)"],
        ["Stock", "int", "tidak boleh negatif"],
        ["IsActive", "bool", "default true"],
    ], widths=[3.5, 3, 8.5])
caption(doc, "Tabel 1. Properti entity Product dan aturannya")

doc.add_heading("Migration dan database", level=2)
para(doc,
     "Migration dibuat dari dalam folder project agar tool dapat menemukan "
     "DbContext, kemudian diterapkan ke database SQLite. Nama database "
     "adalah uts-if133.db dan pathnya dijadikan absolut terhadap "
     "ContentRootPath supaya tetap menunjuk berkas yang sama walaupun "
     "perintah dijalankan dari folder berbeda.")

code_block(doc, [
    "cd src/UTS_IF133_1003240018",
    "dotnet ef migrations add InitialCreate -o Data/Migrations",
    "dotnet ef database update",
])

para(doc, "Hasil perintah migrations list:")
code_block(doc, ["20261121234933_InitialCreate"])

para(doc, "Skema tabel yang terbentuk di SQLite:")
code_block(doc, [
    'CREATE TABLE "Products" (',
    '    "Id" INTEGER NOT NULL CONSTRAINT "PK_Products" PRIMARY KEY AUTOINCREMENT,',
    '    "Code" TEXT NOT NULL,',
    '    "Name" TEXT NOT NULL,',
    '    "Price" decimal(18,2) NOT NULL,',
    '    "Stock" INTEGER NOT NULL,',
    '    "IsActive" INTEGER NOT NULL',
    ');',
    'CREATE UNIQUE INDEX "IX_Products_Code" ON "Products" ("Code");',
])

doc.add_heading("Endpoint yang tersedia", level=2)
make_table(doc,
    ["Method", "Route", "Sukses", "Gagal", "Keterangan"],
    [
        ["GET", "/api/products", "200", "-", "seluruh produk, urut Id"],
        ["GET", "/api/products/{id}", "200", "404", "satu produk"],
        ["POST", "/api/products", "201", "400, 409", "tambah produk + header Location"],
        ["PUT", "/api/products/{id}", "204", "400, 404, 409", "ubah produk"],
        ["DELETE", "/api/products/{id}", "204", "404", "hapus produk"],
        ["GET", "/api/diagnostics/error", "500", "-", "simulasi exception"],
    ], widths=[2, 4.2, 1.6, 2.4, 5.8])
caption(doc, "Tabel 2. Daftar endpoint dan status code yang dikembalikan")

doc.add_heading("Penerapan async/await", level=2)
para(doc,
     "Seluruh akses database memakai operasi asynchronous agar thread server "
     "tidak tertahan selama menunggu input/output. Pemetaan operasi yang "
     "dipakai adalah sebagai berikut.")

make_table(doc,
    ["Operasi", "Method async yang dipakai"],
    [
        ["Membaca daftar produk", "ToListAsync()"],
        ["Membaca satu produk", "FirstOrDefaultAsync()"],
        ["Memeriksa keberadaan Code", "AnyAsync()"],
        ["Menyimpan perubahan", "SaveChangesAsync()"],
    ], widths=[7, 8])
caption(doc, "Tabel 3. Pemetaan operasi database ke method asynchronous")

doc.add_heading("Skenario pengujian", level=2)
para(doc,
     "Pengujian dilakukan terhadap 21 skenario yang mencakup kasus berhasil "
     "dan kasus gagal pada setiap endpoint. Skrip pengujian disertakan pada "
     "berkas test-endpoints.sh sehingga hasilnya dapat diulang.")

make_table(doc,
    ["No", "Skenario", "Status diharapkan", "Hasil"],
    [
        ["1", "GET daftar saat database kosong", "200", "Sesuai"],
        ["2", "POST data contoh soal", "201", "Sesuai"],
        ["3", "POST dengan Code duplikat", "409", "Sesuai"],
        ["4", "POST seluruh field tidak valid", "400", "Sesuai"],
        ["5", "POST Code lebih dari 20 karakter", "400", "Sesuai"],
        ["6", "POST Code mengandung spasi", "400", "Sesuai"],
        ["7", "POST produk kedua", "201", "Sesuai"],
        ["8", "POST produk dengan stock 0 dan nonaktif", "201", "Sesuai"],
        ["9", "GET produk yang ada", "200", "Sesuai"],
        ["10", "GET id 100 (tidak ada)", "404", "Sesuai"],
        ["11", "GET daftar berisi tiga produk", "200", "Sesuai"],
        ["12", "PUT produk yang ada", "204", "Sesuai"],
        ["13", "PUT id tidak ada", "404", "Sesuai"],
        ["14", "PUT memakai Code milik produk lain", "409", "Sesuai"],
        ["15", "PUT payload tidak valid", "400", "Sesuai"],
        ["16", "DELETE produk yang ada", "204", "Sesuai"],
        ["17", "DELETE produk yang sama dua kali", "404", "Sesuai"],
        ["18", "GET produk yang sudah dihapus", "404", "Sesuai"],
        ["19", "GET endpoint simulasi error", "500", "Sesuai"],
        ["20", "Body 500 diperiksa", "tanpa stack trace", "Sesuai"],
        ["21", "GET daftar kondisi akhir", "200", "Sesuai"],
    ], widths=[1.2, 7.2, 3.6, 3])
caption(doc, "Tabel 4. Hasil pengujian 21 skenario")

# ---------------- SOAL 3 ----------------
doc.add_page_break()
doc.add_heading("Soal 3 — Validasi, Status Code, dan Error Handling", level=1)

doc.add_heading("3a. CreateProductDto dan aturan validasi", level=2)
para(doc,
     "DTO dipisahkan dari entity karena tiga alasan. Pertama, entity "
     "mengikuti bentuk tabel sedangkan kontrak API harus dapat berubah "
     "sendiri. Kedua, properti internal seperti Id tidak boleh dapat diisi "
     "client saat pembuatan data. Ketiga, aturan validasi cukup menempel "
     "pada DTO sehingga entity tetap bersih. Berikut bentuk class yang "
     "dipakai pada project ini.")

code_block(doc, [
    "public class CreateProductDto",
    "{",
    '    [Required(ErrorMessage = "Code wajib diisi.")]',
    '    [StringLength(20, ErrorMessage = "Code maksimal 20 karakter.")]',
    "    [RegularExpression(\"^[A-Za-z0-9-]+$\",",
    '        ErrorMessage = "Code hanya boleh huruf, angka, dan tanda hubung.")]',
    "    public string Code { get; set; } = string.Empty;",
    "",
    '    [Required(ErrorMessage = "Name wajib diisi.")]',
    '    [StringLength(100, ErrorMessage = "Name maksimal 100 karakter.")]',
    "    public string Name { get; set; } = string.Empty;",
    "",
    "    [Range(0.01, 1000000000,",
    '        ErrorMessage = "Price harus lebih besar dari 0.")]',
    "    public decimal Price { get; set; }",
    "",
    '    [Range(0, int.MaxValue, ErrorMessage = "Stock tidak boleh negatif.")]',
    "    public int Stock { get; set; }",
    "",
    "    public bool IsActive { get; set; } = true;",
    "}",
])

para(doc, "Alasan pemilihan setiap atribut dijelaskan pada tabel berikut.")
make_table(doc,
    ["Aturan soal", "Atribut", "Alasan"],
    [
        ["Code wajib", "Required", "Menolak null dan string kosong termasuk spasi saja"],
        ["Code maksimal 20 karakter", "StringLength(20)", "Sesuai HasMaxLength(20) pada konfigurasi kolom"],
        ["Name wajib", "Required", "Sama seperti Code"],
        ["Name maksimal 100 karakter", "StringLength(100)", "Sesuai HasMaxLength(100) pada konfigurasi kolom"],
        ["Price lebih dari 0", "Range(0.01, ...)", "Decimal tidak mendukung batas eksklusif 0, sehingga dipakai 0.01"],
        ["Stock tidak negatif", "Range(0, int.MaxValue)", "Batas bawah 0 sudah menutup seluruh nilai negatif"],
    ], widths=[4.2, 3.8, 7])
caption(doc, "Tabel 5. Aturan validasi dan atribut yang dipakai")

para(doc,
     "Tambahan RegularExpression pada Code tidak diminta soal, tetapi "
     "dipakai agar kode produk seragam dan tidak mengandung spasi. Selain "
     "validasi di DTO, entity juga memiliki unique index pada kolom Code "
     "sebagai pengaman terakhir di level database. Bila payload tidak lolos "
     "validasi, atribut ApiController otomatis membalas 400 berisi daftar "
     "kesalahan per field tanpa perlu pemeriksaan manual di controller.")

doc.add_heading("3b. Status code untuk lima skenario", level=2)
make_table(doc,
    ["Skenario", "Status", "Alasan"],
    [
        ["Payload tidak valid", "400 Bad Request",
         "Request sudah dipahami server tetapi isinya melanggar aturan validasi. "
         "Kesalahan ada di sisi client, bukan server."],
        ["Produk tidak ditemukan", "404 Not Found",
         "Request valid dan server sehat, hanya resource dengan id tersebut "
         "memang tidak ada. Bukan 400 karena format benar, bukan 500 karena "
         "tidak ada kesalahan server."],
        ["Create berhasil", "201 Created",
         "Menandakan sukses sekaligus mewajibkan header Location berisi alamat "
         "resource baru. Nilai ini dihasilkan oleh CreatedAtAction."],
        ["Code produk duplikat", "409 Conflict",
         "Format request benar, tetapi bertentangan dengan keadaan data yang "
         "sudah ada karena unique constraint pada Code."],
        ["Exception internal", "500 Internal Server Error",
         "Kegagalan berada di sisi server. Detail asli hanya masuk log, client "
         "menerima pesan umum tanpa stack trace."],
    ], widths=[3.6, 3.4, 8])
caption(doc, "Tabel 6. Pemilihan status code beserta alasannya")

para(doc,
     "Sebagai catatan tambahan, status 401 Unauthorized dipakai bila "
     "identitas belum terbukti dan 403 Forbidden dipakai bila identitas "
     "sudah terbukti tetapi tidak memiliki hak. Keduanya tidak termasuk "
     "dalam lima skenario soal karena project UTS ini tidak memakai "
     "autentikasi.")

doc.add_heading("3c. Centralized error handling dan logging yang aman", level=2)
para(doc,
     "Prinsip yang dipakai adalah satu tempat menangkap kesalahan dengan dua "
     "audiens berbeda. Server membutuhkan informasi selengkap mungkin untuk "
     "diagnosis, sedangkan client hanya membutuhkan pesan yang dapat "
     "ditindaklanjuti. Keduanya tidak boleh menerima informasi yang sama.")

rich_para(doc, [("Penanganan terpusat pada Program.cs. ", True, False, False),
                ("UseExceptionHandler dipasang paling depan pada pipeline "
                 "sehingga membungkus seluruh middleware dan controller di "
                 "belakangnya. Setiap exception yang tidak tertangani akan "
                 "berhenti di sini, dicatat lengkap ke log, lalu diganti "
                 "response yang aman. Karena penanganannya berada di satu "
                 "tempat, bentuk response kesalahan tidak akan berbeda-beda "
                 "antar endpoint.", False, False, False)])

code_block(doc, [
    "app.UseExceptionHandler(errorApp =>",
    "{",
    "    errorApp.Run(async context =>",
    "    {",
    "        var logger = context.RequestServices",
    "            .GetRequiredService<ILogger<Program>>();",
    "        var exception = context.Features",
    "            .Get<IExceptionHandlerFeature>()?.Error;",
    "",
    '        logger.LogError(exception, "Unhandled exception pada {Path}",',
    "            context.Request.Path);",
    "",
    "        context.Response.StatusCode =",
    "            StatusCodes.Status500InternalServerError;",
    '        context.Response.ContentType = "application/problem+json";',
    "",
    "        await Results.Problem(",
    '            title: "Internal Server Error",',
    '            detail: "Terjadi kesalahan pada server.",',
    "            statusCode: StatusCodes.Status500InternalServerError)",
    "            .ExecuteAsync(context);",
    "    });",
    "});",
])

rich_para(doc, [("Kesalahan yang sudah diperkirakan tidak dilempar sebagai exception. ", True, False, False),
                ("Kasus 400, 404, dan 409 bukan kesalahan tak terduga sehingga "
                 "ditangani langsung di controller melalui return value. Yang "
                 "masuk ke UseExceptionHandler hanya kegagalan yang benar-benar "
                 "tidak terduga seperti database mati atau bug null reference. "
                 "Pemisahan ini penting agar log kesalahan tidak penuh oleh hal "
                 "yang sebenarnya normal.", False, False, False)])

rich_para(doc, [("Bentuk respons yang konsisten. ", True, False, False),
                ("Seluruh kesalahan memakai format ProblemDetails mengikuti "
                 "RFC 7807 sehingga client cukup memeriksa properti status dan "
                 "errors tanpa perlu menebak bentuk body tiap endpoint. "
                 "Contoh untuk kasus produk tidak ditemukan dan kasus validasi "
                 "adalah sebagai berikut.", False, False, False)])

code_block(doc, [
    '{ "title": "Product not found", "status": 404,',
    '  "detail": "Produk dengan id 5 tidak ditemukan." }',
    "",
    '{ "type": ".../rfc9110#section-15.5.1",',
    '  "title": "One or more validation errors occurred.",',
    '  "status": 400,',
    '  "errors": {',
    '    "Code":  ["Code wajib diisi."],',
    '    "Price": ["Price harus lebih besar dari 0."],',
    '    "Stock": ["Stock tidak boleh negatif."] } }',
])

rich_para(doc, [("Logging yang berguna untuk diagnosis. ", True, False, False),
                ("LogInformation dipakai untuk kejadian normal yang penting "
                 "seperti produk dibuat, diperbarui, atau dihapus beserta id "
                 "dan kodenya. LogWarning dipakai untuk kejadian yang wajar "
                 "tetapi perlu diperhatikan, misalnya permintaan ke id yang "
                 "tidak ada atau percobaan membuat Code duplikat. LogError "
                 "dipakai untuk exception tak terduga dan selalu menyertakan "
                 "objek exception beserta path request. Log memakai structured "
                 "logging dengan placeholder bernama sehingga dapat dicari dan "
                 "difilter, bukan penggabungan string.", False, False, False)])

rich_para(doc, [("Informasi yang tidak boleh diekspos ke client. ", True, False, False),
                ("Beberapa hal berikut harus tetap berada di sisi server saja.", False, False, False)])

for item in [
    "Stack trace serta nama class dan method internal, karena menunjukkan "
    "struktur kode dan memudahkan penyerang mencari celah.",
    "Connection string dan kredensial database.",
    "Nama tabel, kolom, dan query SQL yang gagal, karena membocorkan skema database.",
    "Pesan exception mentah dari provider database, misalnya keterangan unique "
    "constraint yang menyebut nama tabel secara persis.",
    "Path berkas pada server yang menunjukkan lokasi source code.",
    "Token, password, dan API key, termasuk di dalam berkas log.",
]:
    bullet(doc, item)

para(doc,
     "Cara memisahkan keduanya adalah client hanya menerima properti title, "
     "status, dan detail yang sudah ditulis ulang dalam bahasa manusia, "
     "sedangkan stack trace utuh hanya ditulis ke log server yang aksesnya "
     "terbatas pada administrator.")

# ---------------- BUKTI ----------------
doc.add_page_break()
doc.add_heading("Bukti Pengujian", level=1)
para(doc,
     "Bagian ini memuat tangkapan layar hasil pengujian seluruh endpoint "
     "melalui Swagger serta bukti migration dan isi database. Setiap gambar "
     "disertai keterangan singkat mengenai skenario yang diuji dan status "
     "code yang dihasilkan.")

for i, (fn, title) in enumerate(SHOTS, start=1):
    add_image_or_placeholder(doc, fn, title, i)

# ---------------- KESIMPULAN ----------------
doc.add_page_break()
doc.add_heading("Kesimpulan", level=1)
para(doc,
     "Project UTS_IF133_1003240018 berhasil dibangun dan dijalankan dengan "
     "ASP.NET Core Web API, Entity Framework Core, dan SQLite. Seluruh "
     "endpoint CRUD pada /api/products berfungsi sesuai ketentuan soal, "
     "menggunakan operasi asynchronous pada setiap akses database, dan "
     "mengembalikan status code yang semantik untuk tiap kondisi.")
para(doc,
     "Dari sisi kualitas API, pemisahan DTO dari entity membuat kontrak API "
     "tidak ikut berubah ketika model database berubah. Validasi dengan "
     "DataAnnotations menolak input tidak valid sebelum menyentuh database, "
     "sedangkan unique index pada kolom Code menjaga keunikan kode produk di "
     "level basis data. Centralized error handling memastikan seluruh "
     "kesalahan memiliki bentuk respons yang sama serta tidak membocorkan "
     "detail internal ke client.")
para(doc,
     "Pengujian dilakukan terhadap 21 skenario yang mencakup kasus berhasil "
     "dan kasus gagal, dan seluruhnya menghasilkan status code sesuai "
     "harapan. Dengan demikian project ini memenuhi ketentuan Soal 2 dan "
     "Soal 3 pada UTS mata kuliah Pemrograman .NET.")

# ---------------- KENDALA ---------------- 
doc.add_page_break()
doc.add_heading("Kendala dan Solusi", level=1)

para(doc,
     "Bagian ini mencatat masalah yang benar-benar muncul selama pengerjaan "
     "beserta cara mengatasinya, sebagai bagian dari dokumentasi proses.")

rich_para(doc, [("1. Seluruh endpoint tampil sebagai 200 di Swagger. ", True, False, False),
                ("Pada awalnya Swagger UI menampilkan semua endpoint hanya "
                 "memiliki respons 200, walaupun kode sudah mengembalikan "
                 "201, 204, 400, 404, dan 409. Penyebabnya Swagger hanya "
                 "mendokumentasikan status code yang dideklarasikan secara "
                 "eksplisit. Solusinya menambahkan atribut "
                 "ProducesResponseType pada setiap action dan atribut "
                 "Produces(\"application/json\") pada level controller. "
                 "Setelah itu Swagger menampilkan 201, 400, dan 409 untuk "
                 "POST; 204, 400, 404, dan 409 untuk PUT; serta 204 dan 404 "
                 "untuk DELETE.", False, False, False)])

rich_para(doc, [("2. Pengujian gagal saat dijalankan dua kali. ", True, False, False),
                ("Skrip pengujian sempat melaporkan kegagalan pada skenario "
                 "POST valid karena respons yang diterima 409, padahal "
                 "harusnya 201. Setelah ditelusuri, data PRD-001 dari "
                 "percobaan sebelumnya masih ada di database sehingga unique "
                 "constraint bekerja sebagaimana mestinya. Bukan bug "
                 "aplikasi. Solusinya menghapus berkas basis data lalu "
                 "menjalankan ulang migration sebelum mengulang pengujian, "
                 "sehingga setiap putaran pengujian dimulai dari keadaan "
                 "kosong.", False, False, False)])

rich_para(doc, [("3. Perintah dotnet ef gagal karena berkas terkunci. ", True, False, False),
                ("Saat mengambil bukti migration, perintah dotnet ef "
                 "migrations list berhenti dengan pesan \"Build failed. Use "
                 "dotnet build to see the errors.\" Pesan MSBuild MSB3026 "
                 "dan MSB3027 menunjukkan berkas IF133 exe tidak dapat "
                 "ditimpa karena masih dipakai proses aplikasi yang berjalan "
                 "di terminal lain. Solusinya menjalankan perintah yang sama "
                 "dengan opsi --no-build, sehingga EF Core memakai assembly "
                 "yang sudah ada di folder bin tanpa membangun ulang. "
                 "Migration 20261121234933_InitialCreate berhasil "
                 "ditampilkan tanpa menghentikan server yang sedang dipakai "
                 "untuk pengujian endpoint.", False, False, False)])

rich_para(doc, [("4. Nomor Id tidak berurutan. ", True, False, False),
                ("Setelah satu produk dihapus, produk berikutnya mendapat Id "
                 "yang melompat karena kolom Id memakai AUTOINCREMENT. Hal "
                 "ini bukan kesalahan program, melainkan perilaku SQLite "
                 "yang menjaga agar Id yang pernah dipakai tidak digunakan "
                 "ulang. Pengujian GET dengan Id yang tidak ada tetap "
                 "menghasilkan 404 sesuai rancangan.", False, False, False)])

rich_para(doc, [("5. Penyesuaian dokumentasi dengan bukti. ", True, False, False),
                ("Beberapa nilai pada dokumen awal berbeda dengan hasil "
                 "pengujian yang sebenarnya, misalnya Id yang dipakai untuk "
                 "menguji respons 404. Dokumen disesuaikan dengan bukti "
                 "screenshot yang diambil, bukan sebaliknya, agar laporan "
                 "menggambarkan apa yang benar-benar dijalankan.", False, False, False)])

# ---------------- LAMPIRAN ----------------
doc.add_page_break()
doc.add_heading("Lampiran — Perintah yang Digunakan", level=1)

para(doc, "Membangun dan menjalankan project:")
code_block(doc, [
    "dotnet build",
    "cd src/UTS_IF133_1003240018",
    "dotnet ef database update",
    "cd ../..",
    "dotnet run --project src/UTS_IF133_1003240018/UTS_IF133_1003240018.csproj",
])

para(doc, "Memeriksa migration dan isi database:")
code_block(doc, [
    "cd src/UTS_IF133_1003240018",
    "dotnet ef migrations list",
    'sqlite3 uts-if133.db ".tables"',
    'sqlite3 uts-if133.db "SELECT * FROM Products;"',
])

para(doc, "Menjalankan seluruh skenario pengujian:")
code_block(doc, ["./test-endpoints.sh"])

doc.save(OUT_DOCX)
print("DOCX dibuat:", OUT_DOCX)

ada = sum(1 for fn, _ in SHOTS if os.path.exists(os.path.join(SHOT_DIR, fn)))
print(f"Screenshot terpasang: {ada} dari {len(SHOTS)}")
if ada < len(SHOTS):
    print("Yang belum ada akan tampil sebagai kotak placeholder abu-abu.")
