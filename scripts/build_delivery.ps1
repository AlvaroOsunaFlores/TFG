param(
    [string]$DeliveryDate = "2026_03_13",
    [string]$PreviousDelivery = "entrega_tutoria_2026_03_02"
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$proyectosPrincipales = Split-Path -Parent $repoRoot
$workspaceRoot = Split-Path -Parent $proyectosPrincipales
$historicoRoot = Join-Path $workspaceRoot "versiones_historicas"
$currentDeliveryPath = Join-Path $proyectosPrincipales $PreviousDelivery
$historicDeliveryPath = Join-Path $historicoRoot $PreviousDelivery
$newDeliveryName = "entrega_tutoria_$DeliveryDate"
$newDeliveryPath = Join-Path $proyectosPrincipales $newDeliveryName
$zipPath = Join-Path (Join-Path $workspaceRoot "copias_comprimidas") ("ENTREGA_TUTORIA_TFG_$DeliveryDate.zip")

if ((Test-Path $currentDeliveryPath) -and -not (Test-Path $historicDeliveryPath)) {
    Move-Item -Path $currentDeliveryPath -Destination $historicDeliveryPath
}

if (Test-Path $newDeliveryPath) {
    Remove-Item -Path $newDeliveryPath -Recurse -Force
}

New-Item -ItemType Directory -Force -Path $newDeliveryPath | Out-Null

$robocopyArgs = @(
    $repoRoot,
    $newDeliveryPath,
    "/E",
    "/XD", ".git", ".venv", ".idea", ".pytest_cache", "dashboard-react\\node_modules", "dashboard-react\\dist", "session",
    "/XF", ".env", "*.pyc", "docs\\MEMORIA_TFG_ETSII_APA7_V2.md", "docs\\MEMORIA_TFG_ETSII_APA7_V2.docx"
)

& robocopy @robocopyArgs | Out-Null

Get-ChildItem -Path $newDeliveryPath -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force

if (Test-Path $zipPath) {
    Remove-Item -Path $zipPath -Force
}

Compress-Archive -Path (Join-Path $newDeliveryPath "*") -DestinationPath $zipPath -Force

Write-Output "OK -> $newDeliveryPath"
Write-Output "OK -> $zipPath"
