using System.ComponentModel;
using System.Diagnostics;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Interop;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Threading;
using Aemeath.Presentation;
using Geometry = Aemeath.Presentation.Geometry;

namespace Aemeath.Host;

internal sealed class PetWindow : Window
{
    private readonly Image image = new() { Stretch = Stretch.Fill };
    private readonly Stopwatch clock = Stopwatch.StartNew();
    private readonly DragSession drag = new();
    private readonly DiagnosticLog log;
    private readonly Action<string> status, error;
    private AssetPackage? package;
    private CharacterController? controller;
    private bool automatic;
    private Dictionary<string, BitmapSource> images = [];
    private HwndSource? source;
    private IntPtr hwnd;
    private WorkArea area;
    private int scale = 2;
    private uint dpi;
    private bool stopped, positionPaused, layoutPending, renderingSubscribed, rendered;
    private string? lastFrame;
    private TimeSpan lastRendering = TimeSpan.MinValue;
    public PetWindow(DiagnosticLog log, Action<string> status, Action<string> error)
    {
        this.log = log; this.status = status; this.error = error;
        Title = "爱弥斯诊断像素"; WindowStyle = WindowStyle.None; AllowsTransparency = true;
        Background = Brushes.Transparent; ResizeMode = ResizeMode.NoResize; ShowInTaskbar = false;
        Width = 192; Height = 208; Content = image; UseLayoutRounding = false;
        RenderOptions.SetBitmapScalingMode(image, BitmapScalingMode.NearestNeighbor);
        SourceInitialized += (_, _) => { hwnd = new WindowInteropHelper(this).Handle; source = HwndSource.FromHwnd(hwnd); source?.AddHook(WindowMessage); };
        Loaded += (_, _) =>
        {
            ApplyLayout(true);
            if (!renderingSubscribed) { CompositionTarget.Rendering += Render; renderingSubscribed = true; }
            log.Write("pet-loaded", new { hwnd = hwnd.ToInt64() });
        };
        MouseLeftButtonDown += StartDrag; MouseMove += MoveDrag;
        MouseLeftButtonUp += (_, _) => EndDrag("mouse-up");
        LostMouseCapture += (_, _) => EndDrag("capture-loss");
        Deactivated += (_, _) => EndDrag("deactivated");
        PreviewKeyDown += (_, e) => { if (e.Key == Key.Escape) { EndDrag("escape"); e.Handled = true; } };
        Closed += (_, _) => Stop();
    }
    public void SetPackage(AssetPackage next)
    {
        EndDrag("package-change");
        var nextImages = new Dictionary<string, BitmapSource>(StringComparer.Ordinal);
        foreach (var (path, decoded) in next.Images)
        {
            var bitmap = BitmapSource.Create(96, 104, 96, 96, PixelFormats.Bgra32, null, decoded.Bgra, 96 * 4);
            bitmap.Freeze(); nextImages.Add(path, bitmap);
        }
        package = next; images = nextImages;
        controller = new CharacterController(next.Clips, () => clock.ElapsedMilliseconds);
        controller.SetAutomatic(automatic);
        lastFrame = null; Draw();
        log.Write("package-loaded", new { next.Id, next.Version, next.Kind, disabled = next.DisabledActions.Keys });
    }
    public void Play(string action)
    {
        if (controller is null) return;
        if (automatic) { error("自动模式中不能手动选择动作；请先切换到手动模式。"); return; }
        bool available = controller.PlayManual(action);
        log.Write("play-request", new { action, available });
        if (!available) error("动作缺失或已停用；已回 neutral。");
        Draw();
    }
    public void SetAutomatic(bool enabled)
    {
        if (automatic == enabled) return;
        EndDrag("mode-change"); automatic = enabled; controller?.SetAutomatic(enabled);
        log.Write("mode", new { automatic }); lastFrame = null; Draw();
    }
    public void SetScale(int next) { EndDrag("scale-change"); var prior = scale; scale = next; ApplyLayout(false, prior); }
    public void Center() { EndDrag("recenter"); ApplyLayout(true); }
    private void Render(object? sender, EventArgs e)
    {
        if (stopped || e is not RenderingEventArgs rendering || rendering.RenderingTime == lastRendering) return;
        if (!rendered) { rendered = true; log.Write("render-callback"); }
        lastRendering = rendering.RenderingTime; Draw();
    }
    private void Draw()
    {
        if (controller is null || package is null || stopped) return;
        var sample = controller.Sample();
        var path = package.Clips[sample.Action].Frames[sample.FrameIndex].Path;
        image.Source = images[path];
        var key = $"{sample.PlaybackId}:{sample.Action}:{sample.FrameIndex}";
        if (key != lastFrame)
        {
            lastFrame = key;
            log.Write("frame", new { sample.Action, sample.FrameIndex, sample.PlaybackId, dragging = drag.Active, automatic });
            status($"{(automatic ? "自动交互" : "手动诊断")} · {sample.Action} · 帧 {sample.FrameIndex + 1} · DPI {dpi} · 倍率 {scale}× · {(drag.Active ? "拖动中" : "未拖动")}");
        }
        if (sample.CompletedId is long completed) log.Write("natural-end", new { completed });
    }
    private void StartDrag(object sender, MouseButtonEventArgs e)
    {
        if (positionPaused || stopped) return;
        try
        {
            var cursor = NativeMethods.Cursor(); var rect = NativeMethods.Bounds(hwnd);
            if (!CaptureMouse()) { error("鼠标捕获失败；未进入拖动。"); return; }
            drag.Start(cursor, new(rect.Left, rect.Top));
            controller?.BeginDrag();
            Focus();
            log.Write("drag-start", new { cursor, origin = new ScreenPx(rect.Left, rect.Top) });
            lastFrame = null; Draw(); e.Handled = true;
        }
        catch (Win32Exception) { FailPosition(); }
    }
    private void MoveDrag(object sender, MouseEventArgs e)
    {
        if (!drag.Active || positionPaused) return;
        if (e.LeftButton != MouseButtonState.Pressed) { EndDrag("button-not-pressed"); return; }
        try
        {
            var cursor = NativeMethods.Cursor(); var desired = drag.Move(cursor);
            var layout = Geometry.Size(scale, dpi); var clamped = Geometry.Clamp(desired, layout.WidthPx, layout.HeightPx, area);
            NativeMethods.Position(hwnd, clamped);
            var actual = NativeMethods.Bounds(hwnd);
            log.Write("drag-move", new { cursor, desired, clamped, actual = new ScreenPx(actual.Left, actual.Top), frame = lastFrame });
        }
        catch (Win32Exception) { FailPosition(); }
    }
    public void EndDrag(string reason)
    {
        // Clear first: ReleaseMouseCapture synchronously raises LostMouseCapture.
        if (!drag.End()) return;
        if (IsMouseCaptured) ReleaseMouseCapture();
        controller?.EndDrag();
        log.Write("drag-end", new { reason }); lastFrame = null; Draw();
    }
    private void ApplyLayout(bool center, int? oldScale = null)
    {
        if (hwnd == IntPtr.Zero || stopped) return;
        positionPaused = true;
        try
        {
            area = NativeMethods.PrimaryWorkArea(); dpi = NativeMethods.GetDpiForWindow(hwnd);
            if (dpi == 0) throw new Win32Exception();
            int previous = oldScale ?? scale;
            while (scale > 1 && (96 * scale > area.Right - area.Left || 104 * scale > area.Bottom - area.Top)) scale--;
            var layout = Geometry.Size(scale, dpi); var rect = NativeMethods.Bounds(hwnd);
            var origin = center ? new ScreenPx(area.Left + (area.Right - area.Left - layout.WidthPx) / 2, area.Top + (area.Bottom - area.Top - layout.HeightPx) / 2)
                : new ScreenPx(rect.Left + 48 * (previous - scale), rect.Top + 94 * (previous - scale));
            origin = Geometry.Clamp(origin, layout.WidthPx, layout.HeightPx, area);
            Width = image.Width = layout.WidthDip; Height = image.Height = layout.HeightDip;
            NativeMethods.Position(hwnd, origin, layout.WidthPx, layout.HeightPx);
            positionPaused = false;
            var actual = NativeMethods.Bounds(hwnd); var client = NativeMethods.ClientOrigin(hwnd);
            log.Write("layout", new { dpi, scale, widthPx = actual.Right - actual.Left, heightPx = actual.Bottom - actual.Top,
                layout.WidthDip, layout.HeightDip, origin, client, clientOffsetX = client.X - actual.Left, clientOffsetY = client.Y - actual.Top });
            lastFrame = null; Draw();
        }
        catch (Exception ex) when (ex is Win32Exception or ArgumentOutOfRangeException)
        { FailPosition(); Hide(); error("当前显示参数不受支持。像素窗口已隐藏；可重新居中重试或退出。"); }
    }
    private void FailPosition()
    {
        positionPaused = true; EndDrag("position-error"); log.Write("position-error");
        error("窗口定位失败，拖动已停止。请重新居中或重启。");
    }
    private IntPtr WindowMessage(IntPtr h, int msg, IntPtr w, IntPtr l, ref bool handled)
    {
        if (msg is 0x02E0 or 0x007E) // WM_DPICHANGED / WM_DISPLAYCHANGE
        {
            EndDrag("display-change"); positionPaused = true;
            if (!layoutPending)
            {
                layoutPending = true;
                Dispatcher.BeginInvoke(DispatcherPriority.Loaded, new Action(() => { layoutPending = false; ApplyLayout(true); }));
            }
        }
        return IntPtr.Zero;
    }
    public void Stop()
    {
        if (stopped) return;
        EndDrag("shutdown"); stopped = true;
        if (renderingSubscribed) { CompositionTarget.Rendering -= Render; renderingSubscribed = false; }
        source?.RemoveHook(WindowMessage);
        image.Source = null; images.Clear(); controller = null; package = null;
        log.Write("pet-stopped");
    }
}
