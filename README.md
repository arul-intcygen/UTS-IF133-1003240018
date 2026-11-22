# UTS IF133 — Inventory Product API

## Identitas

- Nama: Sahrul Solihin
- NIM: 1003240018
- Mata Kuliah: Pemrograman .NET (IF133)
- Kelas: Informatika / Semester 5
- Dosen: Taufik Iqbal Ramdhani, S.Kom., M.Sc.
- Nama project: `UTS_IF133_1003240018`

## Ringkas

REST API untuk mengelola data produk inventori toko, dibuat sesuai Soal 2 UTS. Endpoint yang tersedia adalah CRUD lengkap pada `/api/products` dengan Entity Framework Core + SQLite, validasi input memakai DataAnnotations, dan centralized error handling yang mengembalikan ProblemDetails.

Jawaban tertulis Soal 1 dan Soal 3 ada di file `JAWABAN-UTS.md`.

## Teknologi

- ASP.NET Core Web API (net8.0)
- Entity Framework Core 8.0.32 dengan provider SQLite
- Swashbuckle.AspNetCore 6.6.2 (Swagger/OpenAPI)
- Database: `uts-if133.db` (SQLite)
- Port development: http://localhost:5070

## Cara Menjalankan

```bash
# 1. build
dotnet build

# 2. siapkan database (migration sudah ada di Data/Migrations)
cd src/UTS_IF133_1003240018
dotnet ef database update

# 3. jalankan
cd ../..
dotnet run --project src/UTS_IF133_1003240018/UTS_IF133_1003240018.csproj
```

Buka Swagger di http://localhost:5070/swagger

Kalau ingin mengulang dari database kosong:

```bash
cd src/UTS_IF133_1003240018
rm -f uts-if133.db
dotnet ef database update
```

## Struktur Project

```
UTS_IF133_1003240018/
├── UTS_IF133_1003240018.sln
├── global.json                       # mematok SDK 8.0.426
├── README.md
├── JAWABAN-UTS.md                    # jawaban Soal 1 dan Soal 3
├── test-endpoints.sh                 # skrip uji 21 skenario
├── screenshots/                       # bukti pengujian
└── src/UTS_IF133_1003240018/
    ├── Program.cs                     # konfigurasi service, middleware, error handler
    ├── appsettings.json               # connection string + logging
    ├── Entities/Product.cs            # Id, Code, Name, Price, Stock, IsActive
    ├── Data/
    │   ├── AppDbContext.cs            # DbSet Products + unique index Code
    │   └── Migrations/                # InitialCreate
    ├── Dtos/
    │   ├── CreateProductDto.cs        # validasi create
    │   ├── UpdateProductDto.cs        # validasi update
    │   └── ProductReadDto.cs          # kontrak response
    └── Controllers/
        ├── ProductsController.cs      # CRUD
        └── DiagnosticsController.cs   # simulasi 500 (hanya Development)
```

## Entity Product

| Properti | Tipe | Aturan |
|---|---|---|
| Id | int | primary key, auto increment |
| Code | string | wajib, maks 20 karakter, unique index |
| Name | string | wajib, maks 100 karakter |
| Price | decimal | lebih besar dari 0, disimpan `decimal(18,2)` |
| Stock | int | tidak boleh negatif |
| IsActive | bool | default true |

## Endpoint

| Method | Route | Sukses | Gagal | Keterangan |
|---|---|---|---|---|
| GET | /api/products | 200 | - | seluruh produk, urut Id |
| GET | /api/products/{id} | 200 | 404 | satu produk |
| POST | /api/products | 201 + Location | 400, 409 | tambah produk |
| PUT | /api/products/{id} | 204 | 400, 404, 409 | ubah produk |
| DELETE | /api/products/{id} | 204 | 404 | hapus produk |
| GET | /api/diagnostics/error | 500 | - | simulasi exception untuk bukti error handling |

Endpoint `diagnostics` hanya aktif saat environment Development dan hanya dipakai sebagai bukti bahwa centralized error handling bekerja.

## Contoh Request

**POST /api/products** dengan data contoh dari soal:

