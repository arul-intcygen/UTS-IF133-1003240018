namespace UTS_IF133_1003240018.Dtos;

// Bentuk data yang dikirim balik ke client. Sengaja hanya berisi field yang
// memang dibutuhkan, bukan seluruh isi entity.
public class ProductReadDto
{
    public int Id { get; set; }
    public string Code { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public decimal Price { get; set; }
    public int Stock { get; set; }
    public bool IsActive { get; set; }
}
