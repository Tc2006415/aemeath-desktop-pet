namespace Aemeath.Presentation;

/// <summary>Local animation choices only; never infers or consumes task status.</summary>
public sealed class CharacterController
{
    private enum Phase { Manual, Idle, Smile, Pickup, Hold, Release }
    private readonly Playback player;
    private readonly Func<long> clock;
    private long lastTime, expectedInstance;
    private long? idleStarted;
    private bool dragging;
    private Phase phase;
    public CharacterController(IReadOnlyDictionary<string, Clip> clips, Func<long> clock)
    {
        this.clock = clock; player = new Playback(clips);
        Select("neutral", Phase.Manual, Now());
    }
    public bool Automatic { get; private set; }
    private long Now()
    {
        long now = clock();
        if (now < lastTime) throw new ArgumentOutOfRangeException(nameof(clock), "Clock must be nonnegative and monotonic.");
        lastTime = now; return now;
    }
    public void SetAutomatic(bool enabled)
    {
        long now = Now(); if (Automatic == enabled) return;
        Automatic = enabled;
        if (!enabled) Select("neutral", Phase.Manual, now);
        else if (dragging) Pickup(now);
        else Idle(now);
    }
    public bool PlayManual(string action)
    {
        long now = Now(); if (Automatic) return false;
        Select(action, Phase.Manual, now); return expectedInstance != 0;
    }
    public void BeginDrag()
    {
        long now = Now(); if (dragging) return;
        dragging = true; if (Automatic) Pickup(now);
    }
    public void EndDrag()
    {
        long now = Now(); if (!dragging) return;
        dragging = false;
        if (!Automatic) return;
        if (player.Available("drag-release")) Select("drag-release", Phase.Release, now);
        else Idle(now);
    }
    public PlaybackSample Sample()
    {
        long now = Now(); var result = player.Sample(now);
        if (!Automatic) return result;
        // Only this player owns completion production. Replaced instances cannot enqueue callbacks.
        if (result.CompletedId is long completed && completed == expectedInstance)
        {
            if (phase == Phase.Pickup) Hold(now);
            else if (phase is Phase.Smile or Phase.Release) Idle(now);
            return player.Sample(now) with { CompletedId = completed };
        }
        if (phase == Phase.Idle && idleStarted is long since && now - since >= 15000)
        {
            Select("idle-smile", Phase.Smile, now);
            return player.Sample(now);
        }
        return result;
    }
    private void Select(string action, Phase next, long now)
    {
        idleStarted = null; phase = next; expectedInstance = player.Play(action, now);
    }
    private void Idle(long now)
    {
        bool available = player.Available("idle-soft");
        Select(available ? "idle-soft" : "neutral", Phase.Idle, now);
        if (available && player.Available("idle-smile")) idleStarted = now;
    }
    private void Pickup(long now)
    {
        if (player.Available("drag-pickup")) Select("drag-pickup", Phase.Pickup, now);
        else Hold(now);
    }
    private void Hold(long now) => Select(player.Available("drag-hold") ? "drag-hold" : "neutral", Phase.Hold, now);
}
