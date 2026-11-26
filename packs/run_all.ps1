# Run all reproduction packs (Windows / PowerShell)
#   .\run_all.ps1                run all
#   .\run_all.ps1 p1_uibc_core   run one
param([string]$Only = "")
$ErrorActionPreference = "Continue"
$root = $PSScriptRoot

$python = $env:PYTHON
if (-not $python) { $python = "python" }

$packs = @("p1_uibc_core", "p2_uibc_bench", "p3_lgd_eval", "p4_aitb_bench", "p5_synomosai_mcp")
if ($Only) { $packs = @($Only) }

$failed = 0
foreach ($p in $packs) {
    $dir = Join-Path $root $p
    $exe = $python
    $venv = Join-Path $dir ".venv\Scripts\python.exe"
    if ($p -eq "p1_uibc_core" -and (Test-Path $venv)) { $exe = $venv }
    Write-Host "==> $p"
    Push-Location $dir
    & $exe -X utf8 verify.py
    $rc = $LASTEXITCODE
    Pop-Location
    $res = Join-Path $dir "RESULT.json"
    if (Test-Path $res) {
        $j = Get-Content $res -Raw | ConvertFrom-Json
        Write-Host ("    passed={0} failed={1} pin={2} -> {3}s" -f $j.passed, $j.failed, $j.pin, $j.seconds_total)
    }
    if ($rc -ne 0) { $failed++ }
}
if ($failed -gt 0) { Write-Host "FAILED: $failed pack(s)"; exit 1 }
Write-Host "ALL PACKS PASS"
