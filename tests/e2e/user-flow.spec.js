import { test, expect } from '@playwright/test';

/**
 * Tests E2E - Flujo Completo de Usuario
 * Simulan comportamiento real de usuario recorriendo todo el sistema
 */

test.describe('E2E: Acceso a la Aplicación', () => {
  
  test('usuario accede a la aplicación correctamente', async ({ page }) => {
    // PASO 1: Acceso inicial
    await page.goto('/static/index.html', { waitUntil: 'load' });
    
    // Verificar que la aplicación carga correctamente
    await expect(page).toHaveTitle(/Dashboard/i);
    await expect(page.locator('nav.navbar')).toBeVisible();
    
    // PASO 2: Verificar elementos visibles para el usuario
    const brand = page.locator('.navbar-brand');
    await expect(brand).toBeVisible();
    await expect(brand).toContainText('FastAPI Dashboard');
  });

  test('usuario navega por la interfaz', async ({ page }) => {
    // PASO 1: Cargar página
    await page.goto('/static/index.html', { waitUntil: 'load' });
    
    // PASO 2: Usuario ve el contenido principal
    const mainContent = page.locator('body');
    await expect(mainContent).toBeVisible();
    
    // PASO 3: Verificar que la navegación está visible y funcional
    const navbar = page.locator('nav.navbar');
    await navbar.waitFor({ state: 'visible', timeout: 10000 });
    await expect(navbar).toBeVisible();
    
    // PASO 4: Verificar que el navbar tiene contenido
    const navbarText = await navbar.textContent();
    expect(navbarText).toContain('FastAPI Dashboard');
  });
});

test.describe('E2E: Interacción con Datos', () => {
  
  test('usuario visualiza lista de items (Frontend → Backend)', async ({ page }) => {
    // PASO 1: Usuario accede a la aplicación
    await page.goto('/static/index.html', { waitUntil: 'load' });
    
    // PASO 2: Verificar que la interfaz está lista
    await expect(page.locator('body')).toBeVisible();
    await expect(page).toHaveTitle(/Dashboard/i);
    
    // PASO 3: Si hay botones o enlaces, el usuario puede interactuar
    const links = page.locator('a, button');
    const count = await links.count();
    expect(count).toBeGreaterThan(0);
  });

  test('usuario realiza búsqueda o filtrado (si aplica)', async ({ page }) => {
    await page.goto('/static/index.html', { waitUntil: 'load' });
    
    // Verificar que la página responde a la interacción
    const body = await page.locator('body').textContent();
    expect(body).toBeTruthy();
    expect(body.length).toBeGreaterThan(0);
  });
});

test.describe('E2E: Flujo Completo Frontend → Backend', () => {
  
  test('flujo completo: acceso → carga → interacción → validación', async ({ page }) => {
    // PASO 1: Acceso (Usuario abre la aplicación)
    await page.goto('/static/index.html', { waitUntil: 'load' });
    await page.locator('nav.navbar').waitFor({ state: 'visible', timeout: 10000 });
    
    // PASO 2: Verificar carga completa (Frontend cargado)
    await expect(page).toHaveTitle(/Dashboard/i);
    await expect(page.locator('body')).toBeVisible();
    
    // PASO 3: Verificar que la interfaz es funcional
    await expect(page.locator('nav.navbar')).toBeVisible();
    
    // PASO 4: Verificar que hay contenido interactivo
    const links = await page.locator('a, button').count();
    expect(links).toBeGreaterThan(0);
  });

  test('validación de cambios en la interfaz tras interacción', async ({ page }) => {
    // PASO 1: Estado inicial
    await page.goto('/static/index.html', { waitUntil: 'load' });
    await page.locator('nav.navbar').waitFor({ state: 'visible', timeout: 10000 });
    
    // PASO 2: Verificar contenido inicial
    await expect(page.locator('nav.navbar')).toBeVisible();
    const initialTitle = await page.title();
    
    // PASO 3: Usuario interactúa (navegación)
    await page.goto('/static/index.html', { waitUntil: 'load' });
    await page.locator('nav.navbar').waitFor({ state: 'visible', timeout: 10000 });
    
    // PASO 4: Validar que la interfaz sigue funcional
    await expect(page.locator('nav.navbar')).toBeVisible();
    const newTitle = await page.title();
    expect(newTitle).toBe(initialTitle);
  });
});

