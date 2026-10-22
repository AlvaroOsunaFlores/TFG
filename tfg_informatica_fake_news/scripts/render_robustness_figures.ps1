Add-Type -AssemblyName System.Drawing

$runId = 'robustness-1a94400d502b149f'
$runOut = Join-Path (Get-Location) (Join-Path 'reports\robustness_runs' (Join-Path $runId 'figures'))
New-Item -ItemType Directory -Force -Path $runOut | Out-Null

$navy = [System.Drawing.Color]::FromArgb(37, 79, 125)
$blue = [System.Drawing.Color]::FromArgb(67, 125, 177)
$green = [System.Drawing.Color]::FromArgb(69, 143, 115)
$red = [System.Drawing.Color]::FromArgb(184, 83, 83)
$gray = [System.Drawing.Color]::FromArgb(105, 112, 120)
$light = [System.Drawing.Color]::FromArgb(229, 236, 243)
$grid = [System.Drawing.Color]::FromArgb(218, 223, 228)

function New-Canvas([int]$width, [int]$height) {
    $bitmap = New-Object System.Drawing.Bitmap($width, $height)
    $bitmap.SetResolution(300, 300)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
    $graphics.Clear([System.Drawing.Color]::White)
    return @{ Bitmap = $bitmap; Graphics = $graphics }
}

function Add-Text($graphics, [string]$text, [float]$x, [float]$y, [float]$size = 30, [System.Drawing.Color]$color = $navy, [bool]$bold = $false) {
    $style = if ($bold) { [System.Drawing.FontStyle]::Bold } else { [System.Drawing.FontStyle]::Regular }
    $font = New-Object System.Drawing.Font('Arial', $size, $style, [System.Drawing.GraphicsUnit]::Pixel)
    $brush = New-Object System.Drawing.SolidBrush($color)
    $graphics.DrawString($text, $font, $brush, $x, $y)
    $font.Dispose(); $brush.Dispose()
}

function Add-Line($graphics, [System.Drawing.Color]$color, [float]$x1, [float]$y1, [float]$x2, [float]$y2, [float]$width = 3) {
    $pen = New-Object System.Drawing.Pen($color, $width)
    $graphics.DrawLine($pen, $x1, $y1, $x2, $y2)
    $pen.Dispose()
}

function Add-Arrow($graphics, [float]$x1, [float]$y1, [float]$x2, [float]$y2, [System.Drawing.Color]$color = $gray) {
    $pen = New-Object System.Drawing.Pen($color, 5)
    $pen.EndCap = [System.Drawing.Drawing2D.LineCap]::ArrowAnchor
    $graphics.DrawLine($pen, $x1, $y1, $x2, $y2)
    $pen.Dispose()
}

function Add-Box($graphics, [float]$x, [float]$y, [float]$w, [float]$h, [string[]]$lines, [System.Drawing.Color]$fill = $light) {
    $rect = New-Object System.Drawing.RectangleF($x, $y, $w, $h)
    $brush = New-Object System.Drawing.SolidBrush($fill)
    $pen = New-Object System.Drawing.Pen($navy, 3)
    $graphics.FillRectangle($brush, $rect); $graphics.DrawRectangle($pen, $x, $y, $w, $h)
    $lineHeight = 42
    $startY = $y + (($h - ($lines.Count * $lineHeight)) / 2)
    foreach ($line in $lines) {
        $font = New-Object System.Drawing.Font('Arial', 27, [System.Drawing.FontStyle]::Regular, [System.Drawing.GraphicsUnit]::Pixel)
        $measure = $graphics.MeasureString($line, $font)
        Add-Text $graphics $line ($x + (($w - $measure.Width) / 2)) $startY 27 $navy $false
        $font.Dispose()
        $startY += $lineHeight
    }
    $brush.Dispose(); $pen.Dispose()
}

