# JAWABAN UTS IF133 — Pemrograman .NET

Sahrul Solihin — 1003240018 — Informatika ITTS — Semester 5

---

## Soal 1a — Fungsi dan hubungan Program.cs, appsettings.json, Controller, DbContext, Swagger/OpenAPI

**Program.cs** adalah titik masuk aplikasi sekaligus tempat merakit seluruh komponen. Di file ini objek `builder` mengumpulkan service ke dalam container Dependency Injection (DbContext, controller, CORS, Swagger, dan lain-lain), lalu `app` menyusun urutan middleware yang dilewati setiap request. Urutan middleware penting: `UseExceptionHandler` harus paling depan agar bisa menangkap error dari middleware berikutnya, dan `UseAuthorization` harus setelah `UseAuthentication`. Kalau urutannya tertukar, penanganan error atau otorisasi tidak jalan sebagaimana mestinya. Program.cs tidak menyimpan data dan tidak memproses request, tugasnya hanya konfigurasi dan perakitan.

**appsettings.json** menyimpan konfigurasi yang bisa berubah tanpa mengompilasi ulang, misalnya connection string, level logging, dan daftar origin CORS. Nilainya dibaca lewat `builder.Configuration` dan bisa ditimpa oleh `appsettings.{Environment}.json`, environment variable, atau user-secrets. Urutan prioritasnya dari yang paling lemah ke paling kuat: appsettings.json → appsettings.Development.json → environment variable → command line. Karena itu connection string diletakkan di sini, bukan ditulis langsung di dalam kode, supaya development dan production bisa memakai database berbeda tanpa mengubah source code.

**Controller** adalah lapisan yang menerima HTTP request dan mengembalikan HTTP response. Controller tidak mengakses database secara langsung, ia meminta data lewat DbContext, lalu mengubah hasilnya menjadi DTO sebelum dikirim ke client. Atribut `[ApiController]` mengaktifkan binding otomatis dari body JSON ke parameter, dan `[Route("api/[controller]")]` menentukan alamat endpoint. Controller juga yang bertanggung jawab memilih status code yang tepat (200, 201, 204, 400, 404, 409).

**DbContext** adalah jembatan antara kode C# dan database. Ia berisi `DbSet<Product>` yang merepresentasikan tabel, menyimpan konfigurasi model (panjang kolom, unique index) lewat `OnModelCreating`, dan menerjemahkan query LINQ menjadi SQL. DbContext didaftarkan di Program.cs dengan `AddDbContext` dan provider SQLite, lalu disuntikkan ke controller lewat constructor. DbContext bersifat scoped: satu instance per request, dan dibuang setelah request selesai.

**Swagger/OpenAPI** menghasilkan dokumentasi endpoint yang bisa dicoba langsung dari browser. `AddEndpointsApiExplorer` mengumpulkan metadata endpoint, `AddSwaggerGen` menyusunnya menjadi dokumen OpenAPI, dan `UseSwagger`/`UseSwaggerUI` menyajikannya di `/swagger`. Swagger membaca atribut route dan tipe parameter dari controller, jadi dokumentasinya otomatis sinkron dengan kode. Karena hanya didaftarkan saat Development, di production endpoint dokumentasi ini tidak aktif.

**Hubungan kelimanya** dalam satu alur: Program.cs merakit semuanya dan menentukan urutan middleware → appsettings.json memasok nilai konfigurasi yang dipakai Program.cs → request masuk melewati middleware lalu diteruskan ke Controller yang cocok dengan route → Controller memakai DbContext untuk mengambil atau menyimpan data → hasilnya diubah ke DTO dan dikembalikan sebagai JSON → Swagger mendokumentasikan seluruh proses itu dari sisi luar tanpa ikut mengeksekusi request.

---

## Soal 1b — Alur request–response GET /api/products/5

**Tahap 1 — Client mengirim request.**
Client (Swagger, Postman, atau browser) mengirim `GET http://localhost:5070/api/products/5` dengan header `Accept: application/json`. Tidak ada body karena GET tidak membawa payload.

