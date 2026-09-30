using System.IO;
using System.Security.Cryptography;
using System.Text.Json.Nodes;
using Aemeath.Host;
using Aemeath.Presentation;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace Aemeath.Tests;

internal sealed class BehaviorFixture : IDisposable
{
    internal readonly string Root = Path.Combine(Path.GetTempPath(), "aemeath-v3-" + Guid.NewGuid().ToString("N"));
    internal JsonObject Manifest;
    internal static string PathFor(string key) => "frames/" + key.Replace(':','-').ToLowerInvariant() + ".png";
    internal static JsonArray Track(params (string Value,int Ms)[] items) => new(items.Select(x => (JsonNode)new JsonObject { ["value"]=x.Value,["durationMs"]=x.Ms }).ToArray());
    internal static JsonArray Frames(params (string Key,int Ms)[] items) => new(items.Select(x => (JsonNode)new JsonObject { ["key"]=x.Key,["durationMs"]=x.Ms }).ToArray());
    internal const string Neutral = "idle:A-open-base";
    internal JsonObject Behavior => Manifest["behavior"]!.AsObject();
    internal BehaviorFixture()
    {
        Directory.CreateDirectory(Path.Combine(Root,"frames"));
        byte[] png=PackageTests.Png(); string sha=Convert.ToHexString(SHA256.HashData(png)).ToLowerInvariant();
        var images=new JsonObject(); var combinations=new JsonArray(); var routes=new JsonObject(); var tails=new JsonObject();
        void Add(string key,string route)
        {
            images[key]=new JsonObject { ["path"]=PathFor(key),["sha256"]=sha }; routes[key]=route;
            File.WriteAllBytes(Path.Combine(Root,PathFor(key)),png);
        }
        foreach(string wing in new[]{"A","B","C"}) foreach(string eye in new[]{"open","half","closed","mid","wink"}) foreach(string hem in new[]{"base","light","upper"})
        {
            string key=$"idle:{wing}-{eye}-{hem}"; Add(key,"normal");
            combinations.Add(new JsonObject { ["wing"]=wing,["eyeHead"]=eye,["hem"]=hem,["key"]=key });
        }
        foreach(string body in new[]{"normal-normal","left-panic","right-panic","annoyed-annoyed"})
            foreach(string wing in new[]{"A","B","C","H"}) Add($"pose:{body}-{wing}",body=="normal-normal"?"normal":body=="annoyed-annoyed"?"annoyed":body);
        Add("pose:normal-half-B","normal"); Add("pose:transition-annoyed-C","transition"); Add("pose:transition-annoyed-H","transition");
        foreach(var (id,body) in new[]{("normal","normal-normal"),("left-panic","left-panic"),("right-panic","right-panic"),("annoyed","annoyed-annoyed"),("transition","transition-annoyed")})
            tails[id]=Frames(($"pose:{body}-H",100),($"pose:{body}-C",100),("pose:normal-half-B",120),(Neutral,160));
        var pickup=Frames(("pose:left-panic-B",140),("pose:right-panic-C",140),("pose:left-panic-A",140),("pose:right-panic-B",140),("pose:transition-annoyed-C",80));
        var hold=Frames(("pose:annoyed-annoyed-A",400),("pose:annoyed-annoyed-B",150),("pose:annoyed-annoyed-C",550),("pose:annoyed-annoyed-B",150),("pose:annoyed-annoyed-A",150));
        var actions=new JsonObject();
        void Clip(string id,bool loop,JsonArray keyed)
        {
            var frames=new JsonArray(); foreach(var item in keyed) frames.Add(new JsonObject { ["path"]=PathFor(item!["key"]!.GetValue<string>()),["durationMs"]=item["durationMs"]!.DeepClone() });
            actions[id]=new JsonObject { ["playback"]=loop?"loop":"once",["origin"]="diagnostic",["frames"]=frames };
        }
        Clip("neutral",true,Frames((Neutral,1000)));
        Clip("idle-soft",true,Frames((Neutral,400),("idle:B-open-base",150),("idle:C-open-base",150),("idle:C-open-base",400),("idle:B-open-base",150),(Neutral,150)));
        Clip("idle-smile",false,Frames(("idle:A-mid-base",250),("idle:A-wink-base",450),("idle:A-mid-base",350),(Neutral,150)));
        var manualPickup=Frames((Neutral,60)); foreach(var item in pickup) manualPickup.Add(item!.DeepClone()); Clip("drag-pickup",false,manualPickup);
        Clip("drag-hold",true,(JsonArray)hold.DeepClone());
        var manualRelease=Frames((Neutral,60)); foreach(var item in tails["normal"]!.AsArray()) manualRelease.Add(item!.DeepClone()); Clip("drag-release",false,manualRelease);
        Manifest=new JsonObject {
            ["schemaVersion"]=3,["packageId"]="diagnostic-v3",["packageVersion"]="0.5.0",["packageKind"]="diagnostic",["sourceScale"]=1,
            ["frameSize"]=new JsonObject{["width"]=96,["height"]=104},["anchor"]=new JsonObject{["x"]=48,["y"]=94},["fallbackAction"]="neutral",["actions"]=actions,
            ["behavior"]=new JsonObject {
                ["profile"]="layered-idle-drag-v1",["neutralKey"]=Neutral,["images"]=images,
                ["idle"]=new JsonObject { ["combinations"]=combinations,["wing"]=Track(("A",400),("B",150),("C",150),("C",400),("B",150),("A",150)),
                    ["hem"]=Track(("base",400),("light",150),("upper",650),("light",150),("base",50)),
                    ["blink"]=new JsonObject { ["waitMinMs"]=4000,["waitMaxMs"]=7000,["track"]=Track(("half",60),("closed",80),("half",60),("open",40)) },
                    ["wink"]=new JsonObject { ["waitMinMs"]=50000,["waitMaxMs"]=69999,["track"]=Track(("mid",250),("wink",450),("mid",350),("open",150)) } },
                ["interaction"]=new JsonObject { ["pickup"]=new JsonObject { ["sourceDurationMs"]=60,["tail"]=pickup },["hold"]=hold,
                    ["release"]=new JsonObject { ["sourceDurationMs"]=60,["routes"]=routes,["tails"]=tails } }
            }
        };
    }
    internal AssetPackage Load() { File.WriteAllText(Path.Combine(Root,"manifest.json"),Manifest.ToJsonString()); return PackageLoader.Load(Root,PngDecoder.Decode); }
    public void Dispose() => Directory.Delete(Root,true);
}

