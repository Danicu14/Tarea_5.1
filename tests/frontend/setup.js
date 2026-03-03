/**
 * Setup inicial para los tests de Jest
 */

// Mock de fetch global
global.fetch = jest.fn();

// Mock de console para tests limpios
global.console = {
  ...console,
  error: jest.fn(),
  warn: jest.fn(),
};

// Configuración de entorno DOM
document.body.innerHTML = `
  <div id="app"></div>
  <div id="notification-toast" class="toast">
    <div class="toast-header">
      <strong></strong>
    </div>
    <div class="toast-body"></div>
  </div>
`;

// Reset después de cada test
afterEach(() => {
  jest.clearAllMocks();
  fetch.mockClear();
});
