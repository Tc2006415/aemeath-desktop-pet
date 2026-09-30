using System.IO;
using System.Text.Json;
using Aemeath.Host;
using Aemeath.Presentation;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace Aemeath.Tests;

[TestClass]
public class NativeV2CandidateTests
{
    public TestContext TestContext { get; set; }=null!;
    private static string Root()
    {
        var root=Environment.GetEnvironmentVariable("AEMEATH_V2_PACKAGE");
        if(string.IsNullOrEmpty(root)) Assert.Inconclusive("Set AEMEATH_V2_PACKAGE to fixed ART036; no synthetic substitute.");
        return root!;
    }
    [TestMethod] public void ActualCandidateAll64BoundReleasePathsMatchArt035AndCompleteOnce()
    {
        string root=Root(); var p=PackageLoader.Load(root,PngDecoder.Decode); var b=p.Behavior!;
        Assert.AreEqual("95CF8F8102F9631D0A02AE40A46FA497F61D9D423FF350191A399104A0A4B182",p.ManifestSha256);
        Assert.AreEqual("0.5.0",p.Version); Assert.AreEqual(3,p.SchemaVersion); Assert.AreEqual(64,p.Images.Count); Assert.AreEqual(0,p.DisabledActions.Count);
        using var reference=JsonDocument.Parse(File.ReadAllText(Path.Combine(root,"../art035-handoff.json")));
        var expectedRoutes=reference.RootElement.GetProperty("interaction").GetProperty("releaseByCapturedKey");
        foreach(var entry in expectedRoutes.EnumerateObject())
        {
            var bound=b.BindRelease(entry.Name); var expected=entry.Value.EnumerateArray().ToArray();
            Assert.AreEqual(5,bound.Count);
            var clip=new Clip("drag-release",false,bound.Select(s=>new Frame(b.Images[s.Value].Path,s.DurationMs)).ToArray());
            var player=new Playback(new Dictionary<string,Clip>{{"neutral",p.Clips["neutral"]},{"drag-release",clip}});
            long id=player.Play("drag-release",0), t=0;
            for(int i=0;i<bound.Count;i++)
            {
                string key=expected[i].GetProperty("key").GetString()!; int ms=expected[i].GetProperty("durationMs").GetInt32();
                Assert.AreEqual(key,bound[i].Value); Assert.AreEqual(ms,bound[i].DurationMs);
                Assert.AreEqual(b.Images[key].Path,player.Sample(t).FramePath); var last=player.Sample(t+ms-1); Assert.AreEqual(id,last.PlaybackId); Assert.AreEqual(b.Images[key].Path,last.FramePath); t+=ms;
            }
            Assert.AreEqual(540L,t); Assert.AreEqual(id,player.Sample(t).CompletedId); Assert.IsNull(player.Sample(t).CompletedId);
            TestContext.WriteLine(JsonSerializer.Serialize(new { Source=entry.Name,Duration=t,Keys=bound.Select(s=>s.Value),Paths=bound.Select(s=>b.Images[s.Value].Path) }));
        }
    }
    [TestMethod] public void ActualCandidateControllerAndAllManualFramesUseRegisteredKeys()
    {
        var p=PackageLoader.Load(Root(),PngDecoder.Decode); var b=p.Behavior!;
        foreach(var clip in p.Clips.Values)
        {
            long now=0; var c=new CharacterController(p,()=>now); Assert.IsTrue(c.PlayManual(clip.Id));
            foreach(var f in clip.Frames) { var s=c.Sample(); Assert.AreEqual(f.Path,s.FramePath); Assert.AreEqual(f.Path,b.Images[s.FrameKey].Path); c.CommitRendered(s); now+=f.DurationMs; }
        }
        // Real candidate controller transitions. This clock/submission harness is not OS mouse input.
        foreach(long pressAt in new[]{0L,550,4000,50000})
        {
            long now=0; var c=new CharacterController(p,()=>now,17,(a,z)=>a); c.SetAutomatic(true);
            now=pressAt; c.CommitRendered(c.Sample()); string source=c.LastSubmitted!.FrameKey;
            c.BeginDrag(); Assert.AreEqual(source,c.Sample().FrameKey);
            now=pressAt+620; c.CommitRendered(c.Sample()); Assert.AreEqual("pose:transition-annoyed-C",c.LastSubmitted!.FrameKey);
            c.EndDrag(); long id=c.Sample().PlaybackId;
            now+=60; Assert.AreEqual("pose:transition-annoyed-H",c.Sample().FrameKey);
            now=pressAt+620+260; c.CommitRendered(c.Sample()); Assert.AreEqual("pose:normal-half-B",c.LastSubmitted!.FrameKey);
            c.BeginDrag(); Assert.AreEqual("pose:normal-half-B",c.Sample().FrameKey);
            now+=700; var hold=c.Sample(); Assert.AreEqual("held",hold.BehaviorPhase); Assert.AreNotEqual(id,hold.CompletedId);
            c.CommitRendered(hold); c.EndDrag(); long end=now+540; now+=260; Assert.AreEqual("pose:normal-half-B",c.Sample().FrameKey);
            now=end; Assert.AreEqual(b.NeutralKey,c.Sample().FrameKey);
        }
    }
}
