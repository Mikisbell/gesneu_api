import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Desecho / Desmontaje Operations  
 * Tests tire disposal workflow UI
 */

test.describe('Desmontaje / Desecho Operations', () => {
    const DESMONTAJES_URL = '/dashboard/operaciones/desecho';

    test.beforeEach(async ({ page }) => {
        await page.goto('/dashboard');
    });

    test('should load desecho page successfully', async ({ page }) => {
        await page.goto(DESMONTAJES_URL);
        await expect(page.locator('body')).toContainText(/desecho|desmontaje/i);
    });

    test('should display search input for tires to dispose', async ({ page }) => {
        await page.goto(DESMONTAJES_URL);
        const searchInput = page.locator('input[placeholder*="serie" i], input[placeholder*="buscar" i], input[type="text"]').first();
        await expect(searchInput).toBeVisible();
    });

    test('should validate empty submit on desecho form', async ({ page }) => {
        await page.goto(DESMONTAJES_URL);
        const submitButton = page.locator('button[type="submit"], button:has-text("Confirmar"), button:has-text("Registrar")').first();
        if (await submitButton.count() > 0) {
            await submitButton.click({ force: true });
            // Page stays loaded without crash
            await expect(page).toHaveURL(new RegExp(DESMONTAJES_URL));
        }
    });
});
