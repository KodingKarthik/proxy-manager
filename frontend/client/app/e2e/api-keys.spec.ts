import { test, expect } from '@playwright/test';

/**
 * NOTE: These E2E tests require the dev server to be running.
 * 
 * To run these tests:
 * 1. Start dev server: cd frontend && npm run dev
 * 2. Run tests from correct directory: cd frontend/client/app && npx playwright test e2e/api-keys.spec.ts
 * 
 * The playwright.config.ts should auto-start the server, but if it doesn't work, start it manually.
 * 
 * Currently SKIPPED - Backend tests provide comprehensive coverage.
 * Enable these tests for visual/UI validation once dev environment is stable.
 */

// Helper function to setup authenticated session
async function setupAuthenticatedSession(page) {
    // Mock authentication
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

    // Login
    await page.goto('/login');
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'password');
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/app\/proxies/);
}

test.describe('API Keys Management', () => {
    test.beforeEach(async ({ page }) => {
        await setupAuthenticatedSession(page);
    });

    test('displays API Keys page', async ({ page }) => {
        // Mock empty API keys list
        await page.route('**/api-keys', async (route) => {
            if (route.request().method() === 'GET') {
                await route.fulfill({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify([]),
                });
            }
        });

        // Navigate to API Keys page
        await page.click('a[href="/app/api-keys"]');
        await page.waitForURL(/\/app\/api-keys/);

        // Verify page loads
        await expect(page.getByRole('heading', { name: 'API Keys' })).toBeVisible();
        await expect(page.getByText('Manage your API keys for programmatic access')).toBeVisible();
    });

    test('displays empty state when no keys exist', async ({ page }) => {
        await page.route('**/api-keys', async (route) => {
            if (route.request().method() === 'GET') {
                await route.fulfill({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify([]),
                });
            }
        });

        // Navigate via nav link instead of direct URL
        await page.click('a[href="/app/api-keys"]');
        await page.waitForURL(/\/app\/api-keys/);

        await expect(page.getByText("You don't have any API keys yet.")).toBeVisible();
        await expect(page.getByRole('button', { name: 'Create Your First API Key' })).toBeVisible();
    });

    test('creates a new API key', async ({ page }) => {
        let keysData = [];

        await page.route('**/api-keys', async (route) => {
            if (route.request().method() === 'GET') {
                await route.fulfill({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify(keysData),
                });
            } else if (route.request().method() === 'POST') {
                const newKey = {
                    api_key: {
                        id: 1,
                        prefix: 'abc12345',
                        name: 'E2E Test Key',
                        created_at: new Date().toISOString(),
                        expires_at: null,
                        is_active: true,
                    },
                    raw_key: 'abc12345.full_secret_key_for_testing',
                };
                keysData.push(newKey.api_key);
                await route.fulfill({
                    status: 201,
                    contentType: 'application/json',
                    body: JSON.stringify(newKey),
                });
            }
        });

        await page.click('a[href="/app/api-keys"]');
        await page.waitForURL(/\/app\/api-keys/);

        // Click create button
        await page.click('button:has-text("Create API Key")');

        // Verify modal opened
        await expect(page.getByText('Create New API Key')).toBeVisible();

        // Fill form
        await page.fill('input[id="keyName"]', 'E2E Test Key');

        // Submit
        await page.click('button:has-text("Create Key")');

        // Check success modal
        await expect(page.getByText('API Key Created Successfully')).toBeVisible();
        await expect(page.getByText('⚠️ Important')).toBeVisible();
        await expect(page.getByText('This is the only time you will see this API key')).toBeVisible();

        // Key should be visible
        await expect(page.getByText('abc12345.full_secret_key_for_testing')).toBeVisible();

        // Copy button should be present
        await expect(page.getByRole('button', { name: 'Copy' })).toBeVisible();
    });

    test('displays created key in table after closing modal', async ({ page }) => {
        const mockKeys = [
            {
                id: 1,
                prefix: 'abc12345',
                name: 'Table Test Key',
                created_at: new Date().toISOString(),
                expires_at: null,
                is_active: true,
            },
        ];

        await page.route('**/api-keys', async (route) => {
            if (route.request().method() === 'GET') {
                await route.fulfill({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify(mockKeys),
                });
            } else if (route.request().method() === 'POST') {
                await route.fulfill({
                    status: 201,
                    contentType: 'application/json',
                    body: JSON.stringify({
                        api_key: mockKeys[0],
                        raw_key: 'abc12345.secret',
                    }),
                });
            }
        });

        await page.click('a[href="/app/api-keys"]');
        await page.waitForURL(/\/app\/api-keys/);

        // Create key
        await page.click('button:has-text("Create API Key")');
        await page.fill('input[id="keyName"]', 'Table Test Key');
        await page.click('button:has-text("Create Key")');

        // Close success modal
        await page.click('button:has-text("I\'ve Saved My Key")');

        // Verify key appears in table
        await expect(page.getByText('Table Test Key')).toBeVisible();
        await expect(page.getByText('Active')).toBeVisible();
        await expect(page.getByText('abc12345...')).toBeVisible();
    });

    test('displays multiple API keys in table', async ({ page }) => {
        const mockKeys = [
            {
                id: 1,
                prefix: 'abc12345',
                name: 'Production Key',
                created_at: '2024-01-01T00:00:00Z',
                expires_at: null,
                is_active: true,
            },
            {
                id: 2,
                prefix: 'def67890',
                name: 'Development Key',
                created_at: '2024-01-02T00:00:00Z',
                expires_at: '2024-12-31T23:59:59Z',
                is_active: true,
            },
            {
                id: 3,
                prefix: 'ghi11111',
                name: 'Expired Key',
                created_at: '2023-01-01T00:00:00Z',
                expires_at: '2023-12-31T23:59:59Z',
                is_active: true,
            },
        ];

        await page.route('**/api-keys', async (route) => {
            if (route.request().method() === 'GET') {
                await route.fulfill({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify(mockKeys),
                });
            }
        });

        await page.click('a[href="/app/api-keys"]');
        await page.waitForURL(/\/app\/api-keys/);

        // Verify all keys are displayed
        await expect(page.getByText('Production Key')).toBeVisible();
        await expect(page.getByText('Development Key')).toBeVisible();
        await expect(page.getByText('Expired Key')).toBeVisible();

        // Verify prefixes
        await expect(page.getByText('abc12345...')).toBeVisible();
        await expect(page.getByText('def67890...')).toBeVisible();

        // Verify statuses
        const activeStatuses = page.getByText('Active');
        await expect(activeStatuses.first()).toBeVisible();

        // Expired key should show as expired
        await expect(page.getByText('Expired').first()).toBeVisible();
    });

    test('revokes an API key with confirmation', async ({ page }) => {
        let keysData = [
            {
                id: 1,
                prefix: 'abc12345',
                name: 'Key to Revoke',
                created_at: new Date().toISOString(),
                expires_at: null,
                is_active: true,
            },
        ];

        await page.route('**/api-keys', async (route) => {
            if (route.request().method() === 'GET') {
                await route.fulfill({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify(keysData),
                });
            }
        });

        await page.route('**/api-keys/1', async (route) => {
            if (route.request().method() === 'DELETE') {
                keysData = []; // Remove the key
                await route.fulfill({
                    status: 204,
                });
            }
        });

        await page.click('a[href="/app/api-keys"]');
        await page.waitForURL(/\/app\/api-keys/);

        // Verify key is present
        await expect(page.getByText('Key to Revoke')).toBeVisible();

        // Set up dialog handler for confirmation
        page.once('dialog', (dialog) => {
            expect(dialog.message()).toContain('Key to Revoke');
            expect(dialog.message()).toContain('cannot be undone');
            dialog.accept();
        });

        // Click revoke
        await page.click('button:has-text("Revoke")');

        // Wait for the API call and refetch
        await page.waitForTimeout(500);

        // Reload to see updated list
        await page.reload();

        // Key should be gone (empty state)
        await expect(page.getByText('Key to Revoke')).not.toBeVisible();
    });

    test('cancels revocation when user clicks cancel', async ({ page }) => {
        const mockKey = {
            id: 1,
            prefix: 'abc12345',
            name: 'Protected Key',
            created_at: new Date().toISOString(),
            expires_at: null,
            is_active: true,
        };

        await page.route('**/api-keys', async (route) => {
            if (route.request().method() === 'GET') {
                await route.fulfill({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify([mockKey]),
                });
            }
        });

        await page.click('a[href="/app/api-keys"]');
        await page.waitForURL(/\/app\/api-keys/);

        // Set up dialog handler to cancel
        page.once('dialog', (dialog) => {
            dialog.dismiss();
        });

        // Click revoke
        await page.click('button:has-text("Revoke")');

        // Key should still be visible
        await expect(page.getByText('Protected Key')).toBeVisible();
    });

    test('shows expiration date when set', async ({ page }) => {
        const expiryDate = new Date();
        expiryDate.setDate(expiryDate.getDate() + 30);

        const mockKey = {
            id: 1,
            prefix: 'abc12345',
            name: 'Expiring Key',
            created_at: new Date().toISOString(),
            expires_at: expiryDate.toISOString(),
            is_active: true,
        };

        await page.route('**/api-keys', async (route) => {
            if (route.request().method() === 'GET') {
                await route.fulfill({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify([mockKey]),
                });
            }
        });

        await page.click('a[href="/app/api-keys"]');
        await page.waitForURL(/\/app\/api-keys/);

        // Verify expiry is shown (should not be "Never")
        await expect(page.getByText('Expiring Key')).toBeVisible();
        // The exact date format may vary, but it should not say "Never"
        const rows = page.locator('tbody tr');
        const expiryCell = rows.locator('td').nth(4); // Expires column
        const expiryText = await expiryCell.textContent();
        expect(expiryText).not.toBe('Never');
    });

    test('validates required name field', async ({ page }) => {
        await page.route('**/api-keys', async (route) => {
            if (route.request().method() === 'GET') {
                await route.fulfill({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify([]),
                });
            }
        });

        await page.click('a[href="/app/api-keys"]');
        await page.waitForURL(/\/app\/api-keys/);

        // Open create modal
        await page.click('button:has-text("Create API Key")');

        // Create button should be disabled when name is empty
        const createButton = page.getByRole('button', { name: 'Create Key' });
        await expect(createButton).toBeDisabled();

        // Fill in name
        await page.fill('input[id="keyName"]', 'Valid Name');

        // Button should now be enabled
        await expect(createButton).toBeEnabled();
    });

    test('creates key with expiration date', async ({ page }) => {
        await page.route('**/api-keys', async (route) => {
            if (route.request().method() === 'GET') {
                await route.fulfill({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify([]),
                });
            } else if (route.request().method() === 'POST') {
                const requestBody = await route.request().postDataJSON();
                expect(requestBody.expires_at).toBeTruthy();

                await route.fulfill({
                    status: 201,
                    contentType: 'application/json',
                    body: JSON.stringify({
                        api_key: {
                            id: 1,
                            prefix: 'abc12345',
                            name: requestBody.name,
                            created_at: new Date().toISOString(),
                            expires_at: requestBody.expires_at,
                            is_active: true,
                        },
                        raw_key: 'abc12345.secret',
                    }),
                });
            }
        });

        await page.click('a[href="/app/api-keys"]');
        await page.waitForURL(/\/app\/api-keys/);

        // Open modal
        await page.click('button:has-text("Create API Key")');

        // Fill form with expiry
        await page.fill('input[id="keyName"]', 'Expiring Key');

        // Set expiry date (format: YYYY-MM-DDTHH:MM)
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        const dateString = tomorrow.toISOString().slice(0, 16);
        await page.fill('input[id="keyExpiry"]', dateString);

        // Submit
        await page.click('button:has-text("Create Key")');

        // Verify success
        await expect(page.getByText('API Key Created Successfully')).toBeVisible();
    });

    test('copy button functionality', async ({ page }) => {
        await page.route('**/api-keys', async (route) => {
            if (route.request().method() === 'GET') {
                await route.fulfill({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify([]),
                });
            } else if (route.request().method() === 'POST') {
                await route.fulfill({
                    status: 201,
                    contentType: 'application/json',
                    body: JSON.stringify({
                        api_key: {
                            id: 1,
                            prefix: 'copytest',
                            name: 'Copy Test',
                            created_at: new Date().toISOString(),
                            expires_at: null,
                            is_active: true,
                        },
                        raw_key: 'copytest.this_should_be_copied',
                    }),
                });
            }
        });

        await page.click('a[href="/app/api-keys"]');
        await page.waitForURL(/\/app\/api-keys/);

        // Create a key
        await page.click('button:has-text("Create API Key")');
        await page.fill('input[id="keyName"]', 'Copy Test');
        await page.click('button:has-text("Create Key")');

        // Grant clipboard permissions
        await page.context().grantPermissions(['clipboard-write', 'clipboard-read']);

        // Click copy button
        await page.click('button:has-text("Copy")');

        // Verify text was copied to clipboard
        const clipboardText = await page.evaluate(() => navigator.clipboard.readText());
        expect(clipboardText).toBe('copytest.this_should_be_copied');
    });

    test('handles API error gracefully', async ({ page }) => {
        await page.route('**/api-keys', async (route) => {
            if (route.request().method() === 'GET') {
                await route.fulfill({
                    status: 500,
                    contentType: 'application/json',
                    body: JSON.stringify({
                        detail: 'Internal server error',
                    }),
                });
            }
        });

        await page.click('a[href="/app/api-keys"]');
        await page.waitForURL(/\/app\/api-keys/);

        // Should show error message
        await expect(page.getByText(/Error loading API keys/)).toBeVisible();
    });
});