```json
{
  "code": "PRD-001",
  "name": "Keyboard Mechanical",
  "price": 750000,
  "stock": 12,
  "isActive": true
}
```

Respons 201 Created beserta header `Location: http://localhost:5070/api/Products/1`:

```json
{
  "id": 1,
  "code": "PRD-001",
  "name": "Keyboard Mechanical",
  "price": 750000,
  "stock": 12,
  "isActive": true
}
```

## Bentuk Respons Error

Validasi gagal (400):

```json
{
  "type": "https://tools.ietf.org/html/rfc9110#section-15.5.1",
  "title": "One or more validation errors occurred.",
  "status": 400,
  "errors": {
    "Code": ["Code wajib diisi."],
    "Price": ["Price harus lebih besar dari 0."],
    "Stock": ["Stock tidak boleh negatif."]
  }
}
```

Produk tidak ditemukan (404):

```json
{
  "title": "Product not found",
  "status": 404,
  "detail": "Produk dengan id 9999 tidak ditemukan."
}
```

Code duplikat (409):

```json
{
  "title": "Duplicate product code",
  "status": 409,
  "detail": "Kode produk 'PRD-001' sudah digunakan."
}
```

Exception tak terduga (500), tanpa stack trace:

```json
{
  "type": "https://tools.ietf.org/html/rfc9110#section-15.6.1",
  "title": "Internal Server Error",
  "status": 500,
  "detail": "Terjadi kesalahan pada server. Silakan hubungi administrator."
}
```

## Hasil Pengujian

Skrip `test-endpoints.sh` menguji 21 skenario dan semuanya sesuai harapan. Jalankan dengan database kosong:

| No | Skenario | Hasil |
|---|---|---|
| 1 | GET /api/products saat database kosong | 200, body `[]` |
| 2 | POST dengan data contoh soal | 201, header Location benar |
| 3 | POST Code duplikat | 409 |
| 4 | POST semua field tidak valid | 400, 4 pesan error per field |
| 5 | POST Code lebih dari 20 karakter | 400 |
| 6 | POST Code mengandung spasi | 400 |
| 7 | POST produk kedua | 201 |
| 8 | POST produk ketiga (stock 0, isActive false) | 201 |
| 9 | GET produk yang ada | 200 |
| 10 | GET id 100 | 404 ProblemDetails |
| 11 | GET list berisi 3 produk | 200 |
| 12 | PUT produk ada | 204, data berubah saat GET |
| 13 | PUT id tidak ada | 404 |
| 14 | PUT memakai Code milik produk lain | 409 |
| 15 | PUT payload tidak valid | 400 |
| 16 | DELETE produk ada | 204 |
| 17 | DELETE produk yang sama lagi | 404 |
| 18 | GET produk yang sudah dihapus | 404 |
| 19 | GET /api/diagnostics/error | 500 ProblemDetails |
| 20 | Body 500 diperiksa | tidak memuat stack trace atau path server |
| 21 | GET list akhir | 200, sisa 2 produk |

## Migration dan Database

Migration dibuat dengan:

```bash
cd src/UTS_IF133_1003240018
dotnet ef migrations add InitialCreate -o Data/Migrations
dotnet ef database update
```

Hasil `dotnet ef migrations list`:

```
20261121234933_InitialCreate
```

Skema tabel Products di SQLite:

```sql
CREATE TABLE "Products" (
    "Id" INTEGER NOT NULL CONSTRAINT "PK_Products" PRIMARY KEY AUTOINCREMENT,
    "Code" TEXT NOT NULL,
    "Name" TEXT NOT NULL,
    "Price" decimal(18,2) NOT NULL,
    "Stock" INTEGER NOT NULL,
    "IsActive" INTEGER NOT NULL
);
CREATE UNIQUE INDEX "IX_Products_Code" ON "Products" ("Code");
```

## Catatan Implementasi

