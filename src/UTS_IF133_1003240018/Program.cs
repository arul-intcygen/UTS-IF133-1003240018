using Microsoft.AspNetCore.Diagnostics;
using Microsoft.EntityFrameworkCore;
using UTS_IF133_1003240018.Data;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllers();

// ---------------------------------------------------------------------------
// Koneksi SQLite
// "Data Source" bersifat relatif terhadap working directory, jadi path file
// database dijadikan absolut terhadap ContentRootPath. Dengan begitu database
// tetap menunjuk ke satu file yang sama walaupun dotnet run dijalankan dari
// folder lain.
// ---------------------------------------------------------------------------
var connectionString = builder.Configuration.GetConnectionString("DefaultConnection");

if (string.IsNullOrWhiteSpace(connectionString))
{
    throw new InvalidOperationException(
        "ConnectionStrings:DefaultConnection belum diisi di appsettings.json.");
}

var dbFile = connectionString.Replace("Data Source=", string.Empty).Trim();
var dbFullPath = Path.Combine(builder.Environment.ContentRootPath, dbFile);

builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlite($"Data Source={dbFullPath}"));

// Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(options =>
{
    options.SwaggerDoc("v1", new Microsoft.OpenApi.Models.OpenApiInfo
    {
        Title = "UTS IF133 - Inventory Product API",
        Version = "v1",
        Description = "UTS Pemrograman .NET (IF133) - Sahrul Solihin / 1003240018"
    });
});

var app = builder.Build();

// ---------------------------------------------------------------------------
// Centralized error handling (Soal 3c)
// Exception dicatat lengkap di log server, sedangkan client hanya menerima
// ProblemDetails umum tanpa stack trace, nama tabel, atau detail internal.
// ---------------------------------------------------------------------------
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

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();

app.UseAuthorization();

app.MapControllers();

app.Run();