**Tahap 2 — Middleware berjalan berurutan.**
Request masuk ke pipeline. `UseExceptionHandler` membungkus sisa pipeline agar exception apa pun bisa ditangkap. `UseHttpsRedirection` memastikan koneksi memakai HTTPS. Karena tidak ada autentikasi pada project ini, request langsung melewati `UseAuthorization`, lalu `MapControllers` meneruskan request ke routing.

**Tahap 3 — Routing mencocokkan endpoint.**
Routing memeriksa tabel route yang dibangun saat startup. Template `api/[controller]` dengan nama class `ProductsController` menghasilkan prefix `api/Products`. Method `GetProduct(int id)` memakai `[HttpGet("{id:int}")]`, sehingga `/api/products/5` cocok dan nilai `5` diikat ke parameter `id`. Constraint `{id:int}` memastikan hanya angka yang diterima; kalau client mengirim `/api/products/abc`, route tidak cocok dan server langsung membalas 404 tanpa menyentuh controller.

**Tahap 4 — Model binding dan validasi.**
`[ApiController]` mengikat `id = 5`. Karena `id` adalah parameter sederhana dari route, tidak ada proses validasi model body. Kalau ada body yang tidak valid, `[ApiController]` akan otomatis membalas 400 sebelum action dijalankan.

**Tahap 5 — Controller memanggil DbContext.**
Action `GetProduct` dijalankan. DbContext disuntikkan lewat constructor. Pemanggilan `await _db.Products.AsNoTracking().FirstOrDefaultAsync(p => p.Id == id)` membuat EF Core menerjemahkan ekspresi LINQ menjadi SQL, kira-kira:

```sql
SELECT "p"."Id", "p"."Code", "p"."Name", "p"."Price", "p"."Stock", "p"."IsActive"
FROM "Products" AS "p"
WHERE "p"."Id" = @__id_0
LIMIT 1
```

Karena memakai `await`, thread tidak diblokir selama query berjalan; thread dikembalikan ke pool sampai hasil dari database siap. `AsNoTracking()` mematikan change tracker karena data hanya dibaca, sehingga lebih hemat memori.

**Tahap 6a — Jalur 200 OK.**
Kalau baris dengan Id 5 ditemukan, EF Core memetakan kolom hasil query ke objek `Product`. Controller mengubah entity itu menjadi `ProductReadDto` lewat method `ToReadDto`, lalu memanggil `Ok(dto)`. Hasilnya status **200 OK**, header `Content-Type: application/json`, dan body:

```json
{
  "id": 5,
  "code": "PRD-005",
  "name": "Keyboard Mechanical",
  "price": 750000,
  "stock": 12,
  "isActive": true
}
```

Serialisasi JSON dilakukan oleh `System.Text.Json` yang sudah terpasang di ASP.NET Core. Karena response memakai DTO, hanya field yang ada di DTO yang keluar.

**Tahap 6b — Jalur 404 Not Found.**
Kalau `FirstOrDefaultAsync` mengembalikan `null` (tidak ada baris dengan Id 5), controller mencatat peringatan ke log lewat `_logger.LogWarning` lalu mengembalikan `NotFound(ProblemDetails)`. Hasilnya status **404 Not Found** dan body:

```json
{
  "title": "Product not found",
  "status": 404,
  "detail": "Produk dengan id 5 tidak ditemukan."
}
```

404 dipilih, bukan 500, karena request client sebenarnya valid dan server berjalan normal; yang tidak ada hanyalah resource yang diminta. Status 500 hanya dipakai kalau terjadi kesalahan di sisi server, misalnya database tidak bisa dihubungi.

**Tahap 7 — Response kembali ke client.**
Response melewati middleware secara terbalik, lalu dikirim ke client. DbContext kemudian dibuang bersama berakhirnya scope request.

---

## Soal 3a — CreateProductDto dengan aturan validasi

