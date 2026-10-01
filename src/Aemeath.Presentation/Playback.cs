namespace Aemeath.Presentation;

public sealed record Frame(string Path, int DurationMs);
public sealed record Clip(string Id, bool Loop, IReadOnlyList<Frame> Frames)
{
    public int DurationMs => Frames.Sum(f => f.DurationMs);
}
public sealed record PlaybackSample(string Action, int FrameIndex, long PlaybackId, long? CompletedId);
public sealed class Playback(IReadOnlyDictionary<string, Clip> clips)
{
    private string current = "neutral";
    private long started, lastTime, sequence, instance;
    private void CheckTime(long now)
    {
        if (now < lastTime) throw new ArgumentOutOfRangeException(nameof(now));
        lastTime = now;
    }
    public long Play(string action, long now)
    {
        CheckTime(now);
        current = Available(action) ? action : "neutral";
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
        if (!clip.Loop && elapsed >= clip.DurationMs)
        {
            var completed = instance;
            Play("neutral", now);
            return new(current, 0, instance, completed);
        }
        elapsed %= clip.DurationMs;
        var index = 0;
        while (elapsed >= clip.Frames[index].DurationMs)
            elapsed -= clip.Frames[index++].DurationMs;
        return new(current, index, instance, null);
    }
    public bool Available(string action) => clips.ContainsKey(action);
}
