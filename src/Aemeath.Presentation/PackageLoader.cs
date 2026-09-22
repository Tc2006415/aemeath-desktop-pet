using System.Text.Json;
using System.Text.RegularExpressions;

namespace Aemeath.Presentation;

public sealed record DecodedImage(int Width, int Height, byte[] Bgra);
public sealed record AssetPackage(string Id, string Version, string Kind,
    IReadOnlyDictionary<string, Clip> Clips, IReadOnlyDictionary<string, DecodedImage> Images,
    IReadOnlyDictionary<string, string> DisabledActions)
{
    public int SchemaVersion { get; init; } = 1;
    public string ManifestSha256 { get; init; } = "";
}
public sealed class PackageException(string category) : Exception(category);
public static class PackageLoader
{
    private static readonly Dictionary<string, bool> Modes = new(StringComparer.Ordinal)
    {
        ["neutral"] = true, ["idle-soft"] = true, ["idle-smile"] = false,
        ["drag-pickup"] = false, ["drag-hold"] = true, ["drag-release"] = false
    };
    public static AssetPackage Load(string root, Func<byte[], DecodedImage> decode)
    {
        try { return LoadCore(root, decode); }
        catch (PackageException) { throw; }
        catch (Exception ex) when (ex is JsonException or IOException or UnauthorizedAccessException or ArgumentException or OverflowException)
        { throw new PackageException("package-format-or-access"); }
    }
    private static AssetPackage LoadCore(string root, Func<byte[], DecodedImage> decode)
    {
        using var files = new PackageFiles(root);
        byte[] manifest = files.Read("manifest.json", 64 * 1024);
        var json = manifest.AsMemory();
        if (manifest.AsSpan().StartsWith(new byte[] { 239, 187, 191 })) json = json[3..];
        using var doc = JsonDocument.Parse(json, new JsonDocumentOptions { MaxDepth = 8 });
        var m = doc.RootElement;
        Fields(m, "schemaVersion", "packageId", "packageVersion", "packageKind", "sourceScale", "frameSize", "anchor", "fallbackAction", "actions");
        int schema = Number(m.GetProperty("schemaVersion"), 1, 2); Number(m.GetProperty("sourceScale"), 1, 1);
        var id = Text(m.GetProperty("packageId")); Match(id, "[a-z][a-z0-9-]{0,47}");
        var version = Text(m.GetProperty("packageVersion")); Match(version, "(?:0|[1-9][0-9]{0,3})\\.(?:0|[1-9][0-9]{0,3})\\.(?:0|[1-9][0-9]{0,3})");
        var kind = Text(m.GetProperty("packageKind")); Require(kind is "diagnostic" or "character");
        var size = m.GetProperty("frameSize"); Fields(size, "width", "height"); Number(size.GetProperty("width"), 96, 96); Number(size.GetProperty("height"), 104, 104);
        var anchor = m.GetProperty("anchor"); Fields(anchor, "x", "y"); Number(anchor.GetProperty("x"), 48, 48); Number(anchor.GetProperty("y"), 94, 94);
        Require(Text(m.GetProperty("fallbackAction")) == "neutral");
        var actions = m.GetProperty("actions"); Require(actions.ValueKind == JsonValueKind.Object);
        var clips = new Dictionary<string, Clip>(StringComparer.Ordinal);
        var paths = new HashSet<string>(StringComparer.Ordinal); int totalFrames = 0;
        IReadOnlyList<Frame> ReadFrames(JsonElement array)
        {
            Require(array.ValueKind == JsonValueKind.Array && array.GetArrayLength() is >= 1 and <= 64);
            var result = new List<Frame>(); int duration = 0;
            foreach (var frame in array.EnumerateArray())
            {
                Fields(frame, "path", "durationMs"); var path = ValidPath(Text(frame.GetProperty("path")));
                int ms = Number(frame.GetProperty("durationMs"), 1, 10000);
                duration = checked(duration + ms); Require(duration <= 60000);
                result.Add(new(path, ms)); paths.Add(path);
            }
            totalFrames = checked(totalFrames + result.Count); Require(totalFrames <= 256 && paths.Count <= 128);
            return result.AsReadOnly();
        }
        foreach (var action in actions.EnumerateObject())
        {
            Require(Modes.ContainsKey(action.Name) && !clips.ContainsKey(action.Name));
            Require(action.Value.ValueKind == JsonValueKind.Object);
            bool hasEntries = schema == 2 && action.Name == "drag-release" && action.Value.TryGetProperty("entrySequences", out _);
            if (hasEntries) Fields(action.Value, "playback", "origin", "frames", "entrySequences");
            else Fields(action.Value, "playback", "origin", "frames");
            bool loop = Modes[action.Name]; Require(Text(action.Value.GetProperty("playback")) == (loop ? "loop" : "once"));
            var origin = kind == "diagnostic" ? "diagnostic" : action.Name == "idle-smile" ? "adaptation" : "original";
            Require(Text(action.Value.GetProperty("origin")) == origin);
            var frames = ReadFrames(action.Value.GetProperty("frames"));
            if (action.Name == "neutral") Require(frames.Count == 1);
            var entries = new Dictionary<string, IReadOnlyList<Frame>>(StringComparer.Ordinal);
            if (hasEntries)
            {
                var obj = action.Value.GetProperty("entrySequences"); Require(obj.ValueKind == JsonValueKind.Object);
                foreach (var entry in obj.EnumerateObject())
                {
                    string source = ValidPath(entry.Name); Require(!entries.ContainsKey(source));
                    var sequence = ReadFrames(entry.Value); Require(sequence[0].Path == source);
                    entries.Add(source, sequence);
                }
            }
            clips.Add(action.Name, new(action.Name, loop, frames) { EntrySequences = entries.AsReadOnly() });
        }
        Require(clips.Count is >= 1 and <= 6 && clips.ContainsKey("neutral"));
        foreach (var clip in clips.Values)
            foreach (var entry in clip.EntrySequences.Values) Require(entry[^1].Path == clips["neutral"].Frames[0].Path);
        // Complete all path/size validation before invoking an image decoder.
        var bytes = new Dictionary<string, byte[]>(StringComparer.Ordinal);
        var bad = new HashSet<string>(StringComparer.Ordinal); long compressedTotal = 0;
        foreach (var path in paths)
        {
            try
            {
                var buffer = files.Read(path, 256 * 1024); compressedTotal += buffer.Length;
                Require(compressedTotal <= 8 * 1024 * 1024); bytes.Add(path, buffer);
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException) { bad.Add(path); }
        }
        var images = new Dictionary<string, DecodedImage>(StringComparer.Ordinal);
        foreach (var (path, buffer) in bytes)
        {
            try
            {
                var image = decode(buffer);
                if (image.Width != 96 || image.Height != 104 || image.Bgra.Length != 96 * 104 * 4) throw new InvalidDataException();
                bool visible = false;
                for (int i = 3; i < image.Bgra.Length; i += 4)
                {
                    if (image.Bgra[i] is not (0 or 255)) throw new InvalidDataException();
                    visible |= image.Bgra[i] == 255;
                }
                if (!visible) throw new InvalidDataException();
                images.Add(path, image);
            }
            catch (Exception ex) when (ex is InvalidDataException or NotSupportedException or ArgumentException or IOException or System.Runtime.InteropServices.COMException)
            { bad.Add(path); }
        }
        Require(!clips["neutral"].Frames.Any(f => bad.Contains(f.Path)));
        var disabled = new Dictionary<string, string>(StringComparer.Ordinal);
        foreach (var clip in clips.Values.ToArray())
            if (clip.Frames.Concat(clip.EntrySequences.Values.SelectMany(f => f)).Any(f => bad.Contains(f.Path)))
            { disabled.Add(clip.Id, "invalid-image"); clips.Remove(clip.Id); }
        return new(id, version, kind, clips.AsReadOnly(), images.AsReadOnly(), disabled.AsReadOnly())
        { SchemaVersion = schema, ManifestSha256 = Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(manifest)) };
    }
    private static string ValidPath(string path)
    {
        Match(path, "frames/[a-z0-9][a-z0-9_-]{0,63}\\.png");
        Require(!Regex.IsMatch(Path.GetFileNameWithoutExtension(path), "\\A(?:con|prn|aux|nul|com[1-9]|lpt[1-9])\\z", RegexOptions.CultureInvariant));
        return path;
    }
    private static void Require(bool condition) { if (!condition) throw new PackageException("package-format-or-limit"); }
    private static void Match(string value, string pattern) => Require(Regex.IsMatch(value, "\\A(?:" + pattern + ")\\z", RegexOptions.CultureInvariant));
    private static string Text(JsonElement e) { Require(e.ValueKind == JsonValueKind.String); return e.GetString()!; }
    private static int Number(JsonElement e, int min, int max)
    {
        Require(e.ValueKind == JsonValueKind.Number);
        // Avoid rounding a fractional JSON number to an integer through double/decimal.
        var parts = e.GetRawText().ToLowerInvariant().Split('e');
        long exponent = 0;
        Require(parts.Length == 1 || long.TryParse(parts[1], System.Globalization.NumberStyles.AllowLeadingSign, System.Globalization.CultureInfo.InvariantCulture, out exponent));
        Require(exponent is >= -100000 and <= 100000 && !parts[0].StartsWith('-'));
        var dot = parts[0].IndexOf('.');
        int fractional = dot < 0 ? 0 : parts[0].Length - dot - 1;
        var digits = parts[0].Replace(".", "").TrimStart('0');
        var significant = digits.TrimEnd('0');
        long shift = exponent - fractional + digits.Length - significant.Length;
        Require(significant.Length > 0 && shift >= 0 && significant.Length + shift <= 5);
        int n = int.Parse(significant, System.Globalization.CultureInfo.InvariantCulture);
        for (int i = 0; i < shift; i++) n *= 10;
        Require(n >= min && n <= max); return n;
    }
    private static void Fields(JsonElement e, params string[] names)
    {
        Require(e.ValueKind == JsonValueKind.Object);
        var found = new HashSet<string>(StringComparer.Ordinal);
        foreach (var p in e.EnumerateObject()) Require(names.Contains(p.Name, StringComparer.Ordinal) && found.Add(p.Name));
        Require(found.Count == names.Length);
    }
}

public sealed class PackageSession
{
    public AssetPackage? Current { get; private set; }
    public string? Error { get; private set; }
    public bool TryLoad(string root, Func<byte[], DecodedImage> decode)
    {
        try { var next = PackageLoader.Load(root, decode); Current = next; Error = null; return true; }
        catch (PackageException ex) { Error = ex.Message; return false; }
    }
}