```csharp
using System.ComponentModel.DataAnnotations;

namespace UTS_IF133_1003240018.Dtos;

public class CreateProductDto
{
    [Required(ErrorMessage = "Code wajib diisi.")]
    [StringLength(20, ErrorMessage = "Code maksimal 20 karakter.")]
    [RegularExpression("^[A-Za-z0-9-]+$",
        ErrorMessage = "Code hanya boleh huruf, angka, dan tanda hubung.")]
    public string Code { get; set; } = string.Empty;

    [Required(ErrorMessage = "Name wajib diisi.")]
    [StringLength(100, ErrorMessage = "Name maksimal 100 karakter.")]
    public string Name { get; set; } = string.Empty;

    [Range(0.01, 1000000000, ErrorMessage = "Price harus lebih besar dari 0.")]
    public decimal Price { get; set; }

    [Range(0, int.MaxValue, ErrorMessage = "Stock tidak boleh negatif.")]
    public int Stock { get; set; }

    public bool IsActive { get; set; } = true;
}
```

**Alasan pemilihan atribut:**

| Aturan soal | Atribut yang dipakai | Alasan |
|---|---|---|
| Code wajib | `[Required]` | Menolak null dan string kosong, termasuk string berisi spasi saja |
| Code maksimal 20 karakter | `[StringLength(20)]` | Membatasi panjang sesuai kolom database yang juga `HasMaxLength(20)` |
| Name wajib | `[Required]` | Sama seperti Code |
| Name maksimal 100 karakter | `[StringLength(100)]` | Konsisten dengan `HasMaxLength(100)` di konfigurasi EF |
| Price > 0 | `[Range(0.01, 1000000000)]` | Batas bawah 0.01 karena `decimal` tidak bisa memakai `(0, ...)` eksklusif; batas atas mencegah nilai tidak wajar |
| Stock tidak negatif | `[Range(0, int.MaxValue)]` | Batas bawah 0 sudah menutup nilai negatif |

Tambahan `[RegularExpression]` pada Code tidak diminta soal, tetapi dipakai supaya kode produk seragam dan tidak berisi spasi. Entity juga tetap punya unique index pada kolom Code sebagai pengaman terakhir.

DTO dipisahkan dari entity karena tiga alasan: (1) entity mengikuti bentuk tabel, sedangkan kontrak API harus bisa berubah sendiri; (2) field internal seperti `Id` tidak boleh bisa diisi client saat create; (3) validasi cukup menempel di DTO sehingga entity tetap bersih. Kalau payload tidak lolos validasi, `[ApiController]` otomatis membalas 400 dengan daftar error per field tanpa perlu `if` manual di controller.

---

## Soal 3b — HTTP status code untuk lima skenario

| Skenario | Status | Alasan |
|---|---|---|
| Payload tidak valid | **400 Bad Request** | Request sudah sampai dan dipahami server, tetapi isinya melanggar aturan validasi. Ini kesalahan client, bukan server. Body berisi daftar field yang salah agar client bisa memperbaiki. |
| Produk tidak ditemukan | **404 Not Found** | Request valid dan server sehat, hanya resource dengan id tersebut memang tidak ada. Bukan 400 karena format request benar, dan bukan 500 karena tidak ada kesalahan server. |
| Create berhasil | **201 Created** | Selain menandakan sukses, 201 mewajibkan header `Location` berisi URL resource baru. Di project ini dihasilkan oleh `CreatedAtAction(nameof(GetProduct), new { id = product.Id }, dto)` sehingga client langsung tahu alamat produk yang baru dibuat. |
| Code produk duplikat | **409 Conflict** | Request valid secara format, tetapi bertentangan dengan keadaan data yang sudah ada (unique constraint pada Code). 400 kurang tepat karena payload-nya sendiri tidak salah; 422 juga bisa diterima, tetapi 409 lebih umum untuk benturan keadaan resource. |
| Exception internal tak terduga | **500 Internal Server Error** | Kegagalan ada di sisi server dan bukan karena request client. Detail asli hanya masuk log; client menerima pesan umum. Stack trace tidak boleh ikut dikirim karena bisa membocorkan struktur database dan jalur file server. |

Catatan tambahan: **401 Unauthorized** dipakai kalau identitas belum terbukti dan **403 Forbidden** kalau identitas sudah terbukti tetapi tidak berhak. Keduanya tidak termasuk lima skenario di soal karena project UTS ini tidak memakai autentikasi.

---

## Soal 3c — Rancangan centralized error handling dan logging yang aman

