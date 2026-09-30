using Microsoft.VisualStudio.TestTools.UnitTesting;
using Aemeath.Presentation;

namespace Aemeath.Tests;

[TestClass]
public class PlaybackGeometryTests
{
    private static Playback Player() => new(new Dictionary<string, Clip>
    {
        ["neutral"] = new("neutral", true, [new("n", 1000)]),
        ["idle-soft"] = new("idle-soft", true, [new("a", 100), new("b", 200)]),
        ["idle-smile"] = new("idle-smile", false, [new("a", 100), new("b", 200)])
    });
    [TestMethod] public void HalfOpenBoundariesAndLoopSkip()
    {
        var p = Player(); p.Play("idle-soft", 0);
        Assert.AreEqual(0, p.Sample(99).FrameIndex);
        Assert.AreEqual(1, p.Sample(100).FrameIndex);
        Assert.AreEqual(0, p.Sample(300).FrameIndex);
        Assert.AreEqual(1, p.Sample(10000).FrameIndex);
    }
    [TestMethod] public void OnceReturnsNeutralAndCompletesExactlyOnce()
    {
        var p = Player(); var id = p.Play("idle-smile", 10);
        Assert.AreEqual("idle-smile", p.Sample(309).Action);
        var end = p.Sample(310);
        Assert.AreEqual("neutral", end.Action); Assert.AreEqual(id, end.CompletedId);
        Assert.IsNull(p.Sample(310).CompletedId); Assert.IsNull(p.Sample(10000).CompletedId);
    }
    [TestMethod] public void ReplacementAndStaleCancelCannotEndNewInstance()
    {
        var p = Player(); var old = p.Play("idle-smile", 0);
        var next = p.Play("idle-soft", 50); p.Cancel(old, 60);
        var result = p.Sample(600); Assert.AreEqual(next, result.PlaybackId);
        Assert.AreEqual("idle-soft", result.Action); Assert.IsNull(result.CompletedId);
        p.Cancel(next, 601); Assert.AreEqual("neutral", p.Sample(602).Action);
        Assert.IsNull(p.Sample(1000).CompletedId);
    }
    [TestMethod] public void MissingActionCancelsOnceWithoutFakeCompletion()
    {
        var p = Player(); p.Play("idle-smile", 0);
        Assert.AreEqual(0L, p.Play("drag-release", 10));
        Assert.AreEqual("neutral", p.Sample(300).Action); Assert.IsNull(p.Sample(300).CompletedId);
    }
    [TestMethod] public void ClockMustBeNonnegativeAndMonotonic()
    {
        var p = Player(); Assert.ThrowsExactly<ArgumentOutOfRangeException>(() => p.Sample(-1));
        p.Sample(10); Assert.ThrowsExactly<ArgumentOutOfRangeException>(() => p.Play("idle-soft", 9));
    }
    [TestMethod] public void FractionalDpiPreservesPhysicalPixels()
    {
        var size = Geometry.Size(2, 144);
        Assert.AreEqual(192, size.WidthPx); Assert.AreEqual(208, size.HeightPx);
        Assert.AreEqual(128d, size.WidthDip); Assert.AreEqual(138.6666667, size.HeightDip, 0.00001);
        Assert.ThrowsExactly<ArgumentOutOfRangeException>(() => Geometry.Size(2, 0));
    }
    [TestMethod] public void DragKeepsOffsetAndEndsIdempotently()
    {
        var drag = new DragSession(); drag.Start(new(-90, 80), new(-100, 60));
        Assert.AreEqual(new ScreenPx(400, 300), drag.Move(new(410, 320)));
        Assert.IsTrue(drag.End()); Assert.IsFalse(drag.End()); Assert.IsFalse(drag.Active);
        Assert.ThrowsExactly<InvalidOperationException>(() => drag.Move(new(0, 0)));
    }
    [TestMethod] public void ClampSupportsNegativeWorkareaAndRejectsOversizedPet()
    {
        Assert.AreEqual(new ScreenPx(-1920, 872), Geometry.Clamp(new(-2000, 1000), 192, 208, new(-1920, 0, 0, 1080)));
        Assert.ThrowsExactly<ArgumentOutOfRangeException>(() => Geometry.Clamp(new(0, 0), 192, 208, new(0, 0, 100, 100)));
    }
}
