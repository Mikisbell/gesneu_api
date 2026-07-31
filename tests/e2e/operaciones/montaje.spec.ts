import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Montaje Operations
 * Full functional testing of the tire mounting workflow UI
 */

test.describe('Montaje Operations', () => {
    const MONTAJES_URL = '/dashboard/operaciones/montaje';

    test.beforeEach(async ({ page }) => {
        await page.goto('/dashboard');
    });

    test('should load montaje page successfully', async ({ page }) => {
        await page.goto(MONTAJES_URL);
        await expect(page.locator('body')).toContainText(/montaje/i);
    });

    test('should display vehicle selector and interactive UI elements', async ({ page }) => {
        await page.goto(MONTAJES_URL);
        await expect(page.getByRole('heading', { name: /montaje/i })).toBeVisible();
        await expect(page.locator('body')).toContainText(/Selecciona un veh[íi]culo/i);
    });
});
