using System.ComponentModel.DataAnnotations;

namespace UTS_IF133_1003240018.Dtos;

// Soal 3a: DTO dipisahkan dari entity supaya kontrak API tidak otomatis
// mengikuti perubahan kolom database.
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
