"""
Konversi LANGKAH-SCREENSHOT.md -> HTML -> PDF (via LibreOffice).

Jalankan ulang setiap kali panduan markdown diubah:
    py -3.13 buat-panduan.py

Butuh: markdown sederhana (heading, tabel, blok kode, bullet, bold, inline code).
"""

import html
import os
import re
import subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "LANGKAH-SCREENSHOT.md")
DST_HTML = os.path.join(BASE, "LANGKAH-SCREENSHOT.html")
DST_PDF = os.path.join(BASE, "LANGKAH-SCREENSHOT.pdf")
SOFFICE = r"C:\Program Files\LibreOffice\program\soffice.exe"


def inline(text):
    """Escape HTML lalu terapkan **bold** dan `code`, termasuk di dalam heading."""
    t = html.escape(text)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return t


def md_to_html(md):
    out = []
    in_code = False
    in_table = False

    def close_table():
        nonlocal in_table
        if in_table:
            out.append("</table>")
            in_table = False

    for line in md.split("\n"):
        # blok kode
        if line.startswith("```"):
            if in_code:
                out.append("</pre>")
                in_code = False
            else:
                close_table()
                out.append("<pre>")
                in_code = True
            continue
        if in_code:
            out.append(html.escape(line))
            continue

        # tabel
        if line.startswith("| "):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                continue
            if not in_table:
                out.append("<table>")
                in_table = True
                out.append("<tr>" + "".join(f"<th>{inline(c)}</th>" for c in cells) + "</tr>")
            else:
                out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>")
            continue
        close_table()

        # heading (dengan inline formatting juga, supaya backtick tidak mentah)
        if line.startswith("### "):
            out.append(f"<h3>{inline(line[4:])}</h3>")
        elif line.startswith("## "):
            out.append(f"<h2>{inline(line[3:])}</h2>")
        elif line.startswith("# "):
            out.append(f"<h1>{inline(line[2:])}</h1>")
        elif line.strip() == "---":
            out.append("<hr>")
        elif line.strip() == "":
            out.append("<p></p>")
        elif line.lstrip().startswith("- "):
            depth = (len(line) - len(line.lstrip())) // 2
            out.append(f'<p class="b{depth}">&bull;&nbsp;{inline(line.lstrip()[2:])}</p>')
        else:
            out.append(f"<p>{inline(line)}</p>")

    close_table()
    if in_code:
        out.append("</pre>")
    return "\n".join(out)


CSS = """
@page { size: A4; margin: 1.8cm 1.9cm; }
body { font-family: "Times New Roman", serif; font-size: 11pt; line-height: 1.35; }
h1 { font-size: 15pt; margin: 0 0 8px 0; }
h2 { font-size: 13pt; border-bottom: 1px solid #888; padding-bottom: 3px; margin-top: 14px; }
h3 { font-size: 12pt; margin-top: 12px; }
pre { font-family: Consolas, monospace; font-size: 8.5pt; background: #f4f4f4;
      padding: 6px 8px; border: 1px solid #ddd; white-space: pre-wrap; page-break-inside: avoid; }
code { font-family: Consolas, monospace; font-size: 9.5pt; background: #f0f0f0; }
table { border-collapse: collapse; width: 100%; font-size: 9.5pt; margin: 6px 0;
        page-break-inside: avoid; }
th, td { border: 1px solid #333; padding: 3px 5px; vertical-align: top; }
th { background: #dfe7f5; }
hr { border: none; border-top: 1px solid #bbb; margin: 10px 0; }
p { margin: 3px 0; }
p.b0 { margin-left: 0; }
p.b1 { margin-left: 14px; }
p.b2 { margin-left: 30px; }
"""


def main():
    md = open(SRC, encoding="utf-8").read()
    body = md_to_html(md)
    doc = (
        '<!DOCTYPE html><html><head><meta charset="utf-8">'
        f"<style>{CSS}</style></head><body>{body}</body></html>"
    )
    open(DST_HTML, "w", encoding="utf-8").write(doc)
    print("HTML dibuat:", DST_HTML)

    if not os.path.exists(SOFFICE):
        print("LibreOffice tidak ditemukan, PDF tidak dibuat:", SOFFICE)
        return

    subprocess.run(
        [SOFFICE, "--headless", "--convert-to", "pdf", "--outdir", BASE, DST_HTML],
        check=True, capture_output=True, text=True,
    )
    print("PDF dibuat:", DST_PDF)

    # verifikasi tidak ada tag HTML yang lolos sebagai teks
    try:
        import pymupdf

        d = pymupdf.open(DST_PDF)
        leaked = 0
        for pg in d:
            for b in pg.get_text("dict")["blocks"]:
                for ln in b.get("lines", []):
                    for sp in ln.get("spans", []):
                        s = sp["text"].strip()
                        if s.startswith("<") and s.endswith(">"):
                            leaked += 1
        print(f"Jumlah halaman: {len(d)} | tag HTML bocor: {leaked}")
    except ImportError:
        print("pymupdf tidak tersedia, verifikasi dilewati")


if __name__ == "__main__":
    main()