**Prinsipnya: satu tempat menangkap, dua audiens berbeda.** Server butuh informasi selengkap mungkin untuk diagnosis, client hanya butuh pesan yang bisa ditindaklanjuti. Keduanya tidak boleh menerima informasi yang sama.

**1. Penanganan terpusat di Program.cs.**

```csharp
app.UseExceptionHandler(errorApp =>
{
    errorApp.Run(async context =>
    {
        var logger = context.RequestServices.GetRequiredService<ILogger<Program>>();
        var exception = context.Features.Get<IExceptionHandlerFeature>()?.Error;

        logger.LogError(exception, "Unhandled exception pada {Path}", context.Request.Path);

        context.Response.StatusCode = StatusCodes.Status500InternalServerError;
        context.Response.ContentType = "application/problem+json";

        await Results.Problem(
            title: "Internal Server Error",
            detail: "Terjadi kesalahan pada server. Silakan hubungi administrator.",
            statusCode: StatusCodes.Status500InternalServerError)
            .ExecuteAsync(context);
    });
});
```

`UseExceptionHandler` dipasang paling depan di pipeline sehingga membungkus semua middleware dan controller di belakangnya. Setiap exception yang tidak tertangani akan berhenti di sini, dicatat lengkap, lalu diganti response yang aman. Karena penanganannya satu tempat, bentuk response error tidak akan berbeda-beda antar endpoint.

**2. Error yang sudah diperkirakan tidak dilempar sebagai exception.**
Kasus 400, 404, dan 409 bukan "error tak terduga", jadi ditangani langsung di controller dengan return value (`BadRequest`, `NotFound`, `Conflict`). Yang masuk ke `UseExceptionHandler` hanya kegagalan yang benar-benar tidak terduga seperti database mati atau bug null reference. Ini penting supaya log error tidak penuh oleh hal yang sebenarnya normal.

**3. Bentuk response error yang konsisten (ProblemDetails).**

Semua error memakai format yang sama, mengikuti RFC 7807:

```json
{
  "type": "https://tools.ietf.org/html/rfc9110#section-15.5.4",
  "title": "Product not found",
  "status": 404,
  "detail": "Produk dengan id 5 tidak ditemukan."
}
```

Untuk error validasi, `[ApiController]` menambahkan properti `errors` berisi daftar pesan per field:

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

Client cukup memeriksa `status` dan `errors`, tidak perlu menebak bentuk body tiap endpoint.

**4. Logging yang berguna untuk diagnosis.**

- `LogInformation` untuk kejadian normal yang penting: produk dibuat, diperbarui, dihapus, beserta id dan kode produk.
- `LogWarning` untuk kejadian yang wajar terjadi tetapi perlu diperhatikan: GET/PUT/DELETE ke id yang tidak ada, percobaan membuat Code duplikat.
- `LogError` untuk exception tak terduga, selalu menyertakan objek exception dan `context.Request.Path` supaya bisa dilacak endpoint mana yang gagal.
- Log memakai structured logging (`{Id}`, `{Code}`) bukan penggabungan string, sehingga bisa dicari dan difilter.
- Di production level `Microsoft.AspNetCore` dinaikkan ke `Warning` supaya log tidak penuh noise dari framework.

**5. Informasi yang tidak boleh diekspos ke client.**

- **Stack trace** dan nama class/method internal, karena menunjukkan struktur kode dan memudahkan penyerang mencari celah.
- **Connection string** dan kredensial database.
- **Nama tabel, kolom, atau SQL query** yang gagal, karena membocorkan skema database.
- **Pesan exception mentah** dari provider database (misalnya "SQLite Error 19: UNIQUE constraint failed: Products.Code") karena menyebut nama tabel dan constraint secara persis.
- **Path file server** seperti `C:\Users\...\Program.cs` baris ke berapa.
- **Token, password, API key**, dan data pribadi pengguna, termasuk di dalam log.

Cara memisahkan keduanya: client hanya menerima `title`, `status`, dan `detail` yang sudah ditulis ulang dengan bahasa manusia; sedangkan stack trace utuh hanya ditulis ke log server yang hanya bisa diakses administrator.
