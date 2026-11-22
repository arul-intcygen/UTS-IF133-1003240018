# Langkah Screenshot UTS IF133 — Panduan Satu per Satu

Urutan yang benar:

```
1. Jalankan aplikasi      → server hidup di http://localhost:5070
2. Ambil 14 screenshot    → simpan di folder screenshots/
3. Bangun ulang laporan   → py -3.13 buat-laporan.py
4. Push GitHub + upload PDF ke LMS
```

Screenshot **tidak bisa** diambil sebelum aplikasi jalan, karena semua bukti
adalah tangkapan layar Swagger dan terminal.

---

## BAGIAN 1 — Menjalankan aplikasi

### 1.1 Buka terminal

Tekan `Win + X`, pilih **Terminal** atau **Windows PowerShell**.

### 1.2 Masuk ke folder project

Salin-tempel baris ini (tanda kutip wajib karena nama folder ada spasi dan titik):

```powershell
cd "C:\Users\Administrator\Downloads\Semester 5\Permograman .NET\Hands On\UTS\UTS_IF133_1003240018"
```

Tekan Enter. Tidak ada pesan apa pun kalau berhasil.

### 1.3 Jalankan server

```powershell
dotnet run --project src/UTS_IF133_1003240018/UTS_IF133_1003240018.csproj --launch-profile http
```

Proses build butuh sekitar 10–25 detik. **Yang diharapkan muncul** di terminal:

```
Building...
info: Microsoft.Hosting.Lifetime[14]
      Now listening on: http://localhost:5070
info: Microsoft.Hosting.Lifetime[0]
      Application started. Press Ctrl+C to shut down.
info: Microsoft.Hosting.Lifetime[0]
      Hosting environment: Development
```

Kalau tulisan `Now listening on: http://localhost:5070` sudah muncul,
**server siap**. Browser biasanya otomatis terbuka ke halaman Swagger.

**PENTING:** terminal ini jangan ditutup dan jangan ditekan Ctrl+C sampai
semua screenshot selesai. Server harus tetap hidup.

### 1.4 Buka Swagger (kalau browser tidak terbuka otomatis)

Buka browser, ketik di address bar:

```
http://localhost:5070/swagger
```

Yang terlihat: halaman putih dengan judul **UTS IF133 - Inventory Product API**
dan daftar endpoint:

```
Diagnostics   GET   /api/Diagnostics/error
Products      GET   /api/Products
              POST  /api/Products
              GET   /api/Products/{id}
              PUT   /api/Products/{id}
              DELETE /api/Products/{id}
```

### 1.5 Cara memakai Swagger (pola yang dipakai terus di bawah)

Untuk **semua** endpoint, langkahnya sama:

1. Klik kotak endpoint (misalnya `GET /api/Products`) → kotak terbuka
2. Klik tombol **Try it out** di kanan atas kotak
3. Kalau ada kolom isian, isi sesuai petunjuk
4. Klik tombol biru **Execute**
5. Gulir ke bawah, lihat bagian **Server response**

Yang harus masuk screenshot adalah bagian **Server response** ini, karena di
situ terlihat **Code** (status HTTP) dan **Response body**.

### 1.6 Cara mengambil screenshot

Tekan `Win + Shift + S` → layar meredup → seret mouse mengelilingi area yang
ingin diambil → gambar tersalin ke clipboard → muncul notifikasi kecil di
kanan bawah, klik notifikasi itu → editor Snipping Tool terbuka → tekan
`Ctrl + S` → simpan.

**Tempat menyimpan (penting, harus folder ini):**

```
C:\Users\Administrator\Downloads\Semester 5\Permograman .NET\Hands On\UTS\UTS_IF133_1003240018\screenshots
```

**Nama berkas harus persis** seperti daftar di bawah. Kalau salah nama,
laporan tidak akan menemukan gambarnya.

**Tips Windows:** kalau Explorer menyembunyikan ekstensi, saat mengetik nama
cukup tulis `01_swagger_home` lalu pilih **Save as type: PNG**. Windows
menambahkan `.png` sendiri. Jangan mengetik `01_swagger_home.png.png`.

---

## BAGIAN 2 — Screenshot satu per satu

Kerjakan **berurutan**. Nomor 2 harus sebelum yang lain karena database harus
masih kosong.

---

### Screenshot 1 — `01_swagger_home.png`

**Yang diambil:** seluruh halaman Swagger dari atas, memperlihatkan judul
aplikasi dan keenam endpoint.

**Caranya:** jangan klik apa pun. Gulir ke paling atas halaman Swagger, lalu
`Win + Shift + S` dan seret seluruh area daftar endpoint.

**Yang harus terlihat:** tulisan `UTS IF133 - Inventory Product API`, dan
endpoint Diagnostics serta Products (GET, POST, GET {id}, PUT, DELETE).

