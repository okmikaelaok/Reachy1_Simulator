param(
    [string]$Python = "python",
    [string]$Config = "local_voice_agent_sidecar_config.json",
    [ValidateSet("debug", "info", "warning", "error")]
    [string]$LogLevel = "info"
)

function Add-ExistingPathEntry {
    param(
        [System.Collections.Generic.List[string]]$Entries,
        [string]$Candidate
    )

    if ($null -eq $Entries -or [string]::IsNullOrWhiteSpace($Candidate) -or -not (Test-Path $Candidate)) {
        return
    }

    if (-not $Entries.Contains($Candidate)) {
        $Entries.Add($Candidate)
    }
}

function Get-PortablePythonModuleSearchPaths {
    param([string]$SitePackages)

    $entries = New-Object 'System.Collections.Generic.List[string]'
    Add-ExistingPathEntry -Entries $entries -Candidate $SitePackages
    if (-not (Test-Path $SitePackages)) {
        return $entries
    }

    Get-ChildItem -Path $SitePackages -Filter *.pth -File -ErrorAction SilentlyContinue | ForEach-Object {
        Get-Content $_.FullName | ForEach-Object {
            $trimmed = $_.Trim()
            if (-not [string]::IsNullOrWhiteSpace($trimmed) -and
                -not $trimmed.StartsWith("#") -and
                -not $trimmed.StartsWith("import", [System.StringComparison]::OrdinalIgnoreCase)) {
                $candidate = if ([System.IO.Path]::IsPathRooted($trimmed)) {
                    $trimmed
                } else {
                    Join-Path $SitePackages ($trimmed -replace "[\\/]", [System.IO.Path]::DirectorySeparatorChar)
                }

                Add-ExistingPathEntry -Entries $entries -Candidate $candidate
            }
        }
    }

    Add-ExistingPathEntry -Entries $entries -Candidate (Join-Path $SitePackages "pywin32_system32")
    return $entries
}

function Add-PortablePythonNativeLibraryDirectories {
    param(
        [System.Collections.Generic.List[string]]$Entries,
        [string]$SitePackages
    )

    if ($null -eq $Entries -or -not (Test-Path $SitePackages)) {
        return
    }

    Get-ChildItem -Path $SitePackages -Directory -Filter *.libs -ErrorAction SilentlyContinue | ForEach-Object {
        Add-ExistingPathEntry -Entries $Entries -Candidate $_.FullName
    }

    Get-ChildItem -Path $SitePackages -Directory -ErrorAction SilentlyContinue | ForEach-Object {
        $directory = $_.FullName
        $hasNativeFiles =
            @(Get-ChildItem -Path $directory -File -Filter *.dll -ErrorAction SilentlyContinue).Count -gt 0 -or
            @(Get-ChildItem -Path $directory -File -Filter *.pyd -ErrorAction SilentlyContinue).Count -gt 0
        if ($hasNativeFiles) {
            Add-ExistingPathEntry -Entries $Entries -Candidate $directory
        }
    }
}

function Test-IsPortablePythonRuntime {
    param([string]$PythonPath)

    if ([string]::IsNullOrWhiteSpace($PythonPath)) {
        return $false
    }

    return $PythonPath.Replace("/", "\").EndsWith(
        "\PythonRuntime\python.exe",
        [System.StringComparison]::OrdinalIgnoreCase)
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$scriptPath = Join-Path $scriptDir "local_voice_agent_sidecar.py"
$configPath = if ([System.IO.Path]::IsPathRooted($Config)) { $Config } else { Join-Path $scriptDir $Config }
$portablePython = Join-Path $scriptDir "PythonRuntime\\python.exe"
$bundledPython = Join-Path $scriptDir ".venv\\Scripts\\python.exe"
$pythonExe = $Python
if ($pythonExe -eq "python" -and (Test-Path $bundledPython)) {
    if (Test-Path $portablePython) {
        $pythonExe = $portablePython
    } else {
        $pythonExe = $bundledPython
    }
}

if ($pythonExe -eq "python" -and (Test-Path $portablePython)) {
    $pythonExe = $portablePython
}

if (Test-IsPortablePythonRuntime -PythonPath $pythonExe) {
    $runtimeHome = Split-Path -Parent $pythonExe
    $venvRoot = Join-Path $scriptDir ".venv"
    $sitePackages = Join-Path $venvRoot "Lib\\site-packages"
    $pythonPathEntries = Get-PortablePythonModuleSearchPaths -SitePackages $sitePackages
    $pathEntries = New-Object 'System.Collections.Generic.List[string]'

    $env:PYTHONHOME = $runtimeHome
    $env:PYTHONUTF8 = "1"
    $env:PYTHONIOENCODING = "utf-8"

    if (Test-Path $venvRoot) {
        $env:VIRTUAL_ENV = $venvRoot
    }

    if ($pythonPathEntries.Count -gt 0) {
        $env:PYTHONPATH = [string]::Join([System.IO.Path]::PathSeparator, $pythonPathEntries)
    }

    Add-ExistingPathEntry -Entries $pathEntries -Candidate $runtimeHome
    Add-ExistingPathEntry -Entries $pathEntries -Candidate (Join-Path $runtimeHome "DLLs")
    foreach ($entry in $pythonPathEntries) {
        Add-ExistingPathEntry -Entries $pathEntries -Candidate $entry
    }

    Add-PortablePythonNativeLibraryDirectories -Entries $pathEntries -SitePackages $sitePackages

    if (-not [string]::IsNullOrWhiteSpace($env:PATH)) {
        $pathEntries.Add($env:PATH)
    }

    if ($pathEntries.Count -gt 0) {
        $env:PATH = [string]::Join([System.IO.Path]::PathSeparator, $pathEntries)
    }
}

if ($pythonExe -eq "python" -and (Test-Path $bundledPython)) {
    $pythonExe = $bundledPython
}

& $pythonExe $scriptPath --config $configPath --log-level $LogLevel
