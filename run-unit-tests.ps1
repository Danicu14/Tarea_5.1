# ============================================
# Script para tests unitarios únicamente
# ============================================

Write-Host "🧪 Ejecutando Tests Unitarios" -ForegroundColor Cyan
Write-Host "==============================`n" -ForegroundColor Cyan

pytest tests/unit -v -m unit --cov=app --cov-report=html --cov-report=term-missing

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Tests unitarios completados" -ForegroundColor Green
    Write-Host "📊 Reporte de cobertura generado en: htmlcov/index.html" -ForegroundColor Yellow
} else {
    Write-Host "`n❌ Tests unitarios fallaron" -ForegroundColor Red
    exit 1
}
