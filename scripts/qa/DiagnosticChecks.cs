using System.IO;
using System.Text;
using System.Text.Json.Nodes;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using Aemeath.Host;
using Aemeath.Presentation;
using Geometry = Aemeath.Presentation.Geometry;

// Independent contract probes. No UI automation, business events or character artwork.
internal static class DiagnosticChecks
{
    private static int failures;
    [STAThread]
    private static int Main(string[] args)
    {
        if (args.Length == 1 && args[0] == "interaction") return InteractionChecks.Run();
        if (args.Length == 2 && args[0] == "neutral-package") return NeutralPackageChecks.Run(args[1]);
        if (args.Length == 2 && args[0] == "art009-package") return Art009PackageChecks.Run(args[1]);
        if (args.Length == 2 && args[0] == "reject-package")
        {
            Run("reparse package must reject before decoder", () => {
                int calls = 0;
                Reject(() => PackageLoader.Load(args[1], b => { calls++; return PngDecoder.Decode(b); }));
                Equal(0, calls);
            });
            return failures == 0 ? 0 : 1;
        }
        string root = Path.Combine(Path.GetTempPath(), "aemeath-qa-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(Path.Combine(root, "frames"));
        byte[] pixels = new byte[96 * 104 * 4];
        pixels[0] = 255; pixels[3] = 255; // One synthetic diagnostic pixel, not character artwork.
        var bitmap = BitmapSource.Create(96, 104, 96, 96, PixelFormats.Bgra32, null, pixels, 384);
        var encoder = new PngBitmapEncoder(); encoder.Frames.Add(BitmapFrame.Create(bitmap));
        using (var stream = File.Create(Path.Combine(root, "frames/neutral.png"))) encoder.Save(stream);
        File.Copy(Path.Combine(root, "frames/neutral.png"), Path.Combine(root, "frames/shared.png"));
        var source = """
        {"schemaVersion":1,"packageId":"qa-probe","packageVersion":"0.0.1","packageKind":"diagnostic","sourceScale":1,
        "frameSize":{"width":96,"height":104},"anchor":{"x":48,"y":94},"fallbackAction":"neutral","actions":{
        "neutral":{"playback":"loop","origin":"diagnostic","frames":[{"path":"frames/neutral.png","durationMs":1000}]},
        "idle-soft":{"playback":"loop","origin":"diagnostic","frames":[{"path":"frames/shared.png","durationMs":400},{"path":"frames/neutral.png","durationMs":200}]},
        "idle-smile":{"playback":"once","origin":"diagnostic","frames":[{"path":"frames/shared.png","durationMs":300},{"path":"frames/neutral.png","durationMs":200}]}}}
        """;
        void Write(string json) => File.WriteAllText(Path.Combine(root, "manifest.json"), json, new UTF8Encoding(false));
        AssetPackage Load() => PackageLoader.Load(root, PngDecoder.Decode);
        Write(source);
        Run("valid RGBA diagnostic package caches repeated file", () => { var p = Load(); Equal(2, p.Images.Count); Equal(3, p.Clips.Count); });
        Run("manifest 64 KiB inclusive, one byte over rejected", () => {
            Write(source.PadRight(65536)); Equal(3, Load().Clips.Count);
            Write(source.PadRight(65537)); Reject(() => Load()); Write(source);
        });
        Run("duration 60000 inclusive, larger sum rejected", () => {
            var m = JsonNode.Parse(source)!;
            var frames = new JsonArray();
            for (int i = 0; i < 6; i++) frames.Add(new JsonObject { ["path"]="frames/shared.png", ["durationMs"]=10000 });
            m["actions"]!["idle-soft"]!["frames"] = frames;
            Write(m.ToJsonString()); Equal(60000, Load().Clips["idle-soft"].DurationMs);
            frames.Add(new JsonObject { ["path"]="frames/shared.png", ["durationMs"]=1 });
            Write(m.ToJsonString()); Reject(() => Load()); Write(source);
        });
        Run("64 timing items inclusive, 65 rejected", () => {
            var m = JsonNode.Parse(source)!; var frames = new JsonArray();
            for (int i = 0; i < 64; i++) frames.Add(new JsonObject { ["path"]="frames/shared.png", ["durationMs"]=1 });
            m["actions"]!["idle-soft"]!["frames"] = frames;
            Write(m.ToJsonString()); Equal(64, Load().Clips["idle-soft"].Frames.Count);
            frames.Add(new JsonObject { ["path"]="frames/shared.png", ["durationMs"]=1 });
            Write(m.ToJsonString()); Reject(() => Load()); Write(source);
        });
        Run("path errors fail entire package before image decoding", () => {
            foreach (var path in new[] { "frames/lpt9.png", "frames/a.png:stream", "frames/%2e%2e.png", "frames/a.png\n" }) {
                var m = JsonNode.Parse(source)!; m["actions"]!["idle-soft"]!["frames"]![0]!["path"] = path;
                Write(m.ToJsonString()); int calls = 0;
                Reject(() => PackageLoader.Load(root, b => { calls++; return PngDecoder.Decode(b); })); Equal(0, calls);
            }
            Write(source);
        });
        Run("shared corrupted image disables both full clips", () => {
            File.WriteAllBytes(Path.Combine(root, "frames/shared.png"), [1,2,3]);
            var p = Load(); Equal(1, p.Clips.Count); Equal(2, p.DisabledActions.Count);
            if (!p.Clips.ContainsKey("neutral")) throw new Exception("neutral lost");
            File.Copy(Path.Combine(root, "frames/neutral.png"), Path.Combine(root, "frames/shared.png"), true);
        });
        Run("bad neutral reload retains exact prior package", () => {
            var session = new PackageSession(); if (!session.TryLoad(root, PngDecoder.Decode)) throw new Exception("initial load failed");
            var prior = session.Current; var path = Path.Combine(root, "frames/neutral.png"); var original = File.ReadAllBytes(path);
            File.WriteAllBytes(path, [1,2,3]);
            if (session.TryLoad(root, PngDecoder.Decode) || !ReferenceEquals(prior, session.Current)) throw new Exception("prior package replaced");
            var empty = new PackageSession(); if (empty.TryLoad(root, PngDecoder.Decode) || empty.Current != null || empty.Error == null) throw new Exception("first failure hidden");
            File.WriteAllBytes(path, original);
        });
        Run("once boundary/cancel/replacement never revives stale instance", () => {
            var p = new Playback(Load().Clips); long old = p.Play("idle-smile", 0);
            Equal(0, p.Sample(299).FrameIndex); Equal(1, p.Sample(300).FrameIndex);
            Equal("idle-smile", p.Sample(499).Action);
            var done = p.Sample(500); Equal("neutral", done.Action); Equal<long?>(old, done.CompletedId);
            Equal<long?>(null, p.Sample(500).CompletedId);
            long current = p.Play("idle-soft", 500); p.Cancel(old, 500);
            Equal(current, p.Sample(900).PlaybackId); Equal(1, p.Sample(900).FrameIndex);
            p.Cancel(current, 901); Equal<long?>(null, p.Sample(10000).CompletedId);
            Equal("neutral", p.Sample(10000).Action);
        });
        Run("large sampling gap completes once; unavailable action is not completion", () => {
            var p = new Playback(Load().Clips); long id = p.Play("idle-smile", 0);
            Equal<long?>(id, p.Sample(500000).CompletedId); Equal<long?>(null, p.Sample(500001).CompletedId);
            p.Play("idle-smile", 500002); Equal(0L, p.Play("drag-release", 500003));
            Equal("neutral", p.Sample(600000).Action); Equal<long?>(null, p.Sample(600000).CompletedId);
        });
        Run("120 DPI keeps exact physical size and negative offset", () => {
            var l = Geometry.Size(2,120); Equal(192,l.WidthPx); Equal(208,l.HeightPx);
            Near(153.6,l.WidthDip); Near(166.4,l.HeightDip);
            var d = new DragSession(); d.Start(new(-1897,-966),new(-1920,-1000));
            Equal(new ScreenPx(-523,-434),d.Move(new(-500,-400)));
            Equal(new ScreenPx(-1920,-104),Geometry.Clamp(new(-2000,100),192,104,new(-1920,-1080,0,0)));
            if (!d.End() || d.End()) throw new Exception("drag termination not idempotent");
        });
        Write(source);
        Console.WriteLine("FIXTURE_ROOT="+root); // Retained for bounded reparse probes; only generated fixture data.
        Console.WriteLine($"QA failures: {failures}");
        return failures == 0 ? 0 : 1;
    }
    private static void Run(string name, Action body) { try { body(); Console.WriteLine("PASS "+name); } catch(Exception ex) { failures++; Console.WriteLine("FAIL "+name+": "+ex.GetType().Name+" "+ex.Message); } }
    private static void Reject(Action body) { try { body(); } catch(PackageException) { return; } throw new Exception("Expected PackageException"); }
    private static void Equal<T>(T expected, T actual) { if (!EqualityComparer<T>.Default.Equals(expected,actual)) throw new Exception($"Expected {expected}; actual {actual}"); }
    private static void Near(double expected, double actual) { if (Math.Abs(expected-actual)>0.0000001) throw new Exception($"Expected {expected}; actual {actual}"); }
}
