namespace Aemeath.Presentation;

public sealed record BehaviorImage(string Path, string Sha256);
public sealed record BehaviorStep(string Value, int DurationMs);
public sealed record EyeBehavior(int WaitMinMs, int WaitMaxMs, IReadOnlyList<BehaviorStep> Track);
public sealed record BehaviorDefinition(
    string Profile, string NeutralKey,
    IReadOnlyDictionary<string, BehaviorImage> Images,
    IReadOnlyDictionary<(string Wing, string Eye, string Hem), string> Combinations,
    IReadOnlyList<BehaviorStep> Wing, IReadOnlyList<BehaviorStep> Hem,
    EyeBehavior Blink, EyeBehavior Wink,
    int PickupSourceMs, IReadOnlyList<BehaviorStep> PickupTail, IReadOnlyList<BehaviorStep> Hold,
    int ReleaseSourceMs, IReadOnlyDictionary<string, string> Routes,
    IReadOnlyDictionary<string, IReadOnlyList<BehaviorStep>> Tails)
{
    public IReadOnlyList<BehaviorStep> BindRelease(string sourceKey) =>
        Array.AsReadOnly(new[]{new BehaviorStep(sourceKey,ReleaseSourceMs)}.Concat(Tails[Routes[sourceKey]]).ToArray());
}
