using Aemeath.Presentation;
using System.Buffers.Binary;
using System.IO;
using System.Text;
using System.Windows.Media;
using System.Windows.Media.Imaging;
namespace Aemeath.Host;
public static class PngDecoder
{
    public static DecodedImage Decode(byte[] bytes)
    {
        if (bytes.Length > 256 * 1024 || bytes.Length < 33 || !bytes.AsSpan(0, 8).SequenceEqual(new byte[] {137,80,78,71,13,10,26,10}))
            throw new InvalidDataException("png-signature");
        bool header = false, end = false, data = false;
        for (int offset = 8; offset < bytes.Length;)
        {
            if (bytes.Length - offset < 12) throw new InvalidDataException("png-chunk");
            uint length = BinaryPrimitives.ReadUInt32BigEndian(bytes.AsSpan(offset));
            if (length > bytes.Length - offset - 12) throw new InvalidDataException("png-chunk-length");
            int n = (int)length;
            string type = Encoding.ASCII.GetString(bytes, offset + 4, 4);
            var chunk = bytes.AsSpan(offset + 4, n + 4);
            uint crc = 0xffffffff;
            foreach (byte b in chunk) { crc ^= b; for (int i = 0; i < 8; i++) crc = (crc >> 1) ^ ((crc & 1) == 1 ? 0xedb88320u : 0); }
            if (~crc != BinaryPrimitives.ReadUInt32BigEndian(bytes.AsSpan(offset + 8 + n))) throw new InvalidDataException("png-crc");
            if (!header && type != "IHDR") throw new InvalidDataException("png-header");
            if (type is "acTL" or "fcTL" or "fdAT") throw new InvalidDataException("apng");
            if (type == "IHDR")
            {
                if (header || n != 13) throw new InvalidDataException("png-header");
                var h = bytes.AsSpan(offset + 8, n);
                if (BinaryPrimitives.ReadUInt32BigEndian(h) != 96 || BinaryPrimitives.ReadUInt32BigEndian(h[4..]) != 104 ||
                    h[8] != 8 || h[9] != 6 || h[10] != 0 || h[11] != 0 || h[12] > 1) throw new InvalidDataException("png-format");
                header = true;
            }
            data |= type == "IDAT";
            offset += n + 12;
            if (type == "IEND") { if (n != 0 || offset != bytes.Length) throw new InvalidDataException("png-end"); end = true; break; }
        }
        if (!header || !data || !end) throw new InvalidDataException("png-incomplete");
        try
        {
            using var input = new MemoryStream(bytes, writable: false);
            var decoder = new PngBitmapDecoder(input, BitmapCreateOptions.PreservePixelFormat, BitmapCacheOption.OnLoad);
            if (decoder.Frames.Count != 1 || decoder.Frames[0].PixelWidth != 96 || decoder.Frames[0].PixelHeight != 104) throw new InvalidDataException("png-size");
            var source = new FormatConvertedBitmap(decoder.Frames[0], PixelFormats.Bgra32, null, 0);
            var pixels = new byte[96 * 104 * 4]; source.CopyPixels(pixels, 96 * 4, 0);
            bool visible = false;
            for (int i = 3; i < pixels.Length; i += 4) { if (pixels[i] is not (0 or 255)) throw new InvalidDataException("png-alpha"); visible |= pixels[i] == 255; }
            if (!visible) throw new InvalidDataException("png-transparent");
            return new(96, 104, pixels);
        }
        catch (Exception ex) when (ex is NotSupportedException or ArgumentException or System.Runtime.InteropServices.COMException or FileFormatException)
        { throw new InvalidDataException("png-decode", ex); }
    }
}
