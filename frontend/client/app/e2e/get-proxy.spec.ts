import { test, expect } from '@playwright/test';

test.describe('Get Proxy Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Mock login
    await page.goto('/login');
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'testpassword');

    await page.route('**/auth/login', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: 'test-access-token',
          refresh_token: 'test-refresh-token',
          token_type: 'bearer',
        }),
      });
    });

    await page.route('**/auth/me', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 1,
          username: 'testuser',
          email: 'test@example.com',
          role: 'user',
          is_active: true,
          created_at: new Date().toISOString(),
        }),
      });
    });

    await page.click('button[type="submit"]');
    await page.waitForURL(/\/app\/proxies/);
  });

  test('should get random proxy', async ({ page }) => {
    await page.goto('/app/get-proxy');

    await page.route('**/proxy/random', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 1,
          ip: '192.168.1.1',
          port: 8080,
          protocol: 'http',
          is_working: true,
          fail_count: 0,
          address: '192.168.1.1:8080',
        }),
      });
    });

    await page.click('button:has-text("Random Working")');

    await expect(page.locator('text=192.168.1.1')).toBeVisible();
    await expect(page.locator('text=8080')).toBeVisible();
  });
});