---

### Screenshot 2 — `02_get_list_kosong.png`

**Yang diuji:** GET daftar saat database kosong.

**Langkah:**

1. Klik `GET /api/Products`
2. Klik **Try it out**
3. Tidak ada kolom isian
4. Klik **Execute**
5. Gulir ke **Server response**

**Yang harus terlihat:**

```
Code: 200
Response body: []
```

`[]` artinya tabel masih kosong. Kalau sudah ada isinya, berarti database
belum bersih. Hentikan dulu dan hubungi saya.

---

### Screenshot 3 — `03_post_201.png`

**Yang diuji:** POST berhasil membuat produk baru.

**Langkah:**

1. Klik `POST /api/Products`
2. Klik **Try it out**
3. Di kotak **Request body**, ganti seluruh isinya menjadi:

```json
{
  "code": "PRD-001",
  "name": "Keyboard Mechanical",
  "price": 750000,
  "stock": 12,
  "isActive": true
}
```

4. Klik **Execute**
5. Gulir ke **Server response**

**Yang harus terlihat:**

```
Code: 201
Response body:
{
  "id": 1,
  "code": "PRD-001",
  "name": "Keyboard Mechanical",
  "price": 750000,
  "stock": 12,
  "isActive": true
}
```

**Penting:** gulir sedikit ke atas pada bagian response, cari baris
**`Response headers`** dan pastikan ada `location: http://localhost:5070/api/Products/1`.
Kalau bisa ikut masuk gambar, nilainya tambah bagus karena soal meminta 201
mengarah ke resource baru.

---

### Screenshot 4 — `04_post_409.png`

**Yang diuji:** Code duplikat ditolak.

**Langkah:**

1. Masih di `POST /api/Products`
2. Klik **Try it out** lagi
3. Isi Request body (sengaja `PRD-001` lagi, nama berbeda):

```json
{
  "code": "PRD-001",
  "name": "Produk Lain",
  "price": 100000,
  "stock": 5,
  "isActive": true
}
```

4. Klik **Execute**

**Yang harus terlihat:**

```
Code: 409
Response body:
{
  "title": "Duplicate product code",
  "status": 409,
  "detail": "Kode produk 'PRD-001' sudah digunakan."
}
```

---

### Screenshot 5 — `05_post_400.png`

**Yang diuji:** validasi menolak input tidak valid.

**Langkah:**

1. `POST /api/Products` → **Try it out**
2. Isi Request body (semua nilainya sengaja salah):

```json
{
  "code": "",
  "name": "",
  "price": 0,
  "stock": -5,
  "isActive": true
}
```

3. Klik **Execute**

**Yang harus terlihat:**

```
Code: 400
Response body:
{
  "type": "https://tools.ietf.org/html/rfc9110#section-15.5.1",
  "title": "One or more validation errors occurred.",
  "status": 400,
  "errors": {
    "Code": ["Code wajib diisi."],
    "Name": ["Name wajib diisi."],
    "Price": ["Price harus lebih besar dari 0."],
    "Stock": ["Stock tidak boleh negatif."]
  },
  "traceId": "00-c04a253256f8acb5d79835931caa845e-..."
}
```

Ini bukti keempat aturan validasi bekerja sekaligus. Properti `traceId` di
akhir itu normal — dipakai untuk mencocokkan response dengan baris di log
server, bukan kebocoran informasi.

---

### Langkah antara (tanpa screenshot)

Sebelum lanjut, buat **dua produk tambahan** supaya endpoint GET dan DELETE
punya data. Langkah ini tidak perlu di-screenshot, tapi wajib dilakukan.

**Produk kedua** — `POST /api/Products` → **Try it out** → Execute:

```json
{
  "code": "PRD-002",
  "name": "Mouse Wireless",
  "price": 275000,
  "stock": 30,
  "isActive": true
}
```

**Produk ketiga** — `POST /api/Products` → **Try it out** → Execute:

```json
{
  "code": "PRD-003",
  "name": "Monitor 24 Inch",
  "price": 1850000,
  "stock": 0,
  "isActive": false
}
```

Keduanya harus membalas `201`. Sekarang database berisi 3 produk.

---

### Screenshot 6 — `06_get_200.png`

**Yang diuji:** GET satu produk yang ada.

**Langkah:**

1. Klik `GET /api/Products/{id}`
2. Klik **Try it out**
3. Isi kolom **id** dengan `1`
4. Klik **Execute**

**Yang harus terlihat:**

```
Code: 200
Response body:
{
  "id": 1,
  "code": "PRD-001",
  "name": "Keyboard Mechanical",
  "price": 750000,
  "stock": 12,
  "isActive": true
}
```

---

