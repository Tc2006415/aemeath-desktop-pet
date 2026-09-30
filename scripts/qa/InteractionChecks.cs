using Aemeath.Presentation;

// Independent API-level probes; does not send native mouse or keyboard input.
internal static class InteractionChecks
{
    public static int Run()
    {
        int passed = 0;
        void Check(string name, Action test)
        {
            test(); passed++; Console.WriteLine("PASS " + name);
        }
        void Equal<T>(T expected, T actual)
        {
            if (!Equals(expected, actual)) throw new Exception($"Expected {expected}; actual {actual}");
        }
        string[] optional = ["idle-soft", "idle-smile", "drag-pickup", "drag-hold", "drag-release"];
        Dictionary<string, Clip> Clips(int mask = 0)
        {
            var result = new Dictionary<string, Clip> { ["neutral"] = new("neutral", true, [new("n", 101)]) };
            for (int i = 0; i < optional.Length; i++)
                if ((mask & (1 << i)) == 0)
                    result.Add(optional[i], new(optional[i], i is 0 or 3, [new("a", 17), new("b", 26)]));
            return result;
        }
        Check("all 32 optional-clip subsets release and regrab without trapping", () => {
            for (int mask = 0; mask < 32; mask++)
            {
                long t = 0; var clips = Clips(mask); var c = new CharacterController(clips, () => t);
                string idle = clips.ContainsKey("idle-soft") ? "idle-soft" : "neutral";
                string hold = clips.ContainsKey("drag-hold") ? "drag-hold" : "neutral";
                c.SetAutomatic(true); Equal(idle, c.Sample().Action); c.BeginDrag();
                t = 43; Equal(hold, c.Sample().Action);
                c.EndDrag(); t = 86; Equal(idle, c.Sample().Action);
                c.BeginDrag(); t = 87; c.EndDrag(); t = 88; c.BeginDrag();
                t = 131; Equal(hold, c.Sample().Action); t = 10000; Equal(hold, c.Sample().Action);
                c.EndDrag(); t = 10043; Equal(idle, c.Sample().Action);
            }
        });
        Check("switch modes while captured preserves new capture and cancels old deadlines", () => {
            long t = 0; var c = new CharacterController(Clips(), () => t);
            c.BeginDrag(); c.PlayManual("idle-smile"); t = 10; c.SetAutomatic(true);
            Equal("drag-pickup", c.Sample().Action); t = 52; Equal("drag-pickup", c.Sample().Action);
            t = 53; Equal("drag-hold", c.Sample().Action); c.SetAutomatic(false);
            c.PlayManual("idle-smile"); t = 54; c.EndDrag(); t = 96; Equal("neutral", c.Sample().Action);
            c.SetAutomatic(true); Equal("idle-soft", c.Sample().Action);
        });
        Check("release interrupted by manual then automatic does not retain drag", () => {
            long t = 0; var c = new CharacterController(Clips(), () => t); c.SetAutomatic(true); c.BeginDrag();
            t = 1; c.EndDrag(); t = 2; c.SetAutomatic(false); c.PlayManual("idle-smile");
            t = 3; c.SetAutomatic(true); var idle = c.Sample();
            t = 45; Equal(idle.PlaybackId, c.Sample().PlaybackId); Equal("idle-soft", c.Sample().Action);
        });
        Check("completion emitted once and superseded once never completes", () => {
            long t = 0; var c = new CharacterController(Clips(), () => t); c.SetAutomatic(true);
            t = 15000; var smile = c.Sample(); c.BeginDrag(); var pickup = c.Sample();
            t = 15001; c.EndDrag(); var release = c.Sample(); t = 15002; c.BeginDrag(); var regrab = c.Sample();
            t = 15045; var hold = c.Sample(); Equal<long?>(regrab.PlaybackId, hold.CompletedId);
            if (hold.CompletedId == smile.PlaybackId || hold.CompletedId == pickup.PlaybackId || hold.CompletedId == release.PlaybackId)
                throw new Exception("Superseded instance completed");
            Equal<long?>(null, c.Sample().CompletedId);
            c.EndDrag(); t = 15088; Equal("idle-soft", c.Sample().Action); Equal<long?>(null, c.Sample().CompletedId);
        });
        Check("duplicate mode/start/end calls do not extend animation or idle deadlines", () => {
            long t = 0; var c = new CharacterController(Clips(), () => t); c.SetAutomatic(true);
            t = 14999; c.SetAutomatic(true); Equal("idle-soft", c.Sample().Action);
            t = 15000; Equal("idle-smile", c.Sample().Action); c.BeginDrag();
            t = 15042; c.BeginDrag(); Equal("drag-pickup", c.Sample().Action);
            t = 15043; Equal("drag-hold", c.Sample().Action); c.EndDrag();
            t = 15085; c.EndDrag(); Equal("drag-release", c.Sample().Action);
            t = 15086; Equal("idle-soft", c.Sample().Action);
        });
        Console.WriteLine($"{passed} independent interaction probes passed"); return 0;
    }
}
