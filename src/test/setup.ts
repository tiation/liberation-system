/**
 * 🧪 Liberation System Test Setup
 * Enterprise-grade testing configuration with dark neon theme
 */

import '@testing-library/jest-dom';
import { TextEncoder, TextDecoder } from 'util';

// Global polyfills for Node.js environment
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock window.scrollTo
global.scrollTo = jest.fn();

// Mock console methods for cleaner test output
const originalError = console.error;
console.error = (...args) => {
  // Suppress specific warnings in tests
  if (
    typeof args[0] === 'string' &&
    args[0].includes('Warning: ReactDOM.render is no longer supported')
  ) {
    return;
  }
  originalError.call(console, ...args);
};

// Custom test utilities
export const testUtils = {
  // Mock user for testing
  mockUser: {
    id: 'test-user-001',
    name: 'Test User',
    email: 'test@liberation.system',
    role: 'admin',
    permissions: ['read', 'write', 'admin']
  },
  
  // Mock system data
  mockSystemData: {
    totalHumans: 1000,
    totalResources: 50000,
    distributionRate: 0.85,
    systemHealth: 'optimal'
  },
  
  // Dark neon theme colors for testing
  themeColors: {
    primary: '#00ffff',
    secondary: '#ff00ff',
    accent: '#ffff00',
    background: '#000000',
    surface: '#111111'
  }
};

// Enhanced expect matchers
expect.extend({
  toHaveNeonGlow(received) {
    const pass = received.style.boxShadow.includes('0 0 10px');
    if (pass) {
      return {
        message: () => `expected ${received} not to have neon glow`,
        pass: true,
      };
    } else {
      return {
        message: () => `expected ${received} to have neon glow`,
        pass: false,
      };
    }
  },
  
  toHaveDarkTheme(received) {
    const backgroundColor = getComputedStyle(received).backgroundColor;
    const isDark = backgroundColor.includes('rgb(0, 0, 0)') || 
                   backgroundColor.includes('rgb(17, 17, 17)');
    
    if (isDark) {
      return {
        message: () => `expected ${received} not to have dark theme`,
        pass: true,
      };
    } else {
      return {
        message: () => `expected ${received} to have dark theme`,
        pass: false,
      };
    }
  }
});

// Global test configuration
jest.setTimeout(10000);

// Mock fetch globally
global.fetch = jest.fn();

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Mock sessionStorage
const sessionStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.sessionStorage = sessionStorageMock;

// Clear all mocks before each test
beforeEach(() => {
  jest.clearAllMocks();
  localStorage.clear();
  sessionStorage.clear();
});

// Global cleanup after each test
afterEach(() => {
  jest.restoreAllMocks();
});

console.log('🧪 Liberation System Test Environment Initialized');
console.log('   ✅ Dark neon theme support enabled');
console.log('   ✅ Enterprise-grade testing utilities loaded');
console.log('   ✅ Custom matchers registered');