### Screenshot 7 — `07_get_404.png`

**Yang diuji:** GET produk yang tidak ada.

**Langkah:**

1. Masih di `GET /api/Products/{id}`
2. Klik **Try it out**
3. Isi kolom **id** dengan `9999`
4. Klik **Execute**

**Yang harus terlihat:**

```
Code: 404
Response body:
{
  "title": "Product not found",
  "status": 404,
  "detail": "Produk dengan id 9999 tidak ditemukan."
}
```

---

### Screenshot 8 — `08_put_204.png`

**Yang diuji:** PUT berhasil mengubah produk.

**Langkah:**

1. Klik `PUT /api/Products/{id}`
2. Klik **Try it out**
3. Isi **id** dengan `1`
4. Isi Request body:

```json
{
  "code": "PRD-001",
  "name": "Keyboard Mechanical RGB",
  "price": 825000,
  "stock": 8,
  "isActive": true
}
```

5. Klik **Execute**

**Yang harus terlihat:**

```
Code: 204
Response body: (kosong)
```

**Catatan:** body kosong itu **benar** untuk 204. Bukan error. Jangan panik
kalau tidak ada tulisan apa pun di Response body.

**Bonus (kalau mau gambar lebih kuat):** setelah 204, jalankan
`GET /api/Products/1` di tab lain dan tunjukkan nama sudah berubah jadi
"Keyboard Mechanical RGB" dengan harga 825000. Boleh digabung dalam satu
screenshot dengan hasil 204-nya.

---

### Screenshot 9 — `09_delete_204.png`

**Yang diuji:** DELETE berhasil menghapus produk.

**Langkah:**

1. Klik `DELETE /api/Products/{id}`
2. Klik **Try it out**
3. Isi **id** dengan `2` (ini produk PRD-002 Mouse Wireless)
4. Klik **Execute**

**Yang harus terlihat:**

```
Code: 204
Response body: (kosong)
```

Sama seperti PUT, body kosong itu benar.

---

### Screenshot 10 — `10_delete_404.png`

**Yang diuji:** DELETE produk yang sudah tidak ada.

**Langkah:**

1. Masih di `DELETE /api/Products/{id}`
2. Klik **Try it out** lagi
3. Isi **id** dengan `2` (sama seperti tadi, sekarang sudah terhapus)
4. Klik **Execute**

**Yang harus terlihat:**

```
Code: 404
Response body:
{
  "title": "Product not found",
  "status": 404,
  "detail": "Produk dengan id 2 tidak ditemukan."
}
```

---

### Screenshot 11 — `11_error_500.png`

**Yang diuji:** centralized error handling menangkap exception.

**Langkah:**

1. Klik `GET /api/Diagnostics/error`
2. Klik **Try it out**
3. Klik **Execute**

**Yang harus terlihat:**

```
Code: 500
Response body:
{
  "type": "https://tools.ietf.org/html/rfc9110#section-15.6.1",
  "title": "Internal Server Error",
  "status": 500,
  "detail": "Terjadi kesalahan pada server. Silakan hubungi administrator."
}
```

**Yang paling penting untuk diperhatikan:** body di atas **tidak** memuat
stack trace, nama tabel, atau path file. Itulah buktinya bahwa detail internal
tidak bocor ke client. Ini nilai rubrik Soal 3c.

---

### Screenshot 12 — `12_log_server.png`

**Yang diuji:** bukti bahwa detail lengkap hanya ada di log server.

**Langkah:**

1. Pindah ke terminal tempat `dotnet run` berjalan (terminal dari langkah 1.3)
2. Gulir ke bagian paling bawah
3. Cari blok teks yang diawali `fail:` atau `System.InvalidOperationException`

**Yang harus terlihat** (kira-kira seperti ini):

```
fail: Microsoft.AspNetCore.Diagnostics.ExceptionHandlerMiddleware[1]
      An unhandled exception has occurred while executing the request.
      System.InvalidOperationException: Simulasi kegagalan internal:
      koneksi ke layanan inventori terputus.
         at UTS_IF133_1003240018.Controllers.DiagnosticsController.SimulateError()
            in ...\Controllers\DiagnosticsController.cs:line 34
         at lambda_method123(Closure, Object, Object[])
         at Microsoft.AspNetCore.Mvc.Infrastructure.ActionMethodExecutor...
         ...
```

Ambil area dari baris `fail:` sampai beberapa baris `at ...` di bawahnya.
Tidak perlu seluruh stack trace — tiga atau empat baris `at` sudah cukup
menunjukkan bahwa detail lengkap memang ada di server.

**Inti bukti:** screenshot 11 menunjukkan client hanya dapat pesan umum,
screenshot 12 menunjukkan server punya detail lengkap. Pasangan ini yang
dinilai.

---

