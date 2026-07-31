import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Inspección Operations
 * Tests tire inspection workflow UI
 */

test.describe('Inspección Operations', () => {
    const INSPECCIONES_URL = '/dashboard/operaciones/inspeccion';

    test.beforeEach(async ({ page }) => {
        await page.goto('/dashboard');
    });

    test('should load inspección page successfully', async ({ page }) => {
        await page.goto(INSPECCIONES_URL);
        await expect(page.locator('body')).toContainText(/inspección|medición|registrar/i);
    });

    test('should display search input for inspection', async ({ page }) => {
        await page.goto(INSPECCIONES_URL);
        const searchInput = page.locator('input[placeholder*="buscar" i], input[placeholder*="serie" i], input[type="text"]').first();
        await expect(searchInput).toBeVisible();
    });
});
