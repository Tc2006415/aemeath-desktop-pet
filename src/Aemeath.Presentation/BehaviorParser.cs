using System.Text.Json;
using static Aemeath.Presentation.PackageLoader;

namespace Aemeath.Presentation;

internal static class BehaviorParser
{
    internal static BehaviorDefinition Parse(JsonElement b, IReadOnlyDictionary<string, Clip> clips, ref int totalItems)
    {
        Fields(b,"profile","neutralKey","images","idle","interaction");
        string profile=Text(b.GetProperty("profile")); Require(profile=="layered-idle-drag-v1");
        string neutral=Text(b.GetProperty("neutralKey")); Require(neutral=="idle:A-open-base");
        var images=new Dictionary<string,BehaviorImage>(StringComparer.Ordinal);
        var paths=new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        foreach(var p in Object(b.GetProperty("images"),128))
        {
            Match(p.Name,"[A-Za-z0-9:_-]{1,64}"); Fields(p.Value,"path","sha256");
            string path=ValidPath(Text(p.Value.GetProperty("path"))), sha=Text(p.Value.GetProperty("sha256")); Match(sha,"[a-f0-9]{64}");
            Require(paths.Add(path) && images.TryAdd(p.Name,new(path,sha)));
        }
        Require(images.ContainsKey(neutral) && clips.Count==6 && clips["neutral"].Frames[0].Path==images[neutral].Path);
        foreach(var clip in clips.Values) foreach(var frame in clip.Frames) Require(images.Values.Any(i=>i.Path==frame.Path));
        int count=0;
        IReadOnlyList<BehaviorStep> Steps(JsonElement array,string field)
        {
            Require(array.ValueKind==JsonValueKind.Array && array.GetArrayLength() is >=1 and <=64);
            var steps=new List<BehaviorStep>(); int duration=0;
            foreach(var item in array.EnumerateArray())
            {
                Fields(item,field,"durationMs"); string value=Text(item.GetProperty(field));
                if(field=="key") Require(images.ContainsKey(value));
                int ms=Number(item.GetProperty("durationMs"),1,10000); duration=checked(duration+ms); Require(duration<=60000);
                steps.Add(new(value,ms));
            }
            count=checked(count+steps.Count); Require(count<=256); return steps.AsReadOnly();
        }
        var idle=b.GetProperty("idle"); Fields(idle,"combinations","wing","hem","blink","wink");
        var combos=new Dictionary<(string,string,string),string>();
        var comboArray=idle.GetProperty("combinations"); Require(comboArray.ValueKind==JsonValueKind.Array && comboArray.GetArrayLength()==45);
        var expectedImages=new HashSet<string>(StringComparer.Ordinal);
        foreach(var row in comboArray.EnumerateArray())
        {
            Fields(row,"wing","eyeHead","hem","key"); var w=Text(row.GetProperty("wing")); var e=Text(row.GetProperty("eyeHead")); var h=Text(row.GetProperty("hem")); var key=Text(row.GetProperty("key"));
            Require(new[]{"A","B","C"}.Contains(w) && new[]{"open","half","closed","mid","wink"}.Contains(e) && new[]{"base","light","upper"}.Contains(h));
            Require(key==$"idle:{w}-{e}-{h}" && images.ContainsKey(key) && combos.TryAdd((w,e,h),key)); expectedImages.Add(key);
        }
        var wing=Steps(idle.GetProperty("wing"),"value"); Exact(wing,("A",400),("B",150),("C",150),("C",400),("B",150),("A",150));
        var hem=Steps(idle.GetProperty("hem"),"value"); Exact(hem,("base",400),("light",150),("upper",650),("light",150),("base",50));
        EyeBehavior Eye(string name,int min,int max,params (string,int)[] expected)
        {
            var eye=idle.GetProperty(name); Fields(eye,"waitMinMs","waitMaxMs","track");
            int low=Number(eye.GetProperty("waitMinMs"),1000,120000), high=Number(eye.GetProperty("waitMaxMs"),1000,120000);
            Require(low==min && high==max); var track=Steps(eye.GetProperty("track"),"value"); Exact(track,expected); return new(low,high,track);
        }
        var blink=Eye("blink",4000,7000,("half",60),("closed",80),("half",60),("open",40));
        var wink=Eye("wink",50000,69999,("mid",250),("wink",450),("mid",350),("open",150));
        var interaction=b.GetProperty("interaction"); Fields(interaction,"pickup","hold","release");
        var pickup=interaction.GetProperty("pickup"); Fields(pickup,"sourceDurationMs","tail");
        int pickupMs=Number(pickup.GetProperty("sourceDurationMs"),60,60); count++;
        var pickupTail=Steps(pickup.GetProperty("tail"),"key");
        Exact(pickupTail,("pose:left-panic-B",140),("pose:right-panic-C",140),("pose:left-panic-A",140),("pose:right-panic-B",140),("pose:transition-annoyed-C",80));
        var hold=Steps(interaction.GetProperty("hold"),"key"); Exact(hold,("pose:annoyed-annoyed-A",400),("pose:annoyed-annoyed-B",150),("pose:annoyed-annoyed-C",550),("pose:annoyed-annoyed-B",150),("pose:annoyed-annoyed-A",150));
        var release=interaction.GetProperty("release"); Fields(release,"sourceDurationMs","routes","tails");
        int releaseMs=Number(release.GetProperty("sourceDurationMs"),60,60); count++;
        var tails=new Dictionary<string,IReadOnlyList<BehaviorStep>>(StringComparer.Ordinal);
        foreach(var p in Object(release.GetProperty("tails"),16))
        {
            Match(p.Name,"[a-z0-9-]{1,32}"); var steps=Steps(p.Value,"key"); Require(tails.TryAdd(p.Name,steps));
            Require(steps.Count+1<=64 && steps.Sum(s=>s.DurationMs)+releaseMs<=60000);
        }
        var routes=new Dictionary<string,string>(StringComparer.Ordinal);
        foreach(var p in Object(release.GetProperty("routes"),128))
        {
            string tail=Text(p.Value); Require(images.ContainsKey(p.Name) && tails.ContainsKey(tail) && routes.TryAdd(p.Name,tail));
        }
        Require(routes.Count==images.Count && tails.Count==5 && routes.Values.Distinct().Count()==5);
        void Route(string key,string body)
        {
            Require(routes.TryGetValue(key,out var route)); expectedImages.Add(key);
            Exact(tails[route!],($"pose:{body}-H",100),($"pose:{body}-C",100),("pose:normal-half-B",120),(neutral,160));
        }
        foreach(string key in combos.Values) Route(key,"normal-normal");
        foreach(string body in new[]{"normal-normal","left-panic","right-panic","annoyed-annoyed"}) foreach(string w in new[]{"A","B","C","H"}) Route($"pose:{body}-{w}",body);
        Route("pose:normal-half-B","normal-normal"); Route("pose:transition-annoyed-C","transition-annoyed"); Route("pose:transition-annoyed-H","transition-annoyed");
        Require(expectedImages.SetEquals(images.Keys));
        void Manual(string action,IEnumerable<BehaviorStep> steps)
        {
            Require(clips[action].Frames.SequenceEqual(steps.Select(s=>new Frame(images[s.Value].Path,s.DurationMs))));
        }
        Manual("idle-soft",wing.Select(s=>new BehaviorStep(combos[(s.Value,"open","base")],s.DurationMs)));
        Manual("idle-smile",wink.Track.Select(s=>new BehaviorStep(combos[("A",s.Value,"base")],s.DurationMs)));
        Manual("drag-pickup",new[]{new BehaviorStep(neutral,pickupMs)}.Concat(pickupTail)); Manual("drag-hold",hold);
        Manual("drag-release",new[]{new BehaviorStep(neutral,releaseMs)}.Concat(tails[routes[neutral]]));
        totalItems=checked(totalItems+count); Require(totalItems<=256);
        return new(profile,neutral,images.AsReadOnly(),combos.AsReadOnly(),wing,hem,blink,wink,pickupMs,pickupTail,hold,releaseMs,routes.AsReadOnly(),tails.AsReadOnly());
    }
    private static JsonElement.ObjectEnumerator Object(JsonElement e,int max)
    {
        Require(e.ValueKind==JsonValueKind.Object); var items=e.EnumerateObject(); Require(items.Count() is >0 && items.Count()<=max); return e.EnumerateObject();
    }
    private static void Exact(IReadOnlyList<BehaviorStep> actual,params (string Value,int Ms)[] expected) => Require(actual.SequenceEqual(expected.Select(x=>new BehaviorStep(x.Value,x.Ms))));
}
