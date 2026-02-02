param(
    [ValidateSet("start", "stop", "restart", "status")]
    [string]$Action = "status",
    [string]$BindHost = "127.0.0.1",
    [int]$Port = 8000,
    [switch]$Reload
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$PythonExe = Join-Path $ProjectRoot ".venv\\Scripts\\python.exe"
$PidFile = Join-Path $ProjectRoot ("tmp_server_{0}.pid.txt" -f $Port)
$StdoutLog = Join-Path $ProjectRoot ("tmp_server_{0}.stdout.log" -f $Port)
$StderrLog = Join-Path $ProjectRoot ("tmp_server_{0}.stderr.log" -f $Port)

function Get-PidByPort {
    param([int]$LocalPort)

    try {
        $conn = Get-NetTCPConnection -LocalPort $LocalPort -State Listen -ErrorAction Stop |
            Select-Object -First 1
        if ($conn) {
            return [int]$conn.OwningProcess
        }
    } catch {
        $line = netstat -ano | Select-String ":$LocalPort\s+.*LISTENING"
        if ($line) {
            $parts = ($line.Line -replace "\s+", " ").Trim().Split(" ")
            return [int]$parts[-1]
        }
    }

    return $null
}

function Test-ProcessAlive {
    param([int]$ProcessId)
    try {
        Get-Process -Id $ProcessId -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

function Wait-ForHealth {
    param(
        [string]$BaseUrl,
        [int]$TimeoutSec = 20
    )

    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    while ($sw.Elapsed.TotalSeconds -lt $TimeoutSec) {
        try {
            $resp = Invoke-RestMethod -Method Get "$BaseUrl/health" -TimeoutSec 2
            if ($resp.success -eq $true) {
                return $true
            }
        } catch {
            Start-Sleep -Milliseconds 350
        }
    }
    return $false
}

if (-not (Test-Path $PythonExe)) {
    throw "python 실행 파일을 찾을 수 없습니다: $PythonExe"
}

$BaseUrl = "http://$BindHost`:$Port"

switch ($Action) {
    "status" {
        $serverPid = Get-PidByPort -LocalPort $Port
        if ($serverPid -and (Test-ProcessAlive -ProcessId $serverPid)) {
            Write-Host "[status] 실행 중 - PID=$serverPid URL=$BaseUrl" -ForegroundColor Green
            exit 0
        }
        Write-Host "[status] 중지됨 - URL=$BaseUrl" -ForegroundColor Yellow
        exit 1
    }

    "start" {
        $existingPid = Get-PidByPort -LocalPort $Port
        if ($existingPid -and (Test-ProcessAlive -ProcessId $existingPid)) {
            Write-Host "[start] 이미 실행 중입니다 - PID=$existingPid URL=$BaseUrl" -ForegroundColor Yellow
            exit 0
        }

        $args = @("-m", "uvicorn", "app.main:app", "--host", $BindHost, "--port", "$Port")
        if ($Reload.IsPresent) {
            $args += "--reload"
        }

        $proc = Start-Process -FilePath $PythonExe `
            -ArgumentList $args `
            -WorkingDirectory $ProjectRoot `
            -PassThru `
            -RedirectStandardOutput $StdoutLog `
            -RedirectStandardError $StderrLog

        Set-Content -Path $PidFile -Value $proc.Id -Encoding UTF8
        Write-Host "[start] 서버 시작 요청 - PID=$($proc.Id), URL=$BaseUrl" -ForegroundColor Cyan

        if (Wait-ForHealth -BaseUrl $BaseUrl -TimeoutSec 20) {
            Write-Host "[start] health 확인 성공" -ForegroundColor Green
            exit 0
        }

        Write-Host "[start] health 확인 실패, 로그를 확인하세요:" -ForegroundColor Red
        Write-Host "  - $StdoutLog"
        Write-Host "  - $StderrLog"
        exit 2
    }

    "stop" {
        $serverPid = Get-PidByPort -LocalPort $Port
        if (-not $serverPid -and (Test-Path $PidFile)) {
            try {
                $serverPid = [int](Get-Content -Raw $PidFile).Trim()
            } catch {
                $serverPid = $null
            }
        }

        if (-not $serverPid) {
            Write-Host "[stop] 실행 중인 서버를 찾지 못했습니다. URL=$BaseUrl" -ForegroundColor Yellow
            exit 0
        }

        if (Test-ProcessAlive -ProcessId $serverPid) {
            Stop-Process -Id $serverPid -Force
            Write-Host "[stop] 서버 종료 완료 - PID=$serverPid" -ForegroundColor Green
        } else {
            Write-Host "[stop] PID 파일의 프로세스가 이미 종료 상태입니다 - PID=$serverPid" -ForegroundColor Yellow
        }

        if (Test-Path $PidFile) {
            Remove-Item $PidFile -Force
        }
        exit 0
    }

    "restart" {
        & $PSCommandPath -Action stop -BindHost $BindHost -Port $Port
        & $PSCommandPath -Action start -BindHost $BindHost -Port $Port -Reload:$Reload
        exit $LASTEXITCODE
    }
}
