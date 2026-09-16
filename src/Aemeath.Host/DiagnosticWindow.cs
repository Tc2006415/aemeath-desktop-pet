using System.Windows;
using System.Windows.Automation;
using System.Windows.Controls;
using Aemeath.Presentation;

namespace Aemeath.Host;

internal sealed class DiagnosticWindow : Window
{
    private readonly PackageSession session = new();
    private readonly TextBox path;
    private readonly TextBlock packageLabel = new() { TextWrapping = TextWrapping.Wrap };
    private readonly TextBlock metrics = new() { Text = "尚未加载", TextWrapping = TextWrapping.Wrap };
    private readonly TextBlock errors = new() { TextWrapping = TextWrapping.Wrap };
    private readonly ComboBox actions = new() { MinWidth = 180, SelectedIndex = 0 };
    private readonly CheckBox automatic = new() { Content = "自动角色交互（待机 / 笑脸 / 拖动）", Margin = new Thickness(0, 10, 0, 4) };
    private readonly Button playButton;
    private readonly PetWindow pet;
    private readonly DiagnosticLog log;
    private bool stopped;
    public DiagnosticWindow(string initialPackage, DiagnosticLog log, Action shutdown)
    {
        this.log = log;
        pet = new PetWindow(log, text => metrics.Text = text, ReportError);
        Title = "爱弥斯宿主诊断（模拟/未连接）"; Width = 640; Height = 510; MinWidth = 480; MinHeight = 420;
        var panel = new StackPanel { Margin = new Thickness(20) }; Content = new ScrollViewer { Content = panel, VerticalScrollBarVisibility = ScrollBarVisibility.Auto };
        AddText(panel, "来源：未连接 · 任务状态：未知", 20);
        AddText(panel, "本地角色交互 / 手动诊断；没有真实 Codex 联动。笑脸不表示任务成功。");
        AddText(panel, "本地素材包目录");
        path = new TextBox { Text = initialPackage, Margin = new Thickness(0, 4, 0, 8) }; SetAccessibleName(path, "本地素材包目录"); panel.Children.Add(path);
        var loading = new StackPanel { Orientation = Orientation.Horizontal };
        loading.Children.Add(Button("加载 / 重载", LoadPackage));
        loading.Children.Add(Button("重新居中", () => { if (session.Current is not null) { pet.Show(); pet.Center(); } }));
        panel.Children.Add(loading); panel.Children.Add(packageLabel);
        SetAccessibleName(automatic, "自动角色交互模式");
        panel.Children.Add(automatic);
        AddText(panel, "勾选自动模式：待机 15 秒后笑脸一次；拖动时拎起、悬停、松手。取消勾选恢复手动诊断。");
        foreach (var action in new[] { "neutral", "idle-soft", "idle-smile", "drag-pickup", "drag-hold", "drag-release" }) actions.Items.Add(action);
        SetAccessibleName(actions, "手动选择诊断动作");
        var playback = new StackPanel { Orientation = Orientation.Horizontal, Margin = new Thickness(0, 12, 0, 8) };
        playButton = Button("播放所选动作", () => pet.Play((string)actions.SelectedItem));
        playback.Children.Add(actions); playback.Children.Add(playButton); panel.Children.Add(playback);
        automatic.Checked += (_, _) => ChangeMode(true);
        automatic.Unchecked += (_, _) => ChangeMode(false);
        var scales = new StackPanel { Orientation = Orientation.Horizontal };
        foreach (int scale in new[] { 1, 2, 3 }) scales.Children.Add(Button($"{scale}× 像素", () => pet.SetScale(scale)));
        var topmost = new CheckBox { Content = "置顶", Margin = new Thickness(12, 8, 0, 0) }; SetAccessibleName(topmost, "像素窗口置顶");
        topmost.Checked += (_, _) => pet.Topmost = true; topmost.Unchecked += (_, _) => pet.Topmost = false;
        scales.Children.Add(topmost); panel.Children.Add(scales); panel.Children.Add(metrics);
        errors.Margin = new Thickness(0, 10, 0, 10); SetAccessibleName(errors, "素材和窗口错误"); panel.Children.Add(errors);
        AddText(panel, "拖动色块可见部分；Esc 取消拖动。先选择 idle-soft，再观察拖动时持续换帧。透明留白命中与实际像素清晰度需要人工检查。");
        panel.Children.Add(Button("退出 (Alt+X)", shutdown, "退出诊断宿主"));
        pet.Closed += (_, _) => shutdown();
        App.InstallExitKey(this, shutdown); App.InstallExitKey(pet, shutdown);
        ContentRendered += (_, _) => log.Write("control-rendered");
    }
    private static void SetAccessibleName(DependencyObject control, string name) => AutomationProperties.SetName(control, name);
    private static Button Button(string label, Action action, string? name = null)
    {
        var button = new Button { Content = label, Padding = new Thickness(10, 5, 10, 5), Margin = new Thickness(0, 0, 8, 8) };
        SetAccessibleName(button, name ?? label); button.Click += (_, _) => action(); return button;
    }
    private static void AddText(Panel parent, string text, double fontSize = 14)
        => parent.Children.Add(new TextBlock { Text = text, FontSize = fontSize, TextWrapping = TextWrapping.Wrap, Margin = new Thickness(0, 0, 0, 8) });
    public void ReportError(string text) { errors.Text = text; }
    private void ChangeMode(bool enabled)
    {
        actions.IsEnabled = playButton.IsEnabled = !enabled; pet.SetAutomatic(enabled);
    }
    internal void LoadInitial(string root, string? clip, int scale, bool autoMode)
    {
        path.Text = root; pet.SetScale(scale); automatic.IsChecked = autoMode; LoadPackage();
        if (clip is not null && !autoMode) { actions.SelectedItem = clip; pet.Play(clip); }
    }
    public void LoadPackage()
    {
        if (stopped) return;
        if (!session.TryLoad(path.Text, PngDecoder.Decode))
        {
            ReportError($"素材加载失败：{session.Error}。{(session.Current is null ? "没有可用素材；控制窗仍可退出。" : "继续使用原有效包。")}");
            log.Write("package-rejected", new { category = session.Error, retained = session.Current is not null }); return;
        }
        var package = session.Current!;
        string kind = package.Kind == "diagnostic" ? "诊断素材（不是角色成品）" : "角色素材声明（未代表视觉验收）";
        packageLabel.Text = $"{kind} · {package.Id} / {package.Version}";
        var unavailable = new[] { "neutral", "idle-soft", "idle-smile", "drag-pickup", "drag-hold", "drag-release" }.Where(id => !package.Clips.ContainsKey(id));
        ReportError($"可播放：{string.Join(", ", package.Clips.Keys)}\n缺失或停用：{string.Join(", ", unavailable)}");
        // Loaded/ApplyLayout may report a positioning failure. Do not overwrite that error after Show.
        pet.SetPackage(package); pet.Show();
    }
    public void Stop()
    {
        if (stopped) return; stopped = true; pet.Stop(); pet.Close();
    }
}
