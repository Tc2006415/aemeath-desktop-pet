param([Parameter(Mandatory)][string]$Path)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$resolved = (Resolve-Path -LiteralPath $Path).Path
$bytes = [IO.File]::ReadAllBytes($resolved)
$bitmap = [Drawing.Bitmap]::new($resolved)
try {
    $rect = [Drawing.Rectangle]::new(0, 0, $bitmap.Width, $bitmap.Height)
    $data = $bitmap.LockBits($rect, [Drawing.Imaging.ImageLockMode]::ReadOnly, [Drawing.Imaging.PixelFormat]::Format32bppArgb)
    try {
        $pixels = [byte[]]::new([Math]::Abs($data.Stride) * $bitmap.Height)
        [Runtime.InteropServices.Marshal]::Copy($data.Scan0, $pixels, 0, $pixels.Length)
        $counts = [long[]]::new(256)
        for ($y = 0; $y -lt $bitmap.Height; $y++) {
            for ($x = 0; $x -lt $bitmap.Width; $x++) { $counts[$pixels[$y * [Math]::Abs($data.Stride) + $x * 4 + 3]]++ }
        }
        [pscustomobject]@{
            Width = $bitmap.Width; Height = $bitmap.Height; Bytes = $bytes.Length
            PngBitDepth = $bytes[24]; PngColorType = $bytes[25]
            Transparent = $counts[0]; Opaque = $counts[255]
            Semitransparent = ($counts[1..254] | Measure-Object -Sum).Sum
            AlphaValues = ($counts | Where-Object { $_ -gt 0 } | Measure-Object).Count
            SHA256 = (Get-FileHash -LiteralPath $resolved -Algorithm SHA256).Hash
        } | ConvertTo-Json
    } finally { $bitmap.UnlockBits($data) }
} finally { $bitmap.Dispose() }
