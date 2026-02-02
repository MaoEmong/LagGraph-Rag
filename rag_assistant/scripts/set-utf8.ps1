# PowerShell UTF-8 console settings for readable Korean output.
# Usage: .\scripts\set-utf8.ps1

# Set console code page to UTF-8.
chcp 65001 | Out-Null

# Ensure PowerShell uses UTF-8 for output and external commands.
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[Console]::OutputEncoding = $utf8NoBom
$OutputEncoding = $utf8NoBom

# Python UTF-8 mode for subprocess output.
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'

Write-Host 'UTF-8 output configured for this session.'
