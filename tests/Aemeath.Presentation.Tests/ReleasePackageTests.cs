using System.IO;
using System.Text.Json.Nodes;
using Aemeath.Host;
using Aemeath.Presentation;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace Aemeath.Tests;

[TestClass]
public class ReleasePackageTests
{
    private string root = null!;
    private JsonObject manifest = null!;
    private JsonObject Entries => manifest["actions"]!["drag-release"]!["entrySequences"]!.AsObject();
    [TestInitialize] public void Setup()
    {
        root = Path.Combine(Path.GetTempPath(), "aemeath-release-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(Path.Combine(root, "frames"));
        foreach (var name in new[] { "neutral", "up", "bridge" }) File.WriteAllBytes(Path.Combine(root, "frames", name + ".png"), PackageTests.Png());
        manifest = JsonNode.Parse("""
        {"schemaVersion":2,"packageId":"diagnostic-release","packageVersion":"0.4.0","packageKind":"diagnostic","sourceScale":1,
        "frameSize":{"width":96,"height":104},"anchor":{"x":48,"y":94},"fallbackAction":"neutral","actions":{
        "neutral":{"playback":"loop","origin":"diagnostic","frames":[{"path":"frames/neutral.png","durationMs":1000}]},
        "drag-hold":{"playback":"loop","origin":"diagnostic","frames":[{"path":"frames/up.png","durationMs":180}]},
        "drag-release":{"playback":"once","origin":"diagnostic","frames":[{"path":"frames/neutral.png","durationMs":460}],"entrySequences":{
        "frames/up.png":[{"path":"frames/up.png","durationMs":40},{"path":"frames/bridge.png","durationMs":40},{"path":"frames/neutral.png","durationMs":160}]}}}}
        """)!.AsObject();
    }
    [TestCleanup] public void Cleanup() => Directory.Delete(root, true);
    private AssetPackage Load()
    {
        File.WriteAllText(Path.Combine(root, "manifest.json"), manifest.ToJsonString());
        return PackageLoader.Load(root, PngDecoder.Decode);
    }
    [TestMethod] public void SchemaTwoLoadsEntryOnlyImageAndSchemaOneStillWorks()
    {
        var package = Load(); Assert.AreEqual(3, package.Images.Count);
        Assert.AreEqual(240, package.Clips["drag-release"].EntrySequences["frames/up.png"].Sum(f => f.DurationMs));
        manifest["actions"]!["drag-release"]!.AsObject().Remove("entrySequences");
        Assert.AreEqual(0, Load().Clips["drag-release"].EntrySequences.Count);
        manifest["schemaVersion"] = 1; Assert.AreEqual(0, Load().Clips["drag-release"].EntrySequences.Count);
    }
    [TestMethod] public void EntriesOnlyAllowedOnSchemaTwoRelease()
    {
        manifest["schemaVersion"] = 1; Assert.ThrowsExactly<PackageException>(() => Load());
        manifest["schemaVersion"] = 2;
        manifest["actions"]!["drag-hold"]!["entrySequences"] = Entries.DeepClone();
        Assert.ThrowsExactly<PackageException>(() => Load());
    }
    [TestMethod] public void BadEntryImageDisablesEntireReleaseButBadNeutralRejects()
    {
        File.WriteAllBytes(Path.Combine(root, "frames/bridge.png"), [0]);
        var package = Load(); Assert.IsFalse(package.Clips.ContainsKey("drag-release")); Assert.IsTrue(package.Clips.ContainsKey("drag-hold"));
        Assert.IsTrue(package.DisabledActions.ContainsKey("drag-release"));
        File.WriteAllBytes(Path.Combine(root, "frames/neutral.png"), [0]); Assert.ThrowsExactly<PackageException>(() => Load());
    }
    [TestMethod] public void EntryFirstLastPathAndSourcePathMustBeValid()
    {
        var original = Entries["frames/up.png"]!.DeepClone();
        Entries["frames/up.png"]![0]!["path"] = "frames/bridge.png"; Assert.ThrowsExactly<PackageException>(() => Load());
        Entries["frames/up.png"] = original.DeepClone(); Entries["frames/up.png"]![2]!["path"] = "frames/bridge.png";
        Assert.ThrowsExactly<PackageException>(() => Load());
        Entries.Clear(); Entries["../escape.png"] = original; Assert.ThrowsExactly<PackageException>(() => Load());
    }
    [TestMethod] public void EntryLimitsIncludeVariantItemsAndUnknownFields()
    {
        var original = Entries["frames/up.png"]!.DeepClone();
        Entries["frames/up.png"]![0]!["unknown"] = 1; Assert.ThrowsExactly<PackageException>(() => Load());
        Entries["frames/up.png"] = original.DeepClone(); Entries["frames/up.png"]![0]!["durationMs"] = 0;
        Assert.ThrowsExactly<PackageException>(() => Load());
        var oversized = new JsonArray(); for (int i = 0; i < 65; i++) oversized.Add(new JsonObject { ["path"]="frames/up.png", ["durationMs"]=1 });
        oversized[64]!["path"] = "frames/neutral.png"; Entries["frames/up.png"] = oversized;
        Assert.ThrowsExactly<PackageException>(() => Load());
        var longClip = new JsonArray(); for (int i = 0; i < 7; i++) longClip.Add(new JsonObject { ["path"]="frames/up.png", ["durationMs"]=10000 });
        longClip[6]!["path"]="frames/neutral.png"; Entries["frames/up.png"] = longClip;
        Assert.ThrowsExactly<PackageException>(() => Load());
    }
    [TestMethod] public void DuplicateEntryKeyRejects()
    {
        Load(); var path=Path.Combine(root,"manifest.json"); var json=File.ReadAllText(path);
        var marker="\"entrySequences\":{";
        json=json.Replace(marker,marker+"\"frames/up.png\":"+Entries["frames/up.png"]!.ToJsonString()+","); File.WriteAllText(path,json);
        Assert.ThrowsExactly<PackageException>(() => PackageLoader.Load(root,PngDecoder.Decode));
    }
    [TestMethod] public void TotalItemLimitCountsEveryEntryIncludingReusedPng()
    {
        Entries.Clear(); File.WriteAllBytes(Path.Combine(root,"frames/extra.png"),PackageTests.Png());
        var keys = new[] { "up", "bridge", "neutral", "extra" };
        for (int i=0;i<keys.Length;i++)
        {
            var sequence=new JsonArray(); int count=i==3?61:64;
            for(int n=0;n<count;n++) sequence.Add(new JsonObject { ["path"]=$"frames/{keys[i]}.png", ["durationMs"]=1 });
            sequence[count-1]!["path"]="frames/neutral.png"; Entries[$"frames/{keys[i]}.png"]=sequence;
        }
        Assert.AreEqual(4,Load().Clips["drag-release"].EntrySequences.Count); // 253 + 3 base = 256
        Entries["frames/extra.png"]!.AsArray().Add(new JsonObject { ["path"]="frames/neutral.png",["durationMs"]=1 });
        Assert.ThrowsExactly<PackageException>(()=>Load());
    }
}
