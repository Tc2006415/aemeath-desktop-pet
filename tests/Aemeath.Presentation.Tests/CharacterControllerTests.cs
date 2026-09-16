using Aemeath.Presentation;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace Aemeath.Tests;

[TestClass]
public class CharacterControllerTests
{
    private long now;
    private CharacterController Controller(params string[] missing)
    {
        var clips = new Dictionary<string, Clip>
        {
            ["neutral"] = new("neutral", true, [new("n", 1000)]),
            ["idle-soft"] = new("idle-soft", true, [new("a", 100), new("b", 200)]),
            ["idle-smile"] = new("idle-smile", false, [new("s", 270), new("n", 130)]),
            ["drag-pickup"] = new("drag-pickup", false, [new("p", 70), new("q", 50)]),
            ["drag-hold"] = new("drag-hold", true, [new("h", 180)]),
            ["drag-release"] = new("drag-release", false, [new("r", 80), new("n", 200)])
        };
        foreach (var id in missing) clips.Remove(id);
        return new(clips, () => now);
    }
    [TestMethod] public void AutomaticWaitStartsAtIdleEntryAndResetsAfterSmile()
    {
        var c = Controller(); now = 500; c.SetAutomatic(true);
        Assert.AreEqual("idle-soft", c.Sample().Action);
        now = 15499; Assert.AreEqual("idle-soft", c.Sample().Action);
        now = 15500; Assert.AreEqual("idle-smile", c.Sample().Action);
        now = 15899; Assert.AreEqual("idle-smile", c.Sample().Action);
        now = 15900; Assert.AreEqual("idle-soft", c.Sample().Action);
        now = 30899; Assert.AreEqual("idle-soft", c.Sample().Action);
        now = 30900; Assert.AreEqual("idle-smile", c.Sample().Action);
    }
    [TestMethod] public void PickupUsesManifestDurationAndReleaseRestartsIdleWait()
    {
        var c = Controller(); c.SetAutomatic(true); now = 9000; c.BeginDrag();
        Assert.AreEqual("drag-pickup", c.Sample().Action);
        now = 9119; Assert.AreEqual("drag-pickup", c.Sample().Action);
        now = 9120; Assert.AreEqual("drag-hold", c.Sample().Action);
        now = 20000; Assert.AreEqual("drag-hold", c.Sample().Action); c.EndDrag();
        Assert.AreEqual("drag-release", c.Sample().Action);
        now = 20279; Assert.AreEqual("drag-release", c.Sample().Action);
        now = 20280; Assert.AreEqual("idle-soft", c.Sample().Action);
        now = 35279; Assert.AreEqual("idle-soft", c.Sample().Action);
        now = 35280; Assert.AreEqual("idle-smile", c.Sample().Action);
    }
    [TestMethod] public void EarlyReleaseAndRepeatedCaptureLossDoNotRestartRelease()
    {
        var c = Controller(); c.SetAutomatic(true); c.BeginDrag(); now = 10; c.EndDrag();
        var release = c.Sample(); now = 20; c.EndDrag();
        Assert.AreEqual(release.PlaybackId, c.Sample().PlaybackId);
        now = 120; Assert.AreEqual("drag-release", c.Sample().Action); // old pickup deadline
        now = 290; Assert.AreEqual("idle-soft", c.Sample().Action);
    }
    [TestMethod] public void RegrabCancelsOldReleaseAndOldSmileCannotOverridePickup()
    {
        var c = Controller(); c.SetAutomatic(true); now = 15000; var smile = c.Sample();
        c.BeginDrag(); now = 15010; c.EndDrag(); var release = c.Sample();
        now = 15020; c.BeginDrag(); var pickup = c.Sample();
        Assert.AreNotEqual(release.PlaybackId, pickup.PlaybackId);
        now = 15400; var hold = c.Sample(); Assert.AreEqual("drag-hold", hold.Action);
        Assert.AreNotEqual(smile.PlaybackId, hold.CompletedId); Assert.AreNotEqual(release.PlaybackId, hold.CompletedId);
        now = 99999; Assert.AreEqual("drag-hold", c.Sample().Action);
    }
    [TestMethod] public void MissingDragClipsNeverWaitForAnEndThatCannotHappen()
    {
        var c = Controller("drag-pickup", "drag-release"); c.SetAutomatic(true); c.BeginDrag();
        Assert.AreEqual("drag-hold", c.Sample().Action); c.EndDrag(); Assert.AreEqual("idle-soft", c.Sample().Action);
        var allMissing = Controller("drag-pickup", "drag-hold", "drag-release"); allMissing.SetAutomatic(true); allMissing.BeginDrag();
        Assert.AreEqual("neutral", allMissing.Sample().Action); now = 50000; Assert.AreEqual("neutral", allMissing.Sample().Action);
        allMissing.EndDrag(); Assert.AreEqual("idle-soft", allMissing.Sample().Action);
    }
    [TestMethod] public void MissingIdleAndSmileDoNotContinuouslyRestartFallback()
    {
        var c = Controller("idle-smile"); c.SetAutomatic(true); var idle = c.Sample();
        now = 999999; Assert.AreEqual(idle.PlaybackId, c.Sample().PlaybackId);
        var fallback = Controller("idle-soft"); fallback.SetAutomatic(true); var neutral = fallback.Sample();
        now += 999999; Assert.AreEqual("neutral", fallback.Sample().Action); Assert.AreEqual(neutral.PlaybackId, fallback.Sample().PlaybackId);
    }
    [TestMethod] public void ManualModeRetainsExplicitPlaybackAndSwitchCancelsOldOnce()
    {
        var c = Controller(); Assert.IsFalse(c.Automatic); Assert.IsTrue(c.PlayManual("idle-smile"));
        c.BeginDrag(); Assert.AreEqual("idle-smile", c.Sample().Action); c.EndDrag();
        now = 400; Assert.AreEqual("neutral", c.Sample().Action);
        c.SetAutomatic(true); Assert.AreEqual("idle-soft", c.Sample().Action); Assert.IsFalse(c.PlayManual("idle-smile"));
        now = 15400; Assert.AreEqual("idle-smile", c.Sample().Action); c.SetAutomatic(false);
        Assert.IsTrue(c.PlayManual("idle-soft")); now = 15800; Assert.AreEqual("idle-soft", c.Sample().Action);
        now = 100000; Assert.AreEqual("idle-soft", c.Sample().Action);
    }
    [TestMethod] public void LongGapDoesNotQueueSmilesAndClockCannotGoBackwards()
    {
        var c = Controller(); c.SetAutomatic(true); now = 100000; Assert.AreEqual("idle-smile", c.Sample().Action);
        now = 200000; Assert.AreEqual("idle-soft", c.Sample().Action);
        Assert.AreEqual("idle-soft", c.Sample().Action);
        now = 199999; Assert.ThrowsExactly<ArgumentOutOfRangeException>(() => c.BeginDrag());
    }
}
