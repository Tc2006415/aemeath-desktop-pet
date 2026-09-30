namespace Aemeath.Presentation;

/// <summary>Finite schema3 scheduler. No rendering, input, or wall-clock timers.</summary>
internal sealed class LayeredBehaviorController(BehaviorDefinition definition, Func<int,int,int> random, Func<long> nextInstance)
{
    private string phase="idle", eye="open", source=definition.NeutralKey;
    private long started, idleEpoch, eyeStarted, instance, nextBlink, nextWink;
    private IReadOnlyList<BehaviorStep> active=[];
    public string? Route { get; private set; }
    public void Idle(long now)
    {
        phase="idle"; eye="open"; idleEpoch=now; instance=nextInstance(); Route=null;
        ScheduleBoth(now);
    }
    private long Deadline(long now,EyeBehavior behavior)
    {
        int delay=random(behavior.WaitMinMs,behavior.WaitMaxMs);
        if(delay<behavior.WaitMinMs || delay>behavior.WaitMaxMs) throw new ArgumentOutOfRangeException(nameof(random));
        return checked(now+delay);
    }
    private void ScheduleBoth(long now) { nextBlink=Deadline(now,definition.Blink); nextWink=Deadline(now,definition.Wink); }
    public void Pickup(long now,string captured)
    {
        phase="panic"; started=now; source=captured; eye="open"; instance=nextInstance(); Route=null;
        active=Array.AsReadOnly(new[]{new BehaviorStep(source,definition.PickupSourceMs)}.Concat(definition.PickupTail).ToArray());
    }
    public void Release(long now,string captured)
    {
        phase="release"; started=now; source=captured; eye="open"; instance=nextInstance(); Route=definition.Routes[source];
        active=definition.BindRelease(source);
    }
    public PlaybackSample Sample(long now)
    {
        long? completed=null;
        if(phase=="panic" && now-started>=700)
        { completed=instance; instance=nextInstance(); phase="held"; started=checked(started+700); active=definition.Hold; }
        else if(phase=="release" && now-started>=540)
        { completed=instance; Idle(checked(started+540)); }
        string key; int index;
        if(phase=="idle")
        {
            if(eye!="open")
            {
                int duration=eye=="blink"?240:1200;
                if(now-eyeStarted>=duration)
                {
                    long end=checked(eyeStarted+duration); completed=instance; instance=nextInstance();
                    if(eye=="wink") ScheduleBoth(end); else nextBlink=Deadline(end,definition.Blink);
                    eye="open";
                }
            }
            if(eye=="open")
            {
                if(now>=nextWink) StartEye("wink",now);
                else if(now>=nextBlink) StartEye("blink",now);
            }
            long local=(now-idleEpoch)%1400;
            int w=Index(definition.Wing,local), h=Index(definition.Hem,local), e=0;
            string pose="open";
            if(eye!="open")
            {
                var track=eye=="blink"?definition.Blink.Track:definition.Wink.Track;
                e=Index(track,now-eyeStarted); pose=track[e].Value;
            }
            key=definition.Combinations[(definition.Wing[w].Value,pose,definition.Hem[h].Value)];
            index=w*25+h*5+e; // diagnostic identity, not a base clip index
        }
        else { index=Index(active,phase=="held"?(now-started)%1400:now-started); key=active[index].Value; }
        string action=phase switch { "panic"=>"drag-pickup","held"=>"drag-hold","release"=>"drag-release",_=>eye=="wink"?"idle-smile":"idle-soft" };
        return new(action,index,instance,completed,definition.Images[key].Path) { FrameKey=key,BehaviorPhase=phase=="idle"?eye=="open"?"idle":eye:phase };
    }
    private void StartEye(string next,long now) { eye=next; eyeStarted=now; instance=nextInstance(); }
    private static int Index(IReadOnlyList<BehaviorStep> steps,long elapsed)
    {
        int index=0; while(index<steps.Count-1 && elapsed>=steps[index].DurationMs) elapsed-=steps[index++].DurationMs;
        return index;
    }
}
