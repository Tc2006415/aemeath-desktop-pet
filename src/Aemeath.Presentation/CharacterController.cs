namespace Aemeath.Presentation;

public sealed record SubmittedFrame(long PackageEpoch, string Path, long PlaybackId, int FrameIndex, long SubmissionSequence);

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
    private readonly long packageEpoch;
    private long submissionSequence;
    private PlaybackSample? issuedSample;
    public CharacterController(IReadOnlyDictionary<string, Clip> clips, Func<long> clock, long packageEpoch = 0)
    {
        this.clock = clock; this.packageEpoch = packageEpoch; player = new Playback(clips);
        Select("neutral", Phase.Manual, Now());
    }
    public bool Automatic { get; private set; }
    public SubmittedFrame? LastSubmitted { get; private set; }
    public string? ReleaseFallback { get; private set; }
    public void CommitRendered(PlaybackSample sample)
    {
        // Acknowledgment must refer to the actual object most recently sampled by this controller.
        // Cloned/old-package/invalidated requests cannot fabricate a displayed pose.
        if (!ReferenceEquals(sample, issuedSample)) return;
        LastSubmitted = new(packageEpoch, sample.FramePath, sample.PlaybackId, sample.FrameIndex, checked(++submissionSequence));
        issuedSample = null;
    }
    private long Now()
    {
        long now = clock();
        if (now < lastTime) throw new ArgumentOutOfRangeException(nameof(clock), "Clock must be nonnegative and monotonic.");
        lastTime = now; return now;
    }
    public void SetAutomatic(bool enabled)
    {
        long now = Now(); if (Automatic == enabled) return;
        LastSubmitted = null;
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
        ReleaseFallback = null;
        if (player.Available("drag-release"))
        {
            var source = LastSubmitted;
            string? path = source?.PackageEpoch == packageEpoch ? source.Path : null;
            if (path is null) ReleaseFallback = "no-submitted-frame";
            else if (!player.HasReleaseEntry(path)) { ReleaseFallback = "no-entry-for-source"; path = null; }
            Select("drag-release", Phase.Release, now, path);
        }
        else { ReleaseFallback = "release-unavailable"; Idle(now); }
    }
    public PlaybackSample Sample()
    {
        long now = Now(); var result = player.Sample(now);
        if (!Automatic) return Issue(result);
        // Only this player owns completion production. Replaced instances cannot enqueue callbacks.
        if (result.CompletedId is long completed && completed == expectedInstance)
        {
            if (phase == Phase.Pickup) Hold(now);
            else if (phase is Phase.Smile or Phase.Release) Idle(now);
            return Issue(player.Sample(now) with { CompletedId = completed });
        }
        if (phase == Phase.Idle && idleStarted is long since && now - since >= 15000)
        {
            Select("idle-smile", Phase.Smile, now);
            return Issue(player.Sample(now));
        }
        return Issue(result);
    }
    private PlaybackSample Issue(PlaybackSample sample) { issuedSample = sample; return sample; }
    private void Select(string action, Phase next, long now, string? releaseSource = null)
    {
        issuedSample = null;
        idleStarted = null; phase = next; expectedInstance = player.Play(action, now, releaseSource);
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
