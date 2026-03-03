import { test, expect } from '@playwright/test';

/**
 * Tests E2E - Smoke Tests
 * Verifican que la aplicación funciona end-to-end
 */

test.describe('Smoke Tests - Aplicación Básica', () => {
  
  test('debe cargar la página principal', async ({ page }) => {
    await page.goto('/');
    
    // Verificar que el título está presente
    await expect(page).toHaveTitle(/Dashboard/);
  });

  test('debe mostrar el navbar', async ({ page }) => {
    await page.goto('/');
    
    // Verificar elementos del navbar
    const navbar = page.locator('nav.navbar');
    await expect(navbar).toBeVisible();
    
    const brand = page.locator('.navbar-brand');
    await expect(brand).toContainText('FastAPI Dashboard');
  });

  test('debe cargar estilos CSS', async ({ page }) => {
    await page.goto('/');
    
    // Verificar que Bootstrap está cargado
    const body = page.locator('body');
    await expect(body).toBeVisible();
  });
});

test.describe('Tests E2E - API Health Check', () => {
  
  test('debe mostrar el estado de salud de la API', async ({ page }) => {
    await page.goto('/');
    
    // Esperar a que la página cargue
    await page.waitForLoadState('networkidle');
    
    // Verificar que hay contenido
    const content = await page.content();
    expect(content).toBeTruthy();
  });

  test('endpoint /health debe responder', async ({ request }) => {
    const response = await request.get('/health');
    
    expect(response.ok()).toBeTruthy();
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data.status).toBe('healthy');
  });
});

test.describe('Tests E2E - API Info', () => {
  
  test('endpoint /api/info debe retornar información', async ({ request }) => {
    const response = await request.get('/api/info');
    
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data).toHaveProperty('name');
    expect(data).toHaveProperty('version');
    expect(data).toHaveProperty('environment');
  });
});

test.describe('Tests E2E - Items', () => {
  
  test('debe obtener lista de items', async ({ request }) => {
    const response = await request.get('/api/items');
    
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data).toHaveProperty('items');
    expect(Array.isArray(data.items)).toBeTruthy();
  });

  test('debe obtener un item específico', async ({ request }) => {
    const response = await request.get('/api/items/1');
    
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data).toHaveProperty('id');
    expect(data.id).toBe(1);
  });
});

test.describe('Tests E2E - Navegación', () => {
  
  test('debe navegar a diferentes secciones', async ({ page }) => {
    await page.goto('/');
    
    // Verificar que hay enlaces de navegación
    const navLinks = page.locator('.nav-link');
    const count = await navLinks.count();
    
    expect(count).toBeGreaterThan(0);
  });
});

test.describe('Tests E2E - Responsividad', () => {
  
  test('debe ser responsive en móvil', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    
    const navbar = page.locator('nav.navbar');
    await expect(navbar).toBeVisible();
  });

  test('debe ser responsive en tablet', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/');
    
    const content = page.locator('body');
    await expect(content).toBeVisible();
  });
});
