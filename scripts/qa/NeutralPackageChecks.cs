using Aemeath.Host;
using Aemeath.Presentation;

internal static class NeutralPackageChecks
{
    public static int Run(string root)
    {
        var package = PackageLoader.Load(root, PngDecoder.Decode);
        if (package.Id != "aemeath-v1" || package.Kind != "character" || package.Clips.Count != 1 ||
            package.Images.Count != 1 || package.DisabledActions.Count != 0 || !package.Clips.ContainsKey("neutral"))
            throw new Exception("Unexpected neutral-only package");
        var clip = package.Clips["neutral"];
        if (!clip.Loop || clip.Frames.Count != 1 || clip.DurationMs != 1000) throw new Exception("Unexpected neutral timing");
        Console.WriteLine("PASS actual production loader/PNG decoder: one neutral clip, one image, no disabled declared actions");
        long now = 0; var controller = new CharacterController(package.Clips, () => now);
        controller.SetAutomatic(true);
        var initial = controller.Sample();
        foreach (long t in new long[] { 999, 1000, 14999, 15000, 15001, 1000000 })
        {
            now = t; var sample = controller.Sample();
            if (sample.Action != "neutral" || sample.FrameIndex != 0 || sample.CompletedId != null || sample.PlaybackId != initial.PlaybackId)
                throw new Exception($"Fallback restarted or left neutral at {t}");
        }
        controller.BeginDrag(); Check(); controller.EndDrag(); Check();
        controller.BeginDrag(); Check(); now++; controller.EndDrag(); Check();
        now += 20000; Check();
        void Check() { var s = controller.Sample(); if (s.Action != "neutral" || s.FrameIndex != 0 || s.CompletedId != null) throw new Exception("Missing action trapped fallback"); }
        Console.WriteLine("PASS actual package automatic fallback across 15s and repeated drag API transitions; no native input");
        return 0;
    }
}
