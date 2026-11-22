using Microsoft.AspNetCore.Mvc;

namespace UTS_IF133_1003240018.Controllers;

// Controller ini HANYA dipakai untuk membuktikan bahwa centralized error
// handling bekerja: exception yang dilempar di sini harus ditangkap
// UseExceptionHandler di Program.cs, dicatat lengkap di log server, dan
// client hanya menerima ProblemDetails 500 tanpa stack trace.
//
// Endpoint sengaja dibatasi hanya saat environment Development supaya tidak
// pernah ikut aktif di server produksi.
[ApiController]
[Route("api/[controller]")]
public class DiagnosticsController : ControllerBase
{
    private readonly IWebHostEnvironment _env;

    public DiagnosticsController(IWebHostEnvironment env)
    {
        _env = env;
    }

    [HttpGet("error")]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status500InternalServerError)]
    public IActionResult SimulateError()
    {
        if (!_env.IsDevelopment())
        {
            return NotFound();
        }

        // Dilempar sengaja, bukan bug: dipakai sebagai bukti pengujian
        // skenario "exception internal tak terduga" pada Soal 3b dan 3c.
        throw new InvalidOperationException(
            "Simulasi kegagalan internal: koneksi ke layanan inventori terputus.");
    }
}
