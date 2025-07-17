import { test, expect } from '@playwright/test';

/**
 * 🎭 Liberation System Dashboard E2E Tests
 * Testing the main dashboard functionality with dark neon theme
 */

test.describe('Liberation System Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to dashboard
    await page.goto('/');
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
  });

  test('should display dashboard with dark neon theme', async ({ page }) => {
    // Check if the page has the expected title
    await expect(page).toHaveTitle(/Liberation System/);
    
    // Check for dark theme elements
    const body = page.locator('body');
    await expect(body).toHaveCSS('background-color', 'rgb(0, 0, 0)');
    
    // Check for neon elements
    const neonElements = page.locator('[class*="neon"]');
    await expect(neonElements.first()).toBeVisible();
  });

  test('should display system metrics', async ({ page }) => {
    // Check for metric cards
    const metricCards = page.locator('[data-testid="metric-card"]');
    await expect(metricCards).toHaveCount(4);
    
    // Check specific metrics
    await expect(page.locator('[data-testid="total-humans"]')).toBeVisible();
    await expect(page.locator('[data-testid="total-resources"]')).toBeVisible();
    await expect(page.locator('[data-testid="distribution-rate"]')).toBeVisible();
    await expect(page.locator('[data-testid="system-health"]')).toBeVisible();
  });

  test('should have working navigation', async ({ page }) => {
    // Test sidebar navigation
    const sidebar = page.locator('[data-testid="sidebar"]');
    await expect(sidebar).toBeVisible();
    
    // Test navigation links
    const dashboardLink = page.locator('[data-testid="nav-dashboard"]');
    await expect(dashboardLink).toBeVisible();
    await dashboardLink.click();
    
    // Verify we're still on dashboard
    await expect(page.locator('[data-testid="dashboard-content"]')).toBeVisible();
  });

  test('should display console output', async ({ page }) => {
    // Check for console output component
    const consoleOutput = page.locator('[data-testid="console-output"]');
    await expect(consoleOutput).toBeVisible();
    
    // Check for dark theme styling
    await expect(consoleOutput).toHaveCSS('background-color', 'rgb(17, 17, 17)');
    
    // Check for neon text
    const neonText = consoleOutput.locator('[class*="neon"]');
    await expect(neonText).toBeVisible();
  });

  test('should have responsive design', async ({ page }) => {
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Check if sidebar is hidden on mobile
    const sidebar = page.locator('[data-testid="sidebar"]');
    await expect(sidebar).toHaveCSS('display', 'none');
    
    // Test tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    
    // Check if layout adapts
    const mainContent = page.locator('[data-testid="main-content"]');
    await expect(mainContent).toBeVisible();
  });

  test('should handle dark mode toggle', async ({ page }) => {
    // Look for theme toggle button
    const themeToggle = page.locator('[data-testid="theme-toggle"]');
    
    if (await themeToggle.isVisible()) {
      await themeToggle.click();
      
      // Verify theme change
      await expect(page.locator('body')).toHaveAttribute('data-theme', 'dark');
    }
  });

  test('should display progress bars with neon effect', async ({ page }) => {
    // Check for progress bars
    const progressBars = page.locator('[data-testid="progress-bar"]');
    await expect(progressBars.first()).toBeVisible();
    
    // Check for neon glow effect
    const progressBar = progressBars.first();
    const boxShadow = await progressBar.evaluate(el => getComputedStyle(el).boxShadow);
    expect(boxShadow).toContain('0px 0px');
  });

  test('should have working neon buttons', async ({ page }) => {
    // Check for neon buttons
    const neonButtons = page.locator('[data-testid="neon-button"]');
    
    if (await neonButtons.count() > 0) {
      const button = neonButtons.first();
      await expect(button).toBeVisible();
      
      // Test hover effect
      await button.hover();
      
      // Test click
      await button.click();
      
      // Verify button functionality
      await expect(button).toBeEnabled();
    }
  });

  test('should load system data', async ({ page }) => {
    // Wait for data to load
    await page.waitForSelector('[data-testid="system-stats"]');
    
    // Check if data is displayed
    const systemStats = page.locator('[data-testid="system-stats"]');
    await expect(systemStats).toBeVisible();
    
    // Check for loading states
    const loadingIndicator = page.locator('[data-testid="loading"]');
    await expect(loadingIndicator).toBeHidden();
  });

  test('should handle errors gracefully', async ({ page }) => {
    // Simulate network error
    await page.route('/api/system-stats', route => route.abort());
    
    // Reload page
    await page.reload();
    
    // Check for error message
    const errorMessage = page.locator('[data-testid="error-message"]');
    await expect(errorMessage).toBeVisible();
    
    // Check error styling
    await expect(errorMessage).toHaveCSS('color', 'rgb(255, 91, 91)');
  });
});
