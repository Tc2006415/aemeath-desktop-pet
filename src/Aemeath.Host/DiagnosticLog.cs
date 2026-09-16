using System.Diagnostics;
using System.IO;
using System.Text.Json;

namespace Aemeath.Host;

internal sealed class DiagnosticLog : IDisposable
{
    private StreamWriter? writer;
    private readonly Stopwatch clock = Stopwatch.StartNew();
    private int entries;
    public DiagnosticLog(string? file)
    {
        if (file is not null) writer = new StreamWriter(file, false) { AutoFlush = true };
    }
    public void Write(string kind, object? data = null)
    {
        if (writer is null || entries >= 2048) return;
        try { writer.WriteLine(JsonSerializer.Serialize(new { ms = clock.ElapsedMilliseconds, kind, data })); entries++; }
        catch (IOException) { Dispose(); }
    }
    public void Dispose() { writer?.Dispose(); writer = null; }
}
