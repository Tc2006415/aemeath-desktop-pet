# QA-only background/scale preview authorized by QA-005; never writes character assets.
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$repoDir = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$source = [Drawing.Bitmap]::new((Join-Path $repoDir 'assets/characters/aemeath-v1/frames/neutral.png'))
$output = Join-Path $repoDir 'artifacts/qa-neutral-background-preview.png'
$canvas = [Drawing.Bitmap]::new(736, 864)
$graphics = [Drawing.Graphics]::FromImage($canvas)
try {
    $graphics.Clear([Drawing.Color]::White)
    $graphics.FillRectangle([Drawing.Brushes]::DimGray, 0, 432, 736, 432)
    # Exact integer replication avoids interpolation or edits to source pixels.
    foreach ($row in 0, 1) {
        $left = 16
        foreach ($scale in 1, 2, 4) {
            for ($y = 0; $y -lt $source.Height; $y++) {
                for ($x = 0; $x -lt $source.Width; $x++) {
                    $color = $source.GetPixel($x, $y)
                    if ($color.A -eq 0) { continue }
                    $brush = [Drawing.SolidBrush]::new($color)
                    try { $graphics.FillRectangle($brush, $left + $x * $scale, $row * 432 + 8 + $y * $scale, $scale, $scale) }
                    finally { $brush.Dispose() }
                }
            }
            $left += $source.Width * $scale + 16
        }
    }
    $canvas.Save($output, [Drawing.Imaging.ImageFormat]::Png)
    Write-Output $output
} finally { $graphics.Dispose(); $canvas.Dispose(); $source.Dispose() }
