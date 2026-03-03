# ============================================
# Script para tests de integración únicamente
# ============================================

Write-Host "🔗 Ejecutando Tests de Integración" -ForegroundColor Cyan
Write-Host "===================================`n" -ForegroundColor Cyan

pytest tests/integration -v -m integration --cov=app --cov-report=html --cov-report=term-missing

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Tests de integración completados" -ForegroundColor Green
} else {
    Write-Host "`n❌ Tests de integración fallaron" -ForegroundColor Red
    exit 1
}
