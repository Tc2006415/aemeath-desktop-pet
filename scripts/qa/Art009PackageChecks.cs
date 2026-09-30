using Aemeath.Host;
using Aemeath.Presentation;

internal static class Art009PackageChecks
{
    public static int Run(string root)
    {
        var package = PackageLoader.Load(root, PngDecoder.Decode);
        if (package.Version != "0.3.0" || package.Clips.Count != 3 || package.Images.Count != 5 || package.DisabledActions.Count != 0)
            throw new Exception("Candidate did not load completely");
        foreach (var (action, times, loop) in new[] {
            ("idle-soft", new[] {400,150,150,400,150,150}, true),
            ("idle-smile", new[] {120,120,500,120,120,220}, false) })
        {
            var clip = package.Clips[action];
            if (clip.Loop != loop || !clip.Frames.Select(f=>f.DurationMs).SequenceEqual(times)) throw new Exception("Wrong timing");
            var player = new Playback(package.Clips); var id = player.Play(action, 0); long t = 0;
            for (int i = 0; i < 6; i++) {
                var first = player.Sample(t); var last = player.Sample(t+times[i]-1);
                if (first.Action != action || first.FrameIndex != i || last.FrameIndex != i) throw new Exception("Wrong item boundary");
                t += times[i];
            }
            var end = player.Sample(t);
            if (loop ? end.Action != action || end.FrameIndex != 0 || end.CompletedId != null : end.Action != "neutral" || end.CompletedId != id)
                throw new Exception("Wrong loop/once end");
            Console.WriteLine($"PASS real loaded {action}: six item boundaries, duration {t}ms, loop={loop}");
        }
        long now = 0; var controller = new CharacterController(package.Clips, ()=>now); controller.SetAutomatic(true);
        now = 14999; if (controller.Sample().Action != "idle-soft") throw new Exception("Early smile");
        now = 15000; if (controller.Sample().Action != "idle-smile") throw new Exception("Missing smile");
        now = 16200; if (controller.Sample().Action != "idle-soft") throw new Exception("Missing return to idle");
        Console.WriteLine("PASS candidate decoder/loader: 3 actions, 5 PNGs, no disabled actions; automatic 15000/16200ms boundaries");
        return 0;
    }
}
