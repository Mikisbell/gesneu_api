import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Neumatico CRUD Operations
 * Tests inventory management and tire listing UI
 */

test.describe('Neumatico CRUD Operations', () => {
    const NEUMATICOS_URL = '/dashboard/neumaticos';

    test.beforeEach(async ({ page }) => {
        await page.goto(NEUMATICOS_URL);
    });

    test('should load neumaticos inventory page', async ({ page }) => {
        await expect(page.getByRole('main')).toBeVisible();
    });

    test('should open new neumatico modal on button click', async ({ page }) => {
        const btnNew = page.locator('[data-testid="btn-new-neumatico"], button:has-text("Nuevo")').first();
        await btnNew.click({ force: true });
        await expect(page.getByRole('dialog')).toBeVisible();
    });

    test('should display neumaticos table or empty state', async ({ page }) => {
        await expect(page.getByRole('main')).toBeVisible();
        const hasTable = await page.locator('table, [role="grid"]').count() > 0;
        const hasContent = await page.locator('main').innerText();
        expect(hasTable || hasContent.length > 0).toBeTruthy();
    });
});