# Figure 2: derived-corpus composition, based on the final row-level audit.
$canvas = New-Canvas 1800 850; $g = $canvas.Graphics
Add-Text $g 'Composicion del corpus derivado' 100 45 42 $navy $true
Add-Text $g 'Registros conservados por fuente y etiqueta' 100 105 28 $gray
$x0 = 650; $scale = 0.023; $barH = 66
$rows = @(
    @{Name='archive2 / no_fake'; Count=20926; Color=$blue; Y=220},
    @{Name='archive2 / fake_news'; Count=17900; Color=$red; Y=345},
    @{Name='LIAR / no_fake'; Count=2049; Color=$blue; Y=500},
    @{Name='LIAR / fake_news'; Count=3533; Color=$red; Y=625}
)
foreach ($row in $rows) {
    Add-Text $g $row.Name 100 ($row.Y+13) 29 $navy $true
    $w = $row.Count * $scale
    $rect = New-Object System.Drawing.RectangleF($x0, $row.Y, $w, $barH)
    $brush = New-Object System.Drawing.SolidBrush($row.Color)
    $g.FillRectangle($brush, $rect); $brush.Dispose()
    Add-Text $g ('{0:N0}' -f $row.Count) ($x0 + $w + 16) ($row.Y+15) 27 $navy $true
}
Add-Text $g 'Barras en escala comun; los valores absolutos aparecen al final de cada barra.' 100 755 25 $gray
$canvas.Bitmap.Save((Join-Path $runOut 'figure2_derived_corpus.png'), [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $canvas.Bitmap.Dispose()

# Figure 4: grouped cross-validation plus the two isolated source-transfer directions.
$canvas = New-Canvas 1800 950; $g = $canvas.Graphics
Add-Text $g 'Protocolo experimental del run de robustez' 70 30 40 $navy $true
$topY = 150; $boxW = 300; $boxH = 170; $gap = 45; $x = 55
$cvBoxes = @(
    @{Lines=@('Corpus derivado','44.408 filas','grupos de duplicados'); Fill=$light},
    @{Lines=@('5 particiones','StratifiedGroupKFold','semilla 42'); Fill=$light},
    @{Lines=@('Ajuste dentro','de cada fold','TF-IDF + modelo'); Fill=$light},
    @{Lines=@('Predicciones','fuera de entrenamiento','una por registro'); Fill=[System.Drawing.Color]::FromArgb(231,241,236)},
    @{Lines=@('Comparacion','macro F1 medio','+/- DE muestral'); Fill=[System.Drawing.Color]::FromArgb(231,241,236)}
)
for ($i=0; $i -lt $cvBoxes.Count; $i++) {
    $bx = $x + ($i * ($boxW + $gap)); Add-Box $g $bx $topY $boxW $boxH $cvBoxes[$i].Lines $cvBoxes[$i].Fill
    if ($i -lt $cvBoxes.Count - 1) { Add-Arrow $g ($bx + $boxW + 5) ($topY + ($boxH / 2)) ($bx + $boxW + $gap - 8) ($topY + ($boxH / 2)) }
}
Add-Text $g 'Evaluaciones de transferencia independientes' 70 430 32 $navy $true
Add-Box $g 160 525 560 170 @('archive2 -> LIAR','ajuste en archive2','prueba en LIAR') ([System.Drawing.Color]::FromArgb(242,235,235))
Add-Box $g 1080 525 560 170 @('LIAR -> archive2','ajuste en LIAR','prueba en archive2') ([System.Drawing.Color]::FromArgb(242,235,235))
Add-Text $g 'Se excluyen grupos mixtos; no se detectaron en este corpus derivado.' 150 755 27 $gray
$canvas.Bitmap.Save((Join-Path $runOut 'figure4_grouped_protocol.png'), [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $canvas.Bitmap.Dispose()

# Figure 6: fold means with sample standard-deviation whiskers; axis truncation is disclosed in the caption.
$canvas = New-Canvas 1800 900; $g = $canvas.Graphics
Add-Text $g 'Macro F1 medio por validacion cruzada agrupada' 80 30 39 $navy $true
$left=350; $right=1600; $top=160; $bottom=690; $min=0.930; $max=0.945
for ($tick=930; $tick -le 945; $tick+=3) {
    $val=$tick/1000.0; $yy=$bottom-(($val-$min)/($max-$min))*($bottom-$top)
    Add-Line $g $grid $left $yy $right $yy 2
    Add-Text $g ('{0:N3}' -f $val) 230 ($yy-18) 25 $gray
}
Add-Line $g $gray $left $top $left $bottom 3; Add-Line $g $gray $left $bottom $right $bottom 3
Add-Text $g 'Regresion logistica' 430 730 30 $navy $true
Add-Text $g 'Linear SVC' 1150 730 30 $navy $true
$points = @(
    @{X=690; Mean=.9392435036; Std=.0012758471; Color=$blue; Text='0,9392 +/- 0,0013'},
    @{X=1320; Mean=.9387658566; Std=.0019514004; Color=$green; Text='0,9388 +/- 0,0020'}
)
foreach ($point in $points) {
    $yMean=$bottom-(($point.Mean-$min)/($max-$min))*($bottom-$top)
    $yHi=$bottom-((($point.Mean+$point.Std)-$min)/($max-$min))*($bottom-$top)
    $yLo=$bottom-((($point.Mean-$point.Std)-$min)/($max-$min))*($bottom-$top)
    Add-Line $g $point.Color $point.X $yHi $point.X $yLo 8
    Add-Line $g $point.Color ($point.X-22) $yHi ($point.X+22) $yHi 6
    Add-Line $g $point.Color ($point.X-22) $yLo ($point.X+22) $yLo 6
    $brush=New-Object System.Drawing.SolidBrush($point.Color); $g.FillEllipse($brush,($point.X-18),($yMean-18),36,36); $brush.Dispose()
    Add-Text $g $point.Text ($point.X-145) ($yHi-55) 27 $navy $true
}
Add-Text $g 'Macro F1 (eje mostrado: 0,930-0,945)' 640 815 26 $gray
$canvas.Bitmap.Save((Join-Path $runOut 'figure6_cv_macro_f1.png'), [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $canvas.Bitmap.Dispose()

# Figure 7: aggregated out-of-fold confusion matrix for the model selected by mean macro F1.
$canvas = New-Canvas 1800 900; $g = $canvas.Graphics
Add-Text $g 'Predicciones fuera de entrenamiento: regresion logistica' 80 35 38 $navy $true
Add-Text $g 'Prediccion' 840 145 30 $navy $true
Add-Text $g 'no_fake' 835 205 28 $navy $true
Add-Text $g 'fake_news' 1160 205 28 $navy $true
Add-Text $g 'Etiqueta real' 125 485 28 $navy $true
Add-Text $g 'no_fake' 260 355 30 $navy $true
Add-Text $g 'fake_news' 260 590 30 $navy $true
$cx=700; $cy=280; $cw=400; $ch=210
$cells=@(
    @{X=$cx;Y=$cy;Value='21.819';Fill=[System.Drawing.Color]::FromArgb(63,111,153);White=$true},
    @{X=($cx+$cw);Y=$cy;Value='1.156';Fill=[System.Drawing.Color]::FromArgb(221,232,241);White=$false},
    @{X=$cx;Y=($cy+$ch);Value='1.537';Fill=[System.Drawing.Color]::FromArgb(221,232,241);White=$false},
    @{X=($cx+$cw);Y=($cy+$ch);Value='19.896';Fill=[System.Drawing.Color]::FromArgb(72,137,108);White=$true}
)
foreach ($cell in $cells) {
    $brush=New-Object System.Drawing.SolidBrush($cell.Fill); $g.FillRectangle($brush,$cell.X,$cell.Y,$cw,$ch); $brush.Dispose()
    $fontColor=if($cell.White){[System.Drawing.Color]::White}else{$navy}
    Add-Text $g $cell.Value ($cell.X+115) ($cell.Y+77) 42 $fontColor $true
}
Add-Text $g 'Matriz global: [[21.819, 1.156], [1.537, 19.896]]' 680 750 27 $gray
$canvas.Bitmap.Save((Join-Path $runOut 'figure7_logistic_oof_confusion.png'), [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $canvas.Bitmap.Dispose()

Get-ChildItem $runOut -File | Get-FileHash -Algorithm SHA256 | Select-Object Path,Hash | Format-Table -AutoSize
