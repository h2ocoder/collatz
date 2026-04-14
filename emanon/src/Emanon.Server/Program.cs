using Emanon.Server.Endpoints;
using Emanon.Server.Storage;

var builder = WebApplication.CreateBuilder(args);

// ── Services ──────────────────────────────────────────────────────────────────
builder.Services.AddSingleton<InMemoryStore>();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new()
    {
        Title   = "Emanon Central Authority API",
        Version = "v1",
        Description = "Registry and bounty board for Emanon universes. " +
                      "Powered by Collatz genus stamps."
    });
});

var app = builder.Build();

// ── Middleware ────────────────────────────────────────────────────────────────
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(c =>
    {
        c.SwaggerEndpoint("/swagger/v1/swagger.json", "Emanon API v1");
        c.RoutePrefix = string.Empty; // Serve at root /
    });
}

// Disable HTTPS redirect for local dev — Caddy handles TLS in production
// app.UseHttpsRedirection();

// ── Health check ──────────────────────────────────────────────────────────────
app.MapGet("/health", () => Results.Ok(new { status = "ok", server = "emanon-central", version = "0.1.0" }))
   .WithTags("System");

// ── API endpoints ─────────────────────────────────────────────────────────────
app.MapRegistry();
app.MapBounties();

app.Run();

// Required for WebApplicationFactory in integration tests
public partial class Program { }
