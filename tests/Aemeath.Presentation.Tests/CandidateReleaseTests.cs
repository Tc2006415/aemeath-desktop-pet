using System.IO;
using System.Text.Json;
using Aemeath.Host;
using Aemeath.Presentation;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace Aemeath.Tests;

[TestClass]
public class CandidateReleaseTests
{
    public TestContext TestContext { get; set; } = null!;
    [TestMethod] public void Art019ActualLoaderAndEveryEntryPathDeadline()
    {
        var root=Environment.GetEnvironmentVariable("AEMEATH_RELEASE_PACKAGE");
        if (string.IsNullOrWhiteSpace(root)) { Assert.Inconclusive("Set AEMEATH_RELEASE_PACKAGE to fixed ART019 directory."); return; }
        var package=PackageLoader.Load(root,PngDecoder.Decode);
        Assert.AreEqual("aemeath-v1",package.Id); Assert.AreEqual("0.4.0",package.Version); Assert.AreEqual(2,package.SchemaVersion);
        Assert.AreEqual("EAB91ECB10037DA7320D4E9C9321C8DCE0F122D3B9D5DAA6E101A55E1E319DA3",package.ManifestSha256);
        Assert.AreEqual(0,package.DisabledActions.Count); Assert.AreEqual(16,package.Images.Count);
        var release=package.Clips["drag-release"]; Assert.AreEqual(16,release.EntrySequences.Count);
        Assert.AreEqual(20,package.Clips["drag-hold"].Frames.Count); Assert.AreEqual(1440,package.Clips["drag-hold"].DurationMs);
        Assert.AreEqual(104,package.Clips.Values.Sum(c=>c.Frames.Count+c.EntrySequences.Values.Sum(e=>e.Count)));
        var evidence=new List<object>();
        foreach(var (source,sequence) in release.EntrySequences)
        {
            var owner=new[]{"idle-soft","idle-smile","drag-pickup","drag-hold","drag-release"}.Select(id=>package.Clips[id]).First(c=>c.Frames.Any(f=>f.Path==source));
            int offset=owner.Frames.TakeWhile(f=>f.Path!=source).Sum(f=>f.DurationMs);
            long now=0; var c=new CharacterController(package.Clips,()=>now,99); c.SetAutomatic(true);
            // Real candidate sequences with a controlled submission acknowledgment, not simulated native input.
            if(owner.Id=="idle-smile") { now=15000; c.Sample(); }
            if(owner.Id is "drag-pickup" or "drag-hold") c.BeginDrag();
            if(owner.Id=="drag-hold") { now=package.Clips["drag-pickup"].DurationMs; c.Sample(); }
            if(owner.Id=="drag-release") { c.BeginDrag(); c.EndDrag(); }
            now+=offset;
            var rendered=c.Sample(); Assert.AreEqual(source,rendered.FramePath);
            c.CommitRendered(rendered);
            if(owner.Id is not ("drag-pickup" or "drag-hold")) c.BeginDrag();
            c.EndDrag(); long start=now; long id=c.Sample().PlaybackId;
            Assert.IsNull(c.ReleaseFallback,source);
            int cursor=0;
            foreach(var frame in sequence)
            {
                now=start+cursor; Assert.AreEqual(frame.Path,c.Sample().FramePath,source);
                now=start+cursor+frame.DurationMs-1; Assert.AreEqual(frame.Path,c.Sample().FramePath,source);
                cursor+=frame.DurationMs;
            }
            now=start+cursor; var end=c.Sample(); Assert.AreEqual(id,end.CompletedId); Assert.AreEqual("idle-soft",end.Action);
            Assert.IsNull(c.Sample().CompletedId);
            evidence.Add(new { source,totalMs=cursor,paths=sequence.Select(f=>f.Path).ToArray() });
        }
        TestContext.WriteLine(JsonSerializer.Serialize(new { package.Id,package.Version,package.SchemaVersion,package.ManifestSha256,entries=evidence }));
    }
}
