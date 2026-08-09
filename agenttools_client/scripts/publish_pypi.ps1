# Publish agenttools-client to PyPI (run from repo: agenttools_client/)
# Prerequisites: PyPI account + API token at https://pypi.org/manage/account/token/
#
#   $env:TWINE_USERNAME = "__token__"
#   $env:TWINE_PASSWORD = "pypi-AgEIcHlwaS5vcmcC..."   # scope: entire account or project
#   .\scripts\publish_pypi.ps1

$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

if (-not $env:TWINE_PASSWORD) {
    Write-Host "Set TWINE_USERNAME=__token__ and TWINE_PASSWORD=pypi-... first" -ForegroundColor Red
    exit 1
}

if (-not $env:TWINE_USERNAME) {
    $env:TWINE_USERNAME = "__token__"
}

pip install -q build twine
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
python -m build
python -m twine check dist/*
python -m twine upload dist/*
Write-Host "Done. Test: pip install agenttools-client" -ForegroundColor Green
