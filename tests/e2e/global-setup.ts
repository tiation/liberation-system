import { chromium, FullConfig } from '@playwright/test';

/**
 * 🌐 Global E2E Setup
 * Initialize environment for Liberation System E2E tests
 */

async function globalSetup(config: FullConfig) {
  console.log('🚀 Setting up Liberation System E2E test environment...');
  
  // Launch browser for global setup
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  
  // Check if the app is running
  try {
    await page.goto(config.projects[0].use.baseURL || 'http://localhost:3000');
    console.log('✅ Liberation System application is running');
  } catch (error) {
    console.error('❌ Liberation System application is not running');
    throw error;
  } finally {
    await browser.close();
  }
  
  // Setup test data or authentication if needed
  // This is where you would create test users, seed data, etc.
  
  console.log('✅ E2E test environment ready');
}

export default globalSetup;
