/** @type {import('jest').Config} */
module.exports = {
  // Entorno de ejecución
  testEnvironment: 'jsdom',
  
  // Directorio de tests
  roots: ['<rootDir>/tests/frontend'],
  
  // Patrones de archivos de test
  testMatch: [
    '**/__tests__/**/*.js',
    '**/?(*.)+(spec|test).js'
  ],
  
  // Cobertura de código
  collectCoverageFrom: [
    'static/js/**/*.js',
    '!static/js/**/*.min.js',
    '!**/node_modules/**',
    '!**/vendor/**'
  ],
  
  // Configuración de coverage
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'html', 'lcov'],
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70
    }
  },
  
  // Configuración de módulos
  moduleDirectories: ['node_modules', 'static/js'],
  
  // Setup
  setupFilesAfterEnv: ['<rootDir>/tests/frontend/setup.js'],
  
  // Transformaciones
  transform: {},
  
  // Verbose output
  verbose: true
};
