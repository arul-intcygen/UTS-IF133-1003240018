namespace UTS_IF133_1003240018.Entities;

public class Product
{
    public int Id { get; set; }

    // Kode produk unik, misalnya PRD-001. Dipakai sebagai identitas bisnis
    // dan diberi unique index di AppDbContext.
    public string Code { get; set; } = string.Empty;

    public string Name { get; set; } = string.Empty;

    public decimal Price { get; set; }

    public int Stock { get; set; }

    public bool IsActive { get; set; } = true;
}
