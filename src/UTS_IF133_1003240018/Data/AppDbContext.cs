using Microsoft.EntityFrameworkCore;
using UTS_IF133_1003240018.Entities;

namespace UTS_IF133_1003240018.Data;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options)
    {
    }

    public DbSet<Product> Products => Set<Product>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        modelBuilder.Entity<Product>(entity =>
        {
            entity.Property(p => p.Code).IsRequired().HasMaxLength(20);
            entity.Property(p => p.Name).IsRequired().HasMaxLength(100);

            // Harga disimpan sebagai decimal; SQLite tidak punya tipe decimal
            // asli sehingga EF memetakannya ke TEXT untuk menjaga presisi.
            entity.Property(p => p.Price).HasColumnType("decimal(18,2)");

            // Unique index supaya duplikasi Code ditolak di level database,
            // bukan hanya dicek di controller (aman dari race condition).
            entity.HasIndex(p => p.Code).IsUnique();
        });
    }
}
