using System.IO;
using System.Windows;
using System.Windows.Input;
using System.Windows.Threading;

namespace Aemeath.Host;

public sealed class App : Application
{
    private DiagnosticWindow? control;
    private DiagnosticLog? log;
    private DispatcherTimer? exitTimer;
    private bool stopping;
    [STAThread] public static void Main(string[] args)
    {
        var app = new App { ShutdownMode = ShutdownMode.OnExplicitShutdown };
        app.Startup += (_, _) => app.Start(args);
        app.Run();
    }
    private void Start(string[] args)
    {
        string package = Path.Combine(AppContext.BaseDirectory, "assets", "diagnostic");
        string? logPath = null, optionError = null, initialClip = null; int? exitAfter = null; int scale = 2;
        for (int i = 0; i < args.Length; i++)
        {
            if (i + 1 >= args.Length) { optionError = "启动参数不完整。"; break; }
            string key = args[i], value = args[++i];
            if (key == "--package") package = value;
            else if (key == "--diagnostics") logPath = value;
            else if (key == "--clip" && value is "neutral" or "idle-soft" or "idle-smile" or "drag-pickup" or "drag-hold" or "drag-release") initialClip = value;
            else if (key == "--scale" && int.TryParse(value, out var k) && k is >= 1 and <= 3) scale = k;
            else if (key == "--exit-after-ms" && int.TryParse(value, out var ms) && ms is >= 100 and <= 60000) exitAfter = ms;
            else { optionError = "启动参数无效。"; break; }
        }
        try { log = new DiagnosticLog(logPath); }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or ArgumentException)
        { log = new DiagnosticLog(null); optionError = "诊断日志不可写；日志已关闭。"; }
        log.Write("startup", new { pid = Environment.ProcessId, timedExit = exitAfter, note = "own-process-diagnostics-not-UI-acceptance" });
        control = new DiagnosticWindow(package, log, Stop);
        MainWindow = control;
        control.Closed += (_, _) => Stop();
        control.Show();
        if (optionError is not null) control.ReportError(optionError);
        else control.Dispatcher.BeginInvoke(DispatcherPriority.ContextIdle, new Action(() => control.LoadInitial(package, initialClip, scale)));
        if (exitAfter is int delay)
        {
            exitTimer = new DispatcherTimer { Interval = TimeSpan.FromMilliseconds(delay) };
            exitTimer.Tick += (_, _) => { log.Write("timed-smoke-exit"); Stop(); };
            exitTimer.Start();
        }
    }
    internal static void InstallExitKey(Window window, Action stop)
    {
        window.PreviewKeyDown += (_, e) =>
        {
            if (e.Key == Key.System && e.SystemKey == Key.X && Keyboard.Modifiers.HasFlag(ModifierKeys.Alt))
            { e.Handled = true; stop(); }
        };
    }
    private void Stop()
    {
        if (stopping) return; stopping = true;
        exitTimer?.Stop(); control?.Stop(); log?.Write("shutdown"); Shutdown();
    }
    protected override void OnExit(ExitEventArgs e)
    {
        exitTimer?.Stop(); control?.Stop(); log?.Dispose(); base.OnExit(e);
    }
}