[TestClass]
public class BehaviorPackageTests
{
    [TestMethod] public void SchemaThreeLoadsAllLogicalImagesAndManualActions()
    {
        using var f=new BehaviorFixture(); var p=f.Load(); Assert.AreEqual(3,p.SchemaVersion); Assert.AreEqual(64,p.Images.Count); Assert.AreEqual(6,p.Clips.Count); Assert.AreEqual(540,p.Clips["drag-release"].DurationMs);
    }
    [TestMethod] public void MalformedBehaviorRejectsAtomically()
    {
        using var f=new BehaviorFixture(); f.Load(); var original=f.Manifest.DeepClone();
        Action<JsonObject>[] changes=[
            m=>m["behavior"]!["profile"]="script",
            m=>m["behavior"]!["idle"]!["combinations"]!.AsArray().RemoveAt(0),
            m=>m["behavior"]!["images"]![BehaviorFixture.Neutral]!["path"]="../bad.png",
            m=>m["behavior"]!["images"]![BehaviorFixture.Neutral]!["sha256"]=new string('0',64),
            m=>m["behavior"]!["interaction"]!["release"]!["routes"]!.AsObject().Remove(BehaviorFixture.Neutral),
            m=>m["behavior"]!["interaction"]!["release"]!["routes"]!["pose:transition-annoyed-C"]="annoyed",
            m=>m["behavior"]!["idle"]!["blink"]!["waitMaxMs"]=7001,
            m=>m["behavior"]!["idle"]!["blink"]!["track"]![0]!["durationMs"]=59,
            m=>m["behavior"]!["unknown"]=true,
            m=>m["actions"]!["drag-pickup"]!["frames"]![0]!["durationMs"]=61,
            m=>m["behavior"]!["images"]!["idle:A-half-base"]!["path"]=BehaviorFixture.PathFor(BehaviorFixture.Neutral),
            m=>m["behavior"]!["idle"]!["combinations"]![1]=m["behavior"]!["idle"]!["combinations"]![0]!.DeepClone(),
            m=>m["behavior"]!["idle"]!["wing"]![0]!["value"]="C",
            m=>m["behavior"]!["interaction"]!["release"]!["tails"]!["normal"]![0]!["key"]=BehaviorFixture.Neutral,
            m=>m["behavior"]!["interaction"]!["pickup"]!["tail"]![4]!["key"]="pose:annoyed-annoyed-C",
            m=>m["behavior"]!["interaction"]!["pickup"]!["sourceDurationMs"]=59,
            m=>m["behavior"]!["interaction"]!["hold"]=new JsonArray(),
            m=>m["behavior"]!["images"]![BehaviorFixture.Neutral]!["sha256"]="BAD",
            m=>m["behavior"]!["idle"]!["wing"]![0]!["durationMs"]=0.1,
            m=>m["behavior"]!["interaction"]!["release"]!["routes"]=new JsonArray(),
            m=>m["schemaVersion"]=2
        ];
        foreach(var change in changes) { f.Manifest=(JsonObject)original.DeepClone(); change(f.Manifest); Assert.ThrowsExactly<PackageException>(()=>f.Load()); }
        f.Manifest=(JsonObject)original.DeepClone(); var session=new PackageSession(); f.Load(); Assert.IsTrue(session.TryLoad(f.Root,PngDecoder.Decode)); var prior=session.Current;
        File.WriteAllBytes(Path.Combine(f.Root,BehaviorFixture.PathFor("idle:C-wink-upper")),[0]);
        Assert.IsFalse(session.TryLoad(f.Root,PngDecoder.Decode)); Assert.AreSame(prior,session.Current);
    }
    [TestMethod] public void DuplicateBehaviorKeysAndOversizedManifestAreRejected()
    {
        using var f=new BehaviorFixture(); f.Load(); string path=Path.Combine(f.Root,"manifest.json"), json=File.ReadAllText(path);
        File.WriteAllText(path,json.Replace("\"behavior\":{","\"behavior\":{\"profile\":\"layered-idle-drag-v1\","));
        Assert.ThrowsExactly<PackageException>(()=>PackageLoader.Load(f.Root,PngDecoder.Decode));
        File.WriteAllText(path,json+new string(' ',65536)); Assert.ThrowsExactly<PackageException>(()=>PackageLoader.Load(f.Root,PngDecoder.Decode));
    }
}
