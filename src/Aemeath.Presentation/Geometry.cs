namespace Aemeath.Presentation;

public readonly record struct ScreenPx(int X, int Y);
public readonly record struct WorkArea(int Left, int Top, int Right, int Bottom);
public readonly record struct Layout(double WidthDip, double HeightDip, int WidthPx, int HeightPx);
public static class Geometry
{
    public static Layout Size(int scale, uint dpi)
    {
        if (scale is < 1 or > 3 || dpi == 0) throw new ArgumentOutOfRangeException(nameof(scale));
        return new(96 * scale * 96d / dpi, 104 * scale * 96d / dpi, 96 * scale, 104 * scale);
    }
    public static ScreenPx Clamp(ScreenPx origin, int width, int height, WorkArea area)
    {
        if (width <= 0 || height <= 0 || width > (long)area.Right - area.Left || height > (long)area.Bottom - area.Top)
            throw new ArgumentOutOfRangeException(nameof(width));
        return new(Math.Clamp(origin.X, area.Left, area.Right - width), Math.Clamp(origin.Y, area.Top, area.Bottom - height));
    }
}
public sealed class DragSession
{
    public bool Active { get; private set; }
    private ScreenPx offset;
    public void Start(ScreenPx cursor, ScreenPx origin)
    {
        offset = new(checked(cursor.X - origin.X), checked(cursor.Y - origin.Y)); Active = true;
    }
    public ScreenPx Move(ScreenPx cursor)
    {
        if (!Active) throw new InvalidOperationException("Drag is not active.");
        return new(checked(cursor.X - offset.X), checked(cursor.Y - offset.Y));
    }
    public bool End() { var wasActive = Active; Active = false; return wasActive; }
}
