using Aemeath.Presentation;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace Aemeath.Tests;

[TestClass]
public class BehaviorControllerTests
{
    [TestMethod] public void IndependentTracksContinueThroughBlinkAndRandomBoundsAreInclusive()
    {
        using var f=new BehaviorFixture(); long now=0; var calls=new List<(int,int)>();
        var c=new CharacterController(f.Load(),()=>now,3,(min,max)=>{calls.Add((min,max));return min;}); c.SetAutomatic(true);
        foreach(var (time,key) in new (long,string)[]{(0,"A-open-base"),(400,"B-open-light"),(550,"C-open-upper"),(1100,"B-open-upper"),(1200,"B-open-light"),(1250,"A-open-light"),(1350,"A-open-base"),(4000,"B-half-light"),(4060,"A-closed-light"),(4140,"A-half-light"),(4200,"A-open-base"),(4240,"A-open-base")})
        { now=time; Assert.AreEqual(BehaviorFixture.PathFor("idle:"+key),c.Sample().FramePath,$"t={time}"); }
        CollectionAssert.AreEqual(new[]{(4000,7000),(50000,69999),(4000,7000)},calls);
        now=50000; Assert.AreEqual(BehaviorFixture.PathFor("idle:C-mid-upper"),c.Sample().FramePath); // both overdue, wink wins
        now=51200; c.Sample(); Assert.AreEqual(5,calls.Count);
    }
    [TestMethod] public void StartedBlinkFinishesBeforeOverdueWinkAndLateSamplingDoesNotReplay()
    {
        using var f=new BehaviorFixture(); long now=0; var c=new CharacterController(f.Load(),()=>now,0,(a,b)=>a); c.SetAutomatic(true);
        now=49900; c.Sample(); // first late blink starts now; wink not due yet
        now=50000; StringAssert.Contains(c.Sample().FramePath,"closed");
        now=50140; StringAssert.Contains(c.Sample().FramePath,"mid");
        now=1_000_000; var late=c.Sample(); StringAssert.Contains(late.FramePath,"mid"); Assert.IsNotNull(late.CompletedId);
        Assert.IsNull(c.Sample().CompletedId);
    }
    [TestMethod] public void CapturedSourceSurvivesQuickReleaseUnpaintedBoundaryAndRegrab()
    {
        using var f=new BehaviorFixture(); long now=0; var c=new CharacterController(f.Load(),()=>now,8,(a,b)=>a); c.SetAutomatic(true);
        now=550; c.CommitRendered(c.Sample()); c.BeginDrag(); now=590; c.EndDrag();
        var release=c.Sample(); Assert.AreEqual(BehaviorFixture.PathFor("idle:C-open-upper"),release.FramePath);
        now=649; Assert.AreEqual(release.FramePath,c.Sample().FramePath); now=650; c.CommitRendered(c.Sample());
        now=700; c.EndDrag(); Assert.AreEqual(release.PlaybackId,c.Sample().PlaybackId);
        c.BeginDrag(); Assert.AreEqual(BehaviorFixture.PathFor("pose:normal-normal-H"),c.Sample().FramePath);
        now=1129; Assert.AreNotEqual(release.PlaybackId,c.Sample().CompletedId);
        now=1400; c.CommitRendered(c.Sample()); Assert.AreEqual("drag-hold",c.Sample().Action);
        now=1950; c.Sample(); // C sampled but not submitted; release must use submitted A
        c.EndDrag(); Assert.AreEqual(BehaviorFixture.PathFor("pose:annoyed-annoyed-A"),c.Sample().FramePath);
        now=2210; Assert.AreEqual(BehaviorFixture.PathFor("pose:normal-half-B"),c.Sample().FramePath);
        now=2490; var idle=c.Sample(); Assert.AreEqual(BehaviorFixture.PathFor(BehaviorFixture.Neutral),idle.FramePath); Assert.IsNotNull(idle.CompletedId);
    }
    [TestMethod] public void ModeAndPackageInvalidateSamplesAndManualUsesBase()
    {
        using var f=new BehaviorFixture(); var package=f.Load(); long now=0;
        var c=new CharacterController(package,()=>now,1,(a,b)=>b); c.SetAutomatic(true); var sample=c.Sample(); c.CommitRendered(sample with {}); Assert.IsNull(c.LastSubmitted);
        c.CommitRendered(sample); c.SetAutomatic(false); Assert.IsNull(c.LastSubmitted); c.CommitRendered(sample); Assert.IsNull(c.LastSubmitted);
        c.PlayManual("drag-release"); Assert.AreEqual(BehaviorFixture.PathFor(BehaviorFixture.Neutral),c.Sample().FramePath); now=60; Assert.AreEqual(BehaviorFixture.PathFor("pose:normal-normal-H"),c.Sample().FramePath);
        var next=new CharacterController(package,()=>now,2,(a,b)=>b); next.SetAutomatic(true); next.CommitRendered(sample); next.BeginDrag(); next.EndDrag(); Assert.AreEqual("no-submitted-frame",next.ReleaseFallback);
        Assert.AreEqual(BehaviorFixture.PathFor(BehaviorFixture.Neutral),next.Sample().FramePath);
        now=600; next.Sample(); now=7599; StringAssert.Contains(next.Sample().FramePath,"open"); now=7600; StringAssert.Contains(next.Sample().FramePath,"half");
    }
}
