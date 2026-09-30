using System.IO;
using System.IO.Compression;
using System.Text;
using System.Text.Json.Nodes;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using Aemeath.Host;
using Aemeath.Presentation;

namespace Aemeath.Tests;

[TestClass]
public class PackageTests
{
    private string root = null!;
    private JsonObject manifest = null!;
    [TestInitialize] public void Setup()
    {
        root = Path.Combine(Path.GetTempPath(), "aemeath-tests-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(Path.Combine(root, "frames"));
        manifest = JsonNode.Parse("""
        {"schemaVersion":1,"packageId":"diagnostic-v1","packageVersion":"0.1.0","packageKind":"diagnostic","sourceScale":1,
        "frameSize":{"width":96,"height":104},"anchor":{"x":48,"y":94},"fallbackAction":"neutral","actions":{
        "neutral":{"playback":"loop","origin":"diagnostic","frames":[{"path":"frames/neutral.png","durationMs":1000}]},
        "idle-soft":{"playback":"loop","origin":"diagnostic","frames":[{"path":"frames/shared.png","durationMs":100}]},
        "idle-smile":{"playback":"once","origin":"diagnostic","frames":[{"path":"frames/shared.png","durationMs":100}]}}}
        """)!.AsObject();
        File.WriteAllBytes(Path.Combine(root, "frames/neutral.png"), Png());
        File.WriteAllBytes(Path.Combine(root, "frames/shared.png"), Png());
    }
    [TestCleanup] public void Cleanup() => Directory.Delete(root, true);
    private AssetPackage Load()
    {
        File.WriteAllText(Path.Combine(root, "manifest.json"), manifest.ToJsonString());
        return PackageLoader.Load(root, PngDecoder.Decode);
    }
    [TestMethod] public void ValidSubsetCachesDistinctImages()
    {
        var package = Load(); Assert.AreEqual(3, package.Clips.Count); Assert.AreEqual(2, package.Images.Count);
        Assert.AreEqual(0, package.DisabledActions.Count); Assert.AreEqual(96 * 104 * 4, package.Images["frames/neutral.png"].Bgra.Length);
    }
    [TestMethod] public void SharedBadImageDisablesWholeReferencingActions()
    {
        File.WriteAllBytes(Path.Combine(root, "frames/shared.png"), [1, 2, 3]);
        var package = Load(); Assert.AreEqual(1, package.Clips.Count); Assert.AreEqual(2, package.DisabledActions.Count);
        Assert.IsTrue(package.Clips.ContainsKey("neutral"));
    }
    [TestMethod] public void MissingNonneutralDisablesButMissingNeutralRejects()
    {
        File.Delete(Path.Combine(root, "frames/shared.png")); Assert.AreEqual(2, Load().DisabledActions.Count);
        File.Delete(Path.Combine(root, "frames/neutral.png")); Assert.ThrowsExactly<PackageException>(() => Load());
    }
    [TestMethod] public void BadNeutralRejectsWholePackage()
    {
        File.WriteAllBytes(Path.Combine(root, "frames/neutral.png"), Png(alpha: 0));
        Assert.ThrowsExactly<PackageException>(() => Load());
    }
    [TestMethod] public void UnknownFieldAndWrongDurationReject()
    {
        manifest["unexpected"] = true; Assert.ThrowsExactly<PackageException>(() => Load()); manifest.Remove("unexpected");
        manifest["actions"]!["idle-soft"]!["frames"]![0]!["durationMs"] = 0;
        Assert.ThrowsExactly<PackageException>(() => Load());
    }
    [TestMethod] public void DuplicatePropertiesRejectButMathematicalIntegersAndBomWork()
    {
        Load(); var path = Path.Combine(root, "manifest.json"); var json = File.ReadAllText(path);
        File.WriteAllText(path, json.Replace("\"schemaVersion\":1", "\"schemaVersion\":1.0e0"), new UTF8Encoding(true));
        Assert.AreEqual(3, PackageLoader.Load(root, PngDecoder.Decode).Clips.Count);
        File.WriteAllText(path, json.Replace("\"schemaVersion\":1", "\"schemaVersion\":1,\"schemaVersion\":1"));
        Assert.ThrowsExactly<PackageException>(() => PackageLoader.Load(root, PngDecoder.Decode));
    }
    [TestMethod] public void UnsafePathsRejectedBeforeDecoder()
    {
        foreach (var path in new[] { "../outside.png", "frames/con.png", "frames/UPPER.png", "frames/shared.png\n", "frames/a:ads.png" })
        {
            manifest["actions"]!["idle-soft"]!["frames"]![0]!["path"] = path;
            Assert.ThrowsExactly<PackageException>(() => Load(), path);
        }
    }
    [TestMethod] public void ResourceLimitRejectsEvenNonneutral()
    {
        File.WriteAllBytes(Path.Combine(root, "frames/shared.png"), new byte[256 * 1024 + 1]);
        Assert.ThrowsExactly<PackageException>(() => Load());
    }
    [TestMethod] public void CaseMismatchIsPathErrorNotDegradedImage()
    {
        File.Move(Path.Combine(root, "frames/shared.png"), Path.Combine(root, "frames/Shared.png"));
        Assert.ThrowsExactly<PackageException>(() => Load());
    }
    [TestMethod] public void FractionalNumberCannotRoundToAnInteger()
    {
        Load(); var path = Path.Combine(root, "manifest.json");
        File.WriteAllText(path, File.ReadAllText(path).Replace("\"schemaVersion\":1", "\"schemaVersion\":1.00000000000000000000000000001"));
        Assert.ThrowsExactly<PackageException>(() => PackageLoader.Load(root, PngDecoder.Decode));
    }
    [TestMethod] public void InvalidReloadKeepsPriorPackageAndFirstFailureHasNoPackage()
    {
        Load(); var session = new PackageSession(); Assert.IsTrue(session.TryLoad(root, PngDecoder.Decode));
        var prior = session.Current; File.Delete(Path.Combine(root, "frames/neutral.png"));
        Assert.IsFalse(session.TryLoad(root, PngDecoder.Decode)); Assert.AreSame(prior, session.Current);
        var empty = new PackageSession(); Assert.IsFalse(empty.TryLoad(root, PngDecoder.Decode)); Assert.IsNull(empty.Current); Assert.IsNotNull(empty.Error);
    }
    [TestMethod] public void RealDecoderRejectsPartialAlphaWrongSizeApngAndCrc()
    {
        Assert.AreEqual(96, PngDecoder.Decode(Png()).Width);
        foreach (var bytes in new[] { Png(alpha: 128), Png(width: 95), Png(apng: true), Png(alpha: 0) })
            Assert.ThrowsExactly<InvalidDataException>(() => PngDecoder.Decode(bytes));
        var corrupt = Png(); corrupt[^1] ^= 1;
        Assert.ThrowsExactly<InvalidDataException>(() => PngDecoder.Decode(corrupt));
    }
    // Synthetic solid test pixels; never character artwork. Encode RGBA8 directly to exercise the actual WPF decoder.
    internal static byte[] Png(byte alpha = 255, int width = 96, bool apng = false)
    {
        using var output = new MemoryStream(); output.Write(new byte[] {137,80,78,71,13,10,26,10});
        void Chunk(string type, byte[] data)
        {
            var name = Encoding.ASCII.GetBytes(type); var len = BitConverter.GetBytes(System.Net.IPAddress.HostToNetworkOrder(data.Length)); output.Write(len); output.Write(name); output.Write(data);
            uint crc = 0xffffffff; foreach (byte b in name.Concat(data)) { crc ^= b; for (int i = 0; i < 8; i++) crc = (crc >> 1) ^ ((crc & 1) == 1 ? 0xedb88320u : 0); }
            output.Write(BitConverter.GetBytes(System.Net.IPAddress.HostToNetworkOrder(unchecked((int)~crc))));
        }
        var header = new byte[13]; System.Buffers.Binary.BinaryPrimitives.WriteInt32BigEndian(header, width); System.Buffers.Binary.BinaryPrimitives.WriteInt32BigEndian(header.AsSpan(4), 104); header[8] = 8; header[9] = 6; Chunk("IHDR", header);
        if (apng) Chunk("acTL", new byte[8]);
        using var compressed = new MemoryStream();
        using (var zip = new ZLibStream(compressed, CompressionLevel.SmallestSize, true))
            for (var y = 0; y < 104; y++) { zip.WriteByte(0); for (var x = 0; x < width; x++) zip.Write(new byte[] {255,64,32,alpha}); }
        Chunk("IDAT", compressed.ToArray()); Chunk("IEND", []); return output.ToArray();
    }
}
