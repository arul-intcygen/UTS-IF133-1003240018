using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using UTS_IF133_1003240018.Data;
using UTS_IF133_1003240018.Dtos;
using UTS_IF133_1003240018.Entities;

namespace UTS_IF133_1003240018.Controllers;

[ApiController]
[Route("api/[controller]")]
[Produces("application/json")]
public class ProductsController : ControllerBase
{
    private readonly AppDbContext _db;
    private readonly ILogger<ProductsController> _logger;

    public ProductsController(AppDbContext db, ILogger<ProductsController> logger)
    {
        _db = db;
        _logger = logger;
    }

    private static ProductReadDto ToReadDto(Product p) => new()
    {
        Id = p.Id,
        Code = p.Code,
        Name = p.Name,
        Price = p.Price,
        Stock = p.Stock,
        IsActive = p.IsActive
    };

    // GET /api/products -> 200 OK
    [HttpGet]
    [ProducesResponseType(typeof(IEnumerable<ProductReadDto>), StatusCodes.Status200OK)]
    public async Task<ActionResult<IEnumerable<ProductReadDto>>> GetProducts()
    {
        var products = await _db.Products
            .AsNoTracking()
            .OrderBy(p => p.Id)
            .Select(p => new ProductReadDto
            {
                Id = p.Id,
                Code = p.Code,
                Name = p.Name,
                Price = p.Price,
                Stock = p.Stock,
                IsActive = p.IsActive
            })
            .ToListAsync();

        return Ok(products);
    }

    // GET /api/products/{id} -> 200 OK atau 404 Not Found
    [HttpGet("{id:int}")]
    [ProducesResponseType(typeof(ProductReadDto), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status404NotFound)]
    public async Task<ActionResult<ProductReadDto>> GetProduct(int id)
    {
        var product = await _db.Products
            .AsNoTracking()
            .FirstOrDefaultAsync(p => p.Id == id);

        if (product is null)
        {
            _logger.LogWarning("GET produk id {Id} tidak ditemukan", id);
            return NotFound(new ProblemDetails
            {
                Title = "Product not found",
                Detail = $"Produk dengan id {id} tidak ditemukan.",
                Status = StatusCodes.Status404NotFound
            });
        }

        return Ok(ToReadDto(product));
    }

    // POST /api/products -> 201 Created dengan header Location
    [HttpPost]
    [ProducesResponseType(typeof(ProductReadDto), StatusCodes.Status201Created)]
    [ProducesResponseType(typeof(ValidationProblemDetails), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status409Conflict)]
    public async Task<ActionResult<ProductReadDto>> CreateProduct(CreateProductDto dto)
    {
        var code = dto.Code.Trim().ToUpperInvariant();

        // Cek duplikat di aplikasi untuk pesan yang ramah, tetapi unique index
        // di database tetap menjadi pengaman terakhir.
        var codeExists = await _db.Products.AnyAsync(p => p.Code == code);
        if (codeExists)
        {
            _logger.LogWarning("POST ditolak, Code {Code} sudah dipakai", code);
            return Conflict(new ProblemDetails
            {
                Title = "Duplicate product code",
                Detail = $"Kode produk '{code}' sudah digunakan.",
                Status = StatusCodes.Status409Conflict
            });
        }

        var product = new Product
        {
            Code = code,
            Name = dto.Name.Trim(),
            Price = dto.Price,
            Stock = dto.Stock,
            IsActive = dto.IsActive
        };

        _db.Products.Add(product);
        await _db.SaveChangesAsync();

        _logger.LogInformation("Produk {Code} dibuat dengan id {Id}", product.Code, product.Id);

        // CreatedAtAction menghasilkan 201 + header Location ke GET by id.
        return CreatedAtAction(nameof(GetProduct), new { id = product.Id }, ToReadDto(product));
    }

    // PUT /api/products/{id} -> 204 No Content atau 404 Not Found
    [HttpPut("{id:int}")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(typeof(ValidationProblemDetails), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status404NotFound)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status409Conflict)]
    public async Task<IActionResult> UpdateProduct(int id, UpdateProductDto dto)
    {
        var product = await _db.Products.FirstOrDefaultAsync(p => p.Id == id);

        if (product is null)
        {
            _logger.LogWarning("PUT produk id {Id} tidak ditemukan", id);
            return NotFound(new ProblemDetails
            {
                Title = "Product not found",
                Detail = $"Produk dengan id {id} tidak ditemukan.",
                Status = StatusCodes.Status404NotFound
            });
        }

        var code = dto.Code.Trim().ToUpperInvariant();

        // Code milik produk lain tidak boleh dipakai (kecuali miliknya sendiri).
        var codeTaken = await _db.Products.AnyAsync(p => p.Code == code && p.Id != id);
        if (codeTaken)
        {
            _logger.LogWarning("PUT ditolak, Code {Code} milik produk lain", code);
            return Conflict(new ProblemDetails
            {
                Title = "Duplicate product code",
                Detail = $"Kode produk '{code}' sudah digunakan produk lain.",
                Status = StatusCodes.Status409Conflict
            });
        }

        product.Code = code;
        product.Name = dto.Name.Trim();
        product.Price = dto.Price;
        product.Stock = dto.Stock;
        product.IsActive = dto.IsActive;

        await _db.SaveChangesAsync();

        _logger.LogInformation("Produk id {Id} diperbarui", id);

        return NoContent();
    }

    // DELETE /api/products/{id} -> 204 No Content atau 404 Not Found
    [HttpDelete("{id:int}")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status404NotFound)]
    public async Task<IActionResult> DeleteProduct(int id)
    {
        var product = await _db.Products.FirstOrDefaultAsync(p => p.Id == id);

        if (product is null)
        {
            _logger.LogWarning("DELETE produk id {Id} tidak ditemukan", id);
            return NotFound(new ProblemDetails
            {
                Title = "Product not found",
                Detail = $"Produk dengan id {id} tidak ditemukan.",
                Status = StatusCodes.Status404NotFound
            });
        }

        _db.Products.Remove(product);
        await _db.SaveChangesAsync();

        _logger.LogInformation("Produk id {Id} dihapus", id);

        return NoContent();
    }
}
