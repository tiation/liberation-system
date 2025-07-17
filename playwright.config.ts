import { defineConfig, devices } from '@playwright/test';

/**
 * 🎭 Liberation System E2E Test Configuration
 * Enterprise-grade end-to-end testing with dark neon theme
 */

export default defineConfig({
  testDir: './tests/e2e',
  
  // Run tests in files in parallel
  fullyParallel: true,
  
  // Fail the build on CI if you accidentally left test.only in the source code
  forbidOnly: !!process.env.CI,
  
  // Retry on CI only
  retries: process.env.CI ? 2 : 0,
  
  // Opt out of parallel tests on CI
  workers: process.env.CI ? 1 : undefined,
  
  // Reporter to use
  reporter: [
    ['html', { outputFolder: 'test-results/e2e-report' }],
    ['json', { outputFile: 'test-results/e2e-results.json' }],
    ['junit', { outputFile: 'test-results/e2e-junit.xml' }],
    ['line']
  ],
  
  // Shared settings for all the projects below
  use: {
    // Base URL to use in actions like `await page.goto('/')`
    baseURL: 'http://localhost:3000',
    
    // Dark neon theme for testing
    colorScheme: 'dark',
    
    // Collect trace when retrying the failed test
    trace: 'on-first-retry',
    
    // Take screenshot on failure
    screenshot: 'only-on-failure',
    
    // Record video on failure
    video: 'retain-on-failure',
    
    // Global test timeout
    actionTimeout: 10000,
    
    // Navigation timeout
    navigationTimeout: 30000,
    
    // Ignore HTTPS errors
    ignoreHTTPSErrors: true,
    
    // Additional context options
    viewport: { width: 1280, height: 720 },
    
    // User agent
    userAgent: 'Liberation-System-E2E-Tests',
  },
  
  // Configure projects for major browsers
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    
    // Test against mobile viewports
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
    
    // Test against branded browsers
    {
      name: 'Microsoft Edge',
      use: { ...devices['Desktop Edge'], channel: 'msedge' },
    },
    
    {
      name: 'Google Chrome',
      use: { ...devices['Desktop Chrome'], channel: 'chrome' },
    },
  ],
  
  // Run your local dev server before starting the tests
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
  
  // Global setup and teardown
  globalSetup: require.resolve('./tests/e2e/global-setup.ts'),
  globalTeardown: require.resolve('./tests/e2e/global-teardown.ts'),
  
  // Test timeout
  timeout: 30 * 1000,
  
  // Maximum failures
  maxFailures: process.env.CI ? 10 : undefined,
  
  // Output directory for artifacts
  outputDir: 'test-results/e2e-artifacts',
  
  // Expect settings
  expect: {
    // Maximum time expect() should wait for the condition to be met
    timeout: 5000,
    
    // Take screenshot on expect failure
    toHaveScreenshot: {
      mode: 'only-on-failure',
      animations: 'disabled',
      caret: 'hide',
    },
    
    // Visual comparisons
    toMatchSnapshot: {
      threshold: 0.2,
      mode: 'only-on-failure',
    },
  },
});
