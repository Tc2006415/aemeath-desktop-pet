using Aemeath.Presentation;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace Aemeath.Tests;

internal static class ReleaseFixtures
{
    internal static string P(string name) => $"frames/{name}.png";
    internal static Frame F(string name,int ms) => new(P(name),ms);
    internal static readonly (string Name,int Duration)[] Deadlines = [("hold-up-half",620),("high",580),("mid",540),("low",500),("hold-half",460),("hold-down-half",500),("hold-mid-closed",460),("hold-surprise",500),("pickup-surprise",500),("neutral",160),("release-closed",380),("release-half",280),("soft-light",200),("soft-peak",200),("smile-half",200),("smile-closed",200)];
    internal static Dictionary<string,Clip> Clips()
    {
        Frame[] r=[F("hold-half",80),F("release-closed",100),F("release-half",120),F("neutral",160)];
        var entries=new Dictionary<string,IReadOnlyList<Frame>>();
        entries[P("hold-up-half")]=new[]{F("hold-up-half",40),F("high",40),F("mid",40),F("low",40)}.Concat(r).ToArray();
        entries[P("high")]=new[]{F("high",40),F("mid",40),F("low",40)}.Concat(r).ToArray();
        entries[P("mid")]=new[]{F("mid",40),F("low",40)}.Concat(r).ToArray();
        entries[P("low")]=new[]{F("low",40)}.Concat(r).ToArray();
        entries[P("hold-half")]=r;
        foreach(var name in new[]{"hold-down-half","hold-surprise","pickup-surprise"}) entries[P(name)]=new[]{F(name,40)}.Concat(r).ToArray();
        entries[P("hold-mid-closed")]=[F("hold-mid-closed",80),..r.Skip(1)];
        entries[P("neutral")]=[F("neutral",160)];
        entries[P("release-closed")]=r.Skip(1).ToArray(); entries[P("release-half")]=r.Skip(2).ToArray();
        foreach(var name in new[]{"soft-light","soft-peak","smile-half","smile-closed"}) entries[P(name)]=[F(name,40),F("neutral",160)];
        return new()
        {
            ["neutral"]=new("neutral",true,[F("neutral",1000)]),
            ["idle-soft"]=new("idle-soft",true,[F("soft-light",400),F("soft-peak",200)]),
            ["idle-smile"]=new("idle-smile",false,[F("smile-half",120),F("smile-closed",500)]),
            ["drag-pickup"]=new("drag-pickup",false,[F("neutral",80),F("hold-surprise",80),F("pickup-surprise",100),F("hold-half",100)]),
            ["drag-hold"]=new("drag-hold",true,[F("hold-up-half",180),F("hold-down-half",180)]),
            ["drag-release"]=new("drag-release",false,r){EntrySequences=entries.AsReadOnly()}
        };
    }
}

