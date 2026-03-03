# ============================================
# Script para tests E2E únicamente
# ============================================

Write-Host "🌐 Ejecutando Tests End-to-End (Playwright)" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# Iniciar servidor en background si no está corriendo
$serverProcess = Get-Process -Name "uvicorn" -ErrorAction SilentlyContinue
if (-not $serverProcess) {
    Write-Host "🚀 Iniciando servidor en background..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-Command", "uvicorn app.main:app --host 0.0.0.0 --port 8000" -WindowStyle Hidden
    Start-Sleep -Seconds 3
}

# Ejecutar tests E2E
npx playwright test

$exitCode = $LASTEXITCODE

if ($exitCode -eq 0) {
    Write-Host "`n✅ Tests E2E completados" -ForegroundColor Green
    Write-Host "📊 Reporte HTML generado en: playwright-report/index.html" -ForegroundColor Yellow
} else {
    Write-Host "`n❌ Tests E2E fallaron" -ForegroundColor Red
}

exit $exitCode
