using System.Runtime.InteropServices;
using System.Text;
using Microsoft.Win32.SafeHandles;

namespace Aemeath.Presentation;

// Windows host boundary: hold directories without DELETE sharing and inspect opened handles.
// OPEN_REPARSE_POINT prevents following a replaced final component. Final-path checks reject aliases.
internal sealed class PackageFiles : IDisposable
{
    private readonly string root;
    private readonly SafeFileHandle rootHandle;
    private SafeFileHandle? framesHandle;
    internal PackageFiles(string path)
    {
        root = Path.TrimEndingDirectorySeparator(Path.GetFullPath(path));
        if (root.StartsWith("\\\\", StringComparison.Ordinal)) throw new PackageException("local-path-required");
        rootHandle = Open(root, directory: true, exactName: false);
    }
    internal byte[] Read(string relative, int maximum)
    {
        if (relative.StartsWith("frames/", StringComparison.Ordinal))
            framesHandle ??= Open(Path.Combine(root, "frames"), directory: true);
        var full = Path.GetFullPath(Path.Combine(root, relative));
        if (!full.StartsWith(root + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase)) throw new PackageException("path-boundary");
        using var handle = Open(full, directory: false);
        using var stream = new FileStream(handle, FileAccess.Read);
        if (stream.Length > maximum) throw new PackageException("resource-limit");
        var bytes = new byte[checked((int)stream.Length)]; stream.ReadExactly(bytes);
        if (stream.ReadByte() != -1) throw new PackageException("file-changed");
        return bytes;
    }
    private static SafeFileHandle Open(string path, bool directory, bool exactName = true)
    {
        var handle = CreateFileW(path, directory ? 0x80u : 0x80000000u, directory ? 3u : 1u,
            IntPtr.Zero, 3, 0x00200000u | (directory ? 0x02000000u : 0), IntPtr.Zero);
        if (handle.IsInvalid) { handle.Dispose(); throw new IOException("package-file-access"); }
        try
        {
            if (!GetFileInformationByHandle(handle, out var info) || (info.Attributes & 0x400) != 0 || ((info.Attributes & 0x10) != 0) != directory)
                throw new PackageException("reparse-or-file-type");
            var actual = new StringBuilder(32768);
            var count = GetFinalPathNameByHandleW(handle, actual, (uint)actual.Capacity, 0);
            if (count == 0 || count >= actual.Capacity) throw new PackageException("path-inspection");
            var resolved = actual.ToString();
            if (resolved.StartsWith("\\\\?\\", StringComparison.Ordinal)) resolved = resolved[4..];
            if (!string.Equals(resolved, path, StringComparison.OrdinalIgnoreCase) ||
                (exactName && !string.Equals(Path.GetFileName(resolved), Path.GetFileName(path), StringComparison.Ordinal)))
                throw new PackageException("path-changed-or-case");
            return handle;
        }
        catch { handle.Dispose(); throw; }
    }
    public void Dispose() { framesHandle?.Dispose(); rootHandle.Dispose(); }
    [StructLayout(LayoutKind.Sequential)] private struct FileInfo
    {
        public uint Attributes;
        public System.Runtime.InteropServices.ComTypes.FILETIME Creation, Access, Write;
        public uint Volume, SizeHigh, SizeLow, Links, IndexHigh, IndexLow;
    }
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern SafeFileHandle CreateFileW(string name, uint access, uint share, IntPtr security, uint creation, uint flags, IntPtr template);
    [DllImport("kernel32.dll", SetLastError = true)] [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool GetFileInformationByHandle(SafeFileHandle file, out FileInfo info);
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern uint GetFinalPathNameByHandleW(SafeFileHandle file, StringBuilder path, uint length, uint flags);
}