1. **Async/await** dipakai di seluruh akses database: `ToListAsync`, `FirstOrDefaultAsync`, `AnyAsync`, dan `SaveChangesAsync`.
2. **AsNoTracking** dipakai pada operasi baca karena data tidak akan diubah, sehingga lebih hemat memori.
3. **Unique index pada Code** membuat duplikasi ditolak di level database. Pemeriksaan `AnyAsync` di controller tetap ada supaya pesan errornya ramah, bukan error mentah dari SQLite.
4. **Code dinormalisasi** dengan `Trim().ToUpperInvariant()` supaya `prd-001` dan `PRD-001` dianggap sama.
5. **Path database absolut** terhadap `ContentRootPath`, jadi `dotnet run` dari folder mana pun tetap memakai satu file database yang sama.
6. **`dotnet ef` dari folder project**, bukan dari root solution, supaya tool menemukan DbContext dengan benar.

## Kendala dan Solusi

1. Saat menyiapkan atribut dokumentasi Swagger, semua endpoint awalnya tampil sebagai respons 200 saja di Swagger UI walaupun kode sudah mengembalikan 201/204/400/404. Penyebabnya Swagger hanya membaca status code yang dideklarasikan. Solusinya menambahkan `[ProducesResponseType]` pada tiap action dan `[Produces("application/json")]` pada level controller, setelah itu Swagger menampilkan 201/400/409 untuk POST, 204/400/404/409 untuk PUT, dan 204/404 untuk DELETE.
2. Skrip pengujian sempat gagal di skenario POST valid (dapat 409) ketika dijalankan dua kali, karena data `PRD-001` dari run sebelumnya masih ada di database. Bukan bug aplikasi. Solusinya menghapus `uts-if133.db` lalu menjalankan `dotnet ef database update` sebelum mengulang pengujian.
3. `dotnet ef migrations add` gagal kalau aplikasi masih berjalan karena file `.exe` terkunci. Solusinya menghentikan server dulu dengan Ctrl+C.
4. Id produk di SQLite tidak selalu berurutan setelah data dihapus karena AUTOINCREMENT. Bukan bug, hanya penomoran yang terus maju.
5. Saat mengambil bukti migration, `dotnet ef migrations list` sempat gagal dengan pesan `Build failed. Use dotnet build to see the errors.` karena aplikasi masih berjalan di terminal lain sehingga file `UTS_IF133_1003240018.exe` terkunci (pesan MSBuild MSB3026/MSB3027 menyebut proses yang mengunci). Solusinya menjalankan ulang dengan opsi `--no-build`:

   ```
   dotnet ef migrations list --no-build
   ```

   Dengan opsi itu EF memakai DLL yang sudah ada di folder `bin` tanpa membangun ulang, sehingga tidak perlu menimpa file `.exe` yang sedang dipakai. Hasilnya migration `20261121234933_InitialCreate` berhasil ditampilkan dan server Swagger tetap hidup. Screenshot 13 menampilkan kedua percobaan tersebut sebagai bukti prosesnya.

## Daftar Screenshot (sudah ada di folder `screenshots/`)

Semua 14 screenshot sudah diambil sendiri oleh mahasiswa saat aplikasi berjalan:

1. `01_swagger_home.png` — halaman Swagger menampilkan semua endpoint
2. `02_get_list_kosong.png` — GET /api/products, respons `[]`
3. `03_post_201.png` — POST data contoh soal, 201 + header Location
4. `04_post_409.png` — POST Code duplikat, 409
5. `05_post_400.png` — POST field kosong (stock -5), 400 + daftar errors
6. `06_get_200.png` — GET /api/products/1, 200
7. `07_get_404.png` — GET /api/products/100, 404
8. `08_put_204.png` — PUT berhasil, 204
9. `09_delete_204.png` — DELETE id 2 berhasil, 204
10. `10_delete_404.png` — DELETE id 2 ulang, 404
11. `11_error_500.png` — GET /api/diagnostics/error, 500 tanpa stack trace
12. `12_log_server.png` — log terminal: stack trace lengkap hanya di server
13. `13_migration.png` — hasil `dotnet ef migrations list --no-build`
14. `14_db_tabel.png` — isi tabel Products di DB Browser for SQLite
