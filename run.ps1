$ErrorActionPreference = 'Stop'

Push-Location $PSScriptRoot
try {
  if (-not (Test-Path .venv)) {
    Write-Host 'Создаю виртуальное окружение (.venv)'
    python -m venv .venv
  }

  Write-Host 'Активирую .venv'
  .\.venv\Scripts\Activate.ps1

  Write-Host 'Устанавливаю зависимости'
  pip install -r requirements.txt | Out-Host

  Write-Host 'Запускаю бота'
  python -m bot.main
}
finally {
  Pop-Location
}



