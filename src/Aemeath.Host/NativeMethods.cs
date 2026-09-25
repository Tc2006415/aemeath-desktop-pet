using System.ComponentModel;
using System.Runtime.InteropServices;
using Aemeath.Presentation;

namespace Aemeath.Host;

internal static class NativeMethods
{
    [StructLayout(LayoutKind.Sequential)] internal struct Point { public int X, Y; }
    [StructLayout(LayoutKind.Sequential)] internal struct Rect { public int Left, Top, Right, Bottom; }
    [StructLayout(LayoutKind.Sequential)] private struct MonitorInfo { public int Size; public Rect Monitor, Work; public uint Flags; }
    internal static ScreenPx Cursor()
    {
        if (!GetCursorPos(out var p)) throw new Win32Exception(); return new(p.X, p.Y);
    }
    internal static Rect Bounds(IntPtr hwnd)
    {
        if (!GetWindowRect(hwnd, out var r)) throw new Win32Exception(); return r;
    }
    internal static ScreenPx ClientOrigin(IntPtr hwnd)
    {
        var p = new Point(); if (!ClientToScreen(hwnd, ref p)) throw new Win32Exception(); return new(p.X, p.Y);
    }
    internal static WorkArea PrimaryWorkArea()
    {
        var monitor = MonitorFromPoint(new Point(), 1); var info = new MonitorInfo { Size = Marshal.SizeOf<MonitorInfo>() };
        if (monitor == IntPtr.Zero || !GetMonitorInfoW(monitor, ref info)) throw new Win32Exception();
        return new(info.Work.Left, info.Work.Top, info.Work.Right, info.Work.Bottom);
    }
    internal static void Position(IntPtr hwnd, ScreenPx p, int? width = null, int? height = null)
    {
        uint flags = 0x0010 | 0x0004; // NOACTIVATE | NOZORDER; never touch other applications.
        if (width is null) flags |= 0x0001; // NOSIZE
        if (!SetWindowPos(hwnd, IntPtr.Zero, p.X, p.Y, width ?? 0, height ?? 0, flags)) throw new Win32Exception();
    }
    [DllImport("user32.dll")] internal static extern uint GetDpiForWindow(IntPtr hwnd);
    [DllImport("user32.dll", SetLastError = true)] [return: MarshalAs(UnmanagedType.Bool)] private static extern bool GetCursorPos(out Point point);
    [DllImport("user32.dll", SetLastError = true)] [return: MarshalAs(UnmanagedType.Bool)] private static extern bool GetWindowRect(IntPtr hwnd, out Rect rect);
    [DllImport("user32.dll", SetLastError = true)] [return: MarshalAs(UnmanagedType.Bool)] private static extern bool ClientToScreen(IntPtr hwnd, ref Point point);
    [DllImport("user32.dll")] private static extern IntPtr MonitorFromPoint(Point point, uint flags);
    [DllImport("user32.dll", CharSet = CharSet.Unicode, SetLastError = true)] [return: MarshalAs(UnmanagedType.Bool)] private static extern bool GetMonitorInfoW(IntPtr monitor, ref MonitorInfo info);
    [DllImport("user32.dll", SetLastError = true)] [return: MarshalAs(UnmanagedType.Bool)] private static extern bool SetWindowPos(IntPtr hwnd, IntPtr insertAfter, int x, int y, int width, int height, uint flags);
}