[TestClass]
public class ReleaseControllerTests
{
    [TestMethod] public void SixteenSourcesKeepFirstPathAndCompleteAtTheirOwnDeadline()
    {
        foreach(var (name,duration) in ReleaseFixtures.Deadlines)
        {
            long now=0; var clips=ReleaseFixtures.Clips();
            clips["drag-hold"]=new("drag-hold",true,[ReleaseFixtures.F(name,10000)]);
            var c=new CharacterController(clips,()=>now,7); c.SetAutomatic(true); c.BeginDrag(); now=360;
            var drawn=c.Sample(); c.CommitRendered(drawn); Assert.AreEqual(7L,c.LastSubmitted!.PackageEpoch);
            c.EndDrag(); var start=c.Sample(); long instance=start.PlaybackId;
            Assert.AreEqual(ReleaseFixtures.P(name),start.FramePath,name); Assert.AreEqual("drag-release",start.Action);
            now=360+duration-1; Assert.AreEqual(instance,c.Sample().PlaybackId,name);
            now++; var end=c.Sample(); Assert.AreEqual("idle-soft",end.Action,name); Assert.AreEqual(instance,end.CompletedId,name);
            Assert.IsNull(c.Sample().CompletedId,name);
        }
    }
    [TestMethod] public void CrossingUnrenderedBoundaryUsesLastSubmittedImage()
    {
        long now=0; var c=new CharacterController(ReleaseFixtures.Clips(),()=>now); c.SetAutomatic(true); c.BeginDrag();
        now=360; c.CommitRendered(c.Sample()); now=540;
        Assert.AreEqual(ReleaseFixtures.P("hold-down-half"),c.Sample().FramePath); // sampled, not assigned to Image.Source
        c.EndDrag(); Assert.AreEqual(ReleaseFixtures.P("hold-up-half"),c.Sample().FramePath);
        now=579; Assert.AreEqual(ReleaseFixtures.P("hold-up-half"),c.Sample().FramePath);
        now=580; Assert.AreEqual(ReleaseFixtures.P("high"),c.Sample().FramePath);
    }
    [TestMethod] public void QuickReleaseDistinguishesSubmittedPickupFromUnrenderedRequest()
    {
        long now=0; var c=new CharacterController(ReleaseFixtures.Clips(),()=>now); c.SetAutomatic(true);
        c.CommitRendered(c.Sample()); c.BeginDrag(); now=40; c.EndDrag();
        Assert.AreEqual(ReleaseFixtures.P("soft-light"),c.Sample().FramePath); now=240; Assert.AreEqual("idle-soft",c.Sample().Action);
        c.BeginDrag(); c.CommitRendered(c.Sample()); now=280; c.EndDrag();
        Assert.AreEqual(ReleaseFixtures.P("neutral"),c.Sample().FramePath); now=439; Assert.AreEqual("drag-release",c.Sample().Action);
        now=440; Assert.AreEqual("idle-soft",c.Sample().Action);
    }
    [TestMethod] public void RepeatedEndAndRegrabCannotCompleteAnOldRelease()
    {
        long now=0; var c=new CharacterController(ReleaseFixtures.Clips(),()=>now); c.SetAutomatic(true); c.BeginDrag();
        now=360; c.CommitRendered(c.Sample()); c.EndDrag(); var release=c.Sample();
        now=400; c.EndDrag(); Assert.AreEqual(release.PlaybackId,c.Sample().PlaybackId);
        c.BeginDrag(); var pickup=c.Sample(); Assert.AreEqual("drag-pickup",pickup.Action);
        now=980; var hold=c.Sample(); Assert.AreEqual("drag-hold",hold.Action); Assert.AreNotEqual(release.PlaybackId,hold.CompletedId);
        Assert.IsNull(c.Sample().CompletedId);
    }
    [TestMethod] public void OnlyOwnedRenderedSamplesSurviveAndModeOrPackageInvalidatesThem()
    {
        long now=0; var clips=ReleaseFixtures.Clips(); var old=new CharacterController(clips,()=>now,1); old.SetAutomatic(true);
        var sample=old.Sample(); old.CommitRendered(sample); old.BeginDrag(); // last committed older ID is still legitimate
        Assert.AreEqual(sample.PlaybackId,old.LastSubmitted!.PlaybackId);
        old.SetAutomatic(false); Assert.IsNull(old.LastSubmitted); old.CommitRendered(sample); Assert.IsNull(old.LastSubmitted);
        var next=new CharacterController(clips,()=>now,2); next.SetAutomatic(true); next.CommitRendered(sample); Assert.IsNull(next.LastSubmitted);
        next.BeginDrag(); next.EndDrag(); Assert.AreEqual("no-submitted-frame",next.ReleaseFallback);
        Assert.AreEqual(ReleaseFixtures.P("hold-half"),next.Sample().FramePath);
    }
    [TestMethod] public void ManualReleaseUsesBaseFramesEvenAfterRenderingAnotherPose()
    {
        long now=0; var c=new CharacterController(ReleaseFixtures.Clips(),()=>now); c.PlayManual("drag-hold"); c.CommitRendered(c.Sample());
        c.PlayManual("drag-release"); Assert.AreEqual(ReleaseFixtures.P("hold-half"),c.Sample().FramePath);
    }
}
