param(
    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [string]$OutputPath = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path $ProjectRoot "artifacts\reachy-standalone-windows-x64.zip"
}

$buildRoot = Join-Path $ProjectRoot "Build"
$releaseItems = @(
    ".local_voice_models",
    "MonoBleedingEdge",
    "Reachy controller & simulator_Data",
    "ReachyControlApp",
    "Reachy controller & simulator.exe",
    "UnityCrashHandler64.exe",
    "UnityPlayer.dll"
)

if (-not (Test-Path -LiteralPath $buildRoot)) {
    throw "Build directory was not found at '$buildRoot'."
}

$missingItems = @()
foreach ($item in $releaseItems) {
    $sourcePath = Join-Path $buildRoot $item
    if (-not (Test-Path -LiteralPath $sourcePath)) {
        $missingItems += $sourcePath
    }
}

if ($missingItems.Count -gt 0) {
    throw "Standalone build is incomplete. Missing item(s): $($missingItems -join ', ')"
}

$outputDirectory = Split-Path -Parent $OutputPath
if ([string]::IsNullOrWhiteSpace($outputDirectory)) {
    $outputDirectory = $ProjectRoot
    $OutputPath = Join-Path $outputDirectory $OutputPath
}

New-Item -ItemType Directory -Path $outputDirectory -Force | Out-Null
if (Test-Path -LiteralPath $OutputPath) {
    Remove-Item -LiteralPath $OutputPath -Force
}

$checksumPath = "$OutputPath.sha256"
if (Test-Path -LiteralPath $checksumPath) {
    Remove-Item -LiteralPath $checksumPath -Force
}

$stagingRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("reachy-standalone-release-" + [System.Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $stagingRoot -Force | Out-Null

try {
    foreach ($item in $releaseItems) {
        Copy-Item -LiteralPath (Join-Path $buildRoot $item) -Destination $stagingRoot -Recurse -Force
    }

    $pathsToArchive = Get-ChildItem -LiteralPath $stagingRoot -Force | ForEach-Object { $_.FullName }
    if ($pathsToArchive.Count -eq 0) {
        throw "Nothing was staged for the standalone release archive."
    }

    Compress-Archive -LiteralPath $pathsToArchive -DestinationPath $OutputPath -CompressionLevel Optimal

    $hash = Get-FileHash -LiteralPath $OutputPath -Algorithm SHA256
    $checksumLine = "{0} *{1}" -f $hash.Hash.ToLowerInvariant(), (Split-Path -Leaf $OutputPath)
    Set-Content -LiteralPath $checksumPath -Value $checksumLine -Encoding ascii

    $archiveSizeMb = [math]::Round((Get-Item -LiteralPath $OutputPath).Length / 1MB, 2)
    Write-Host "Created release archive at '$OutputPath' ($archiveSizeMb MB)."
    Write-Host "Wrote SHA256 checksum to '$checksumPath'."
}
finally {
    if (Test-Path -LiteralPath $stagingRoot) {
        Remove-Item -LiteralPath $stagingRoot -Recurse -Force
    }
}
