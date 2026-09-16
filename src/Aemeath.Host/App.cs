using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;

namespace Aemeath.Host;

public sealed class App : Application
{
    [STAThread]
    public static void Main()
    {
        var app = new App { ShutdownMode = ShutdownMode.OnMainWindowClose };
        var exit = new Button { Content = "退出 (Alt+X)", Margin = new Thickness(12) };
        System.Windows.Automation.AutomationProperties.SetName(exit, "退出诊断宿主");
        exit.Click += (_, _) => app.Shutdown();
        var panel = new StackPanel();
        panel.Children.Add(new TextBlock { Text = "诊断宿主 · 未连接 / 状态未知\n仅诊断素材，不是角色成品。", Margin = new Thickness(12) });
        panel.Children.Add(exit);
        var window = new Window { Title = "爱弥斯宿主诊断（未连接）", Width = 480, Height = 220, Content = panel };
        window.PreviewKeyDown += (_, e) => { if (e.Key == Key.System && e.SystemKey == Key.X) { e.Handled = true; app.Shutdown(); } };
        app.Run(window);
    }
}