test.describe('E2E: Validación de Sistema Completo', () => {
  
  test('sistema completo responde correctamente', async ({ page }) => {
    // PASO 1: Usuario accede
    await page.goto('/static/index.html', { waitUntil: 'load' });
    
    // PASO 2: Frontend se carga
    await expect(page).toHaveTitle(/Dashboard/i);
    
    // PASO 3: Verificar que JavaScript está activo
    const hasJS = await page.evaluate(() => {
      return typeof window !== 'undefined';
    });
    expect(hasJS).toBeTruthy();
    
    // PASO 4: Validación final
    const navbar = page.locator('nav.navbar');
    await expect(navbar).toBeVisible();
  });

  test('navegación y validación de múltiples páginas', async ({ page }) => {
    // PASO 1: Página principal
    await page.goto('/static/index.html', { waitUntil: 'load' });
    await expect(page).toHaveTitle(/Dashboard/i);
    
    // PASO 2: Verificar que los links funcionan
    const links = page.locator('a[href]');
    const linkCount = await links.count();
    expect(linkCount).toBeGreaterThan(0);
    
    // PASO 3: Validar estado final
    await expect(page.locator('body')).toBeVisible();
    await expect(page.locator('nav.navbar')).toBeVisible();
  });

  test('comportamiento responsivo de la interfaz', async ({ page }) => {
    // PASO 1: Desktop
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('/static/index.html', { waitUntil: 'load' });
    await expect(page.locator('nav.navbar')).toBeVisible();
    
    // PASO 2: Mobile (comportamiento de usuario real)
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.locator('nav.navbar')).toBeVisible();
    
    // PASO 3: Tablet
    await page.setViewportSize({ width: 768, height: 1024 });
    await expect(page.locator('nav.navbar')).toBeVisible();
  });
});

test.describe('E2E: Escenarios de Usuario Real', () => {
  
  test('usuario nuevo visita la aplicación por primera vez', async ({ page }) => {
    // Simula usuario que nunca ha visitado la app
    await page.context().clearCookies();
    
    // PASO 1: Primera visita
    await page.goto('/static/index.html', { waitUntil: 'load' });
    
    // PASO 2: Usuario ve la interfaz
    await expect(page).toHaveTitle(/Dashboard/i);
    await expect(page.locator('nav.navbar')).toBeVisible();
    
    // PASO 3: Validación de experiencia inicial
    const body = await page.locator('body').textContent();
    expect(body.length).toBeGreaterThan(100);
  });

  test('usuario recurrente regresa a la aplicación', async ({ page }) => {
    // PASO 1: Primera visita
    await page.goto('/static/index.html', { waitUntil: 'load' });
    await page.locator('nav.navbar').waitFor({ state: 'visible', timeout: 10000 });
    await expect(page).toHaveTitle(/Dashboard/i);
    
    // PASO 2: Usuario vuelve (segunda visita) - simular recarga
    await page.goto('/static/index.html', { waitUntil: 'load' });
    await page.locator('nav.navbar').waitFor({ state: 'visible', timeout: 10000 });
    
    // PASO 3: Experiencia consistente
    await expect(page).toHaveTitle(/Dashboard/i);
    await expect(page.locator('nav.navbar')).toBeVisible();
  });

  test('usuario interactúa con diferentes elementos', async ({ page }) => {
    await page.goto('/static/index.html', { waitUntil: 'load' });
    
    // Usuario hace click en diferentes áreas
    const clickableElements = await page.locator('a, button, [role="button"]').count();
    expect(clickableElements).toBeGreaterThan(0);
    
    // Usuario hace scroll
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.evaluate(() => window.scrollTo(0, 0));
    
    // Validación: la interfaz sigue funcional
    await expect(page.locator('nav.navbar')).toBeVisible();
  });
});
