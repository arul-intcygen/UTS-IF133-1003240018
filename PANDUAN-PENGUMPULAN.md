# Panduan Pengumpulan UTS IF133

Dokumen ini berisi langkah yang harus dikerjakan sendiri oleh mahasiswa
setelah source code dan laporan siap.

---

## 1. Ambil screenshot bukti pengujian

Bukti screenshot harus dari tangan mahasiswa sendiri karena dosen dapat
meminta demo ulang. Simpan di folder `screenshots/` dengan nama berkas persis
seperti daftar berikut, supaya laporan otomatis memasukkannya.

| No | Nama berkas | Yang harus terlihat |
|---|---|---|
| 1 | `01_swagger_home.png` | Halaman Swagger, semua endpoint tampil |
| 2 | `02_get_list_kosong.png` | GET /api/products → 200, body `[]` |
| 3 | `03_post_201.png` | POST data contoh soal → 201 + header Location |
| 4 | `04_post_409.png` | POST Code duplikat → 409 |
| 5 | `05_post_400.png` | POST field kosong → 400 + daftar errors |
| 6 | `06_get_200.png` | GET /api/products/1 → 200 |
| 7 | `07_get_404.png` | GET /api/products/9999 → 404 |
| 8 | `08_put_204.png` | PUT berhasil → 204 |
| 9 | `09_delete_204.png` | DELETE berhasil → 204 |
| 10 | `10_delete_404.png` | DELETE ulang → 404 |
| 11 | `11_error_500.png` | GET /api/diagnostics/error → 500 tanpa stack trace |
| 12 | `12_log_server.png` | Terminal server: stack trace lengkap ada di sini |
| 13 | `13_migration.png` | Output `dotnet ef migrations list` |
| 14 | `14_db_tabel.png` | Isi tabel Products di DB Browser for SQLite |

**Cara mengambil:** jalankan aplikasi, buka Swagger, kerjakan tiap skenario,
lalu tekan `Win + Shift + S` untuk memotong area yang relevan dan simpan
dengan nama di atas. Pastikan **status code terlihat jelas** di setiap gambar.

---

## 2. Bangun ulang laporan dengan screenshot

Setelah semua screenshot ada:

```bash
cd "Hands On/UTS/UTS_IF133_1003240018"
py -3.13 buat-laporan.py
"C:/Program Files/LibreOffice/program/soffice.exe" --headless --convert-to pdf --outdir . "UTS_IF133_1003240018_SahrulSolihin.docx"
```

Keluaran yang diharapkan:

```
Screenshot terpasang: 14 dari 14
```

Kalau masih kurang dari 14, periksa kembali nama berkasnya — harus sama
persis termasuk huruf kecil dan tanda garis bawah.

---

## 3. Unggah source code ke GitHub

Instruksi di LMS menyebut kode diunggah ke repository GitHub. `gh` CLI tidak
terpasang di mesin ini, jadi langkah berikut memakai `git` biasa dan membuat
repository lewat browser.

### 3.1 Buat repository kosong

1. Buka https://github.com/new
2. Repository name: `UTS-IF133-1003240018`
3. Pilih **Public** (supaya dosen bisa membuka tanpa login) atau **Private**
   kalau dosen meminta tautan dan sudah diberi akses
4. **Jangan** centang "Add a README file", "Add .gitignore", atau "Choose a
   license" — repository harus benar-benar kosong
5. Klik **Create repository**, lalu salin URL yang muncul, misalnya
   `https://github.com/arul-intcygen/UTS-IF133-1003240018.git`

### 3.2 Inisialisasi dan push

Jalankan dari folder project (bukan dari folder `src`):

```bash
cd "C:/Users/Administrator/Downloads/Semester 5/Permograman .NET/Hands On/UTS/UTS_IF133_1003240018"
git init
git add .
git commit -m "UTS IF133 1003240018 - Inventory Product API"
git branch -M main
git remote add origin https://github.com/arul-intcygen/UTS-IF133-1003240018.git
git push -u origin main
```

**Yang diharapkan:** `git push` meminta kredensial. GitHub tidak menerima
password biasa; pakai Personal Access Token (Settings → Developer settings →
Personal access tokens → Tokens (classic) → Generate new token, centang
scope `repo`). Saat diminta password, tempel token tersebut.

### 3.3 Periksa sebelum push

Pastikan tidak ada berkas yang tidak seharusnya ikut:

```bash
git status --short
git ls-files | grep -E "bin/|obj/|\.db$"
```

`.gitignore` sudah mengecualikan `bin/`, `obj/`, dan `*-wal`/`*-shm`, tetapi
berkas `uts-if133.db` **sengaja ikut** karena soal meminta bukti hasil
migration. Kalau tidak ingin menyertakan database, tambahkan
`*.db` ke `.gitignore` lalu `git rm --cached src/UTS_IF133_1003240018/uts-if133.db`.

### 3.4 Verifikasi hasil push

```bash
git log --oneline
git remote -v
```

Buka URL repository di browser dan pastikan berkas `Program.cs`,
`ProductsController.cs`, `README.md`, dan `JAWABAN-UTS.md` terlihat.
Kalau repository Public, buka di jendela incognito untuk memastikan dosen
bisa mengakses tanpa login.

---

## 4. Siapkan berkas ZIP

Soal meminta satu berkas ZIP source code. Nama berkas:
`UTS_IF133_1003240018_SahrulSolihin.zip`

```bash
cd "C:/Users/Administrator/Downloads/Semester 5/Permograman .NET/Hands On/UTS"
tar.exe -a -c -f "UTS_IF133_1003240018_SahrulSolihin.zip" \
  --exclude "bin" --exclude "obj" --exclude ".git" \
  "UTS_IF133_1003240018"
```

Periksa isi ZIP tidak memuat `bin`, `obj`, atau `.git`:

```bash
tar -tf "UTS_IF133_1003240018_SahrulSolihin.zip" | grep -E "bin/|obj/|\.git/" || echo "BERSIH"
```

**Catatan:** `test-endpoints.sh` dan `buat-laporan.py` boleh ikut karena
menunjukkan proses pengujian, bukan bagian yang dilarang.

---

## 5. Unggah ke LMS

1. Buka LMS ITTS → Kelas Kuliah → IF133 Pemrograman .NET → UTS
2. Pada bagian **Unggah File**, unggah berkas PDF laporan
   `UTS_IF133_1003240018_SahrulSolihin.pdf`
3. PDF harus di bawah 10 MB (laporan ini sekitar 0,5 MB, aman)
4. Kalau ada kolom tautan/komentar, tempel URL repository GitHub
5. Klik submit, lalu **unduh kembali berkas yang sudah diunggah** untuk
   memastikan tidak rusak

---

## 6. Daftar periksa akhir

- [ ] Aplikasi bisa di-build dari nol (`dotnet build` → 0 error)
- [ ] Migration diterapkan dan tabel Products punya unique index pada Code
- [ ] 14 screenshot terpasang di folder `screenshots/`
- [ ] Laporan dibangun ulang dan PDF berisi semua gambar
- [ ] Repository GitHub berisi source code lengkap dan bisa dibuka
- [ ] ZIP tidak memuat `bin`, `obj`, atau `.git`
- [ ] PDF diunggah ke LMS dan berhasil diunduh kembali
- [ ] Tautan GitHub ditempelkan bila diminta
