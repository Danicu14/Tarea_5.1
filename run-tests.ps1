# ============================================
# Script para ejecutar todos los tests
# Tarea 5.1 - Testing Automatizado
# ============================================

Write-Host "🧪 Ejecutando batería completa de tests" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Variables de control
$ErrorActionPreference = "Continue"
$allTestsPassed = $true

# ============================================
# 1. Tests Unitarios (pytest)
# ============================================
Write-Host "📦 1/4 - Tests Unitarios (Pytest)" -ForegroundColor Yellow
Write-Host "-----------------------------------`n" -ForegroundColor Yellow

pytest tests/unit -v -m unit
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Tests unitarios fallaron`n" -ForegroundColor Red
    $allTestsPassed = $false
} else {
    Write-Host "✅ Tests unitarios pasaron`n" -ForegroundColor Green
}

# ============================================
# 2. Tests de Integración (pytest)
# ============================================
Write-Host "🔗 2/4 - Tests de Integración (Pytest)" -ForegroundColor Yellow
Write-Host "----------------------------------------`n" -ForegroundColor Yellow

pytest tests/integration -v -m integration
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Tests de integración fallaron`n" -ForegroundColor Red
    $allTestsPassed = $false
} else {
    Write-Host "✅ Tests de integración pasaron`n" -ForegroundColor Green
}

# ============================================
# 3. Tests de Frontend (Jest)
# ============================================
Write-Host "🎨 3/4 - Tests de Frontend (Jest)" -ForegroundColor Yellow
Write-Host "-----------------------------------`n" -ForegroundColor Yellow

npm test -- --passWithNoTests
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Tests de frontend fallaron`n" -ForegroundColor Red
    $allTestsPassed = $false
} else {
    Write-Host "✅ Tests de frontend pasaron`n" -ForegroundColor Green
}

# ============================================
# 4. Tests E2E (Playwright)
# ============================================
Write-Host "🌐 4/4 - Tests End-to-End (Playwright)" -ForegroundColor Yellow
Write-Host "----------------------------------------`n" -ForegroundColor Yellow

npx playwright test
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Tests E2E fallaron`n" -ForegroundColor Red
    $allTestsPassed = $false
} else {
    Write-Host "✅ Tests E2E pasaron`n" -ForegroundColor Green
}

# ============================================
# Resumen Final
# ============================================
Write-Host "`n========================================" -ForegroundColor Cyan
if ($allTestsPassed) {
    Write-Host "✅ TODOS LOS TESTS PASARON EXITOSAMENTE" -ForegroundColor Green
    exit 0
} else {
    Write-Host "❌ ALGUNOS TESTS FALLARON" -ForegroundColor Red
    exit 1
}
