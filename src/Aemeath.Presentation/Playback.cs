namespace Aemeath.Presentation;

public sealed record Frame(string Path, int DurationMs);
public sealed record Clip(string Id, bool Loop, IReadOnlyList<Frame> Frames)
{
    public int DurationMs => Frames.Sum(f => f.DurationMs);
    public IReadOnlyDictionary<string, IReadOnlyList<Frame>> EntrySequences { get; init; } = new Dictionary<string, IReadOnlyList<Frame>>().AsReadOnly();
}
public sealed record PlaybackSample(string Action, int FrameIndex, long PlaybackId, long? CompletedId, string FramePath = "");
public sealed class Playback(IReadOnlyDictionary<string, Clip> clips)
{
    private string current = "neutral";
    private long started, lastTime, sequence, instance;
    private IReadOnlyList<Frame> activeFrames = clips["neutral"].Frames;
    private void CheckTime(long now)
    {
        if (now < lastTime) throw new ArgumentOutOfRangeException(nameof(now));
        lastTime = now;
    }
    public long Play(string action, long now, string? releaseSource = null)
    {
        CheckTime(now);
        current = Available(action) ? action : "neutral";
        activeFrames = current == "drag-release" && releaseSource is not null && clips[current].EntrySequences.TryGetValue(releaseSource, out var entry)
            ? entry : clips[current].Frames;
        started = now;
        instance = checked(++sequence);
        return Available(action) ? instance : 0;
    }
    public void Cancel(long id, long now)
    {
        CheckTime(now);
        if (id == instance) Play("neutral", now);
    }
    public PlaybackSample Sample(long now)
    {
        CheckTime(now);
        var clip = clips[current];
        long elapsed = now - started;
        int duration = activeFrames.Sum(f => f.DurationMs);
        if (!clip.Loop && elapsed >= duration)
        {
            var completed = instance;
            Play("neutral", now);
            return new(current, 0, instance, completed, activeFrames[0].Path);
        }
        elapsed %= duration;
        var index = 0;
        while (elapsed >= activeFrames[index].DurationMs)
            elapsed -= activeFrames[index++].DurationMs;
        return new(current, index, instance, null, activeFrames[index].Path);
    }
    public bool Available(string action) => clips.ContainsKey(action);
    public bool HasReleaseEntry(string path) => clips.TryGetValue("drag-release", out var release) && release.EntrySequences.ContainsKey(path);
}