### Screenshot 13 — `13_migration.png`

**Yang diuji:** migration berhasil dibuat.

**Langkah:**

1. Buka terminal **baru** (jangan tutup yang sedang menjalankan server).
   Tekan `Win + X` → **Terminal** lagi.
2. Masuk ke folder project:

```powershell
cd "C:\Users\Administrator\Downloads\Semester 5\Permograman .NET\Hands On\UTS\UTS_IF133_1003240018\src\UTS_IF133_1003240018"
```

3. Jalankan:

```powershell
dotnet ef migrations list
```

**Yang harus terlihat:**

```
Build started...
Build succeeded.
20261121234933_InitialCreate
```

Ambil screenshot yang memperlihatkan baris `20261121234933_InitialCreate`.
Kalau terminal menunjukkan log query SQL yang panjang, cukup tangkap bagian
akhir yang berisi nama migration tersebut.

---

### Screenshot 14 — `14_db_tabel.png`

**Yang diuji:** tabel dan isi database bisa diverifikasi.

**Langkah:**

1. Buka **DB Browser for SQLite**. Kalau tidak ada di Start Menu, jalankan:

```
C:\Program Files (x86)\DB Browser for SQLite\DB Browser for SQLite.exe
```

2. Klik **Open Database**
3. Arahkan ke:

```
C:\Users\Administrator\Downloads\Semester 5\Permograman .NET\Hands On\UTS\UTS_IF133_1003240018\src\UTS_IF133_1003240018\uts-if133.db
```

4. Klik tab **Browse Data**
5. Pada dropdown **Table**, pilih `Products`

**Yang harus terlihat:** tabel dengan kolom `Id`, `Code`, `Name`, `Price`,
`Stock`, dan `IsActive` berisi 2 baris (PRD-001 hasil update dan PRD-003).
PRD-002 sudah terhapus di langkah 9.

Ambil screenshot seluruh jendela yang memperlihatkan nama tabel `Products`
dan isinya.

**Kalau mau gambar lebih lengkap**, klik tab **Database Structure** — akan
terlihat `Products` dan `__EFMigrationsHistory`, plus index `IX_Products_Code`.
Boleh dijadikan satu gambar dengan tab Browse Data, atau tambahan sendiri.

---

## BAGIAN 3 — Setelah semua screenshot terkumpul

### 3.1 Periksa kelengkapan

Buka File Explorer ke folder `screenshots`. Harus ada **14 berkas**:

```
01_swagger_home.png
02_get_list_kosong.png
03_post_201.png
04_post_409.png
05_post_400.png
06_get_200.png
07_get_404.png
08_put_204.png
09_delete_204.png
10_delete_404.png
11_error_500.png
12_log_server.png
13_migration.png
14_db_tabel.png
```

### 3.2 Bangun ulang laporan

Hentikan server dulu dengan `Ctrl + C` di terminal-nya, lalu di terminal baru:

```powershell
cd "C:\Users\Administrator\Downloads\Semester 5\Permograman .NET\Hands On\UTS\UTS_IF133_1003240018"
py -3.13 buat-laporan.py
```

**Yang diharapkan muncul:**

```
DOCX dibuat: ...\UTS_IF133_1003240018_SahrulSolihin.docx
Screenshot terpasang: 14 dari 14
```

Kalau masih kurang dari 14, berarti ada nama file yang salah ketik atau
salah folder. Periksa lagi.

### 3.3 Ubah DOCX menjadi PDF

```powershell
& "C:\Program Files\LibreOffice\program\soffice.exe" --headless --convert-to pdf --outdir . "UTS_IF133_1003240018_SahrulSolihin.docx"
```

Hasil: `UTS_IF133_1003240018_SahrulSolihin.pdf`. Buka PDF-nya dan pastikan
semua 14 gambar benar-benar muncul, bukan kotak abu-abu placeholder.

---

## Kalau ada masalah

| Gejala | Penyebab | Solusi |
|---|---|---|
| `dotnet : command not found` | terminal belum mengenal dotnet | tutup terminal, buka baru |
| `Address already in use` / port 5070 dipakai | server lain masih hidup | `Ctrl + C` di terminal lama, atau `Stop-Process -Name UTS_IF133_1003240018 -Force` |
| Swagger tidak terbuka | browser tidak auto-launch | buka manual `http://localhost:5070/swagger` |
| POST membalas 409 padahal baru pertama | database belum kosong dari percobaan sebelumnya | hapus `uts-if133.db`, jalankan `dotnet ef database update` dari folder project |
| Laporan masih placeholder | nama file screenshot tidak cocok | cocokkan persis dengan daftar 14 nama di atas |
| `buat-laporan.py` error `No module named docx` | pakai Python yang salah | gunakan `py -3.13`, bukan `python` |
