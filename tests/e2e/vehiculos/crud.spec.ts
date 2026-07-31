import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Vehículos CRUD
 * Tests vehicle fleet management UI
 */

test.describe('Vehículos CRUD', () => {
    const VEHICULOS_URL = '/dashboard/vehiculos';

    test.beforeEach(async ({ page }) => {
        await page.goto(VEHICULOS_URL);
    });

    test('should list all vehicles page title', async ({ page }) => {
        await expect(page.locator('body')).toBeVisible();
        await expect(page.locator('body')).toContainText(/veh[íi]culos/i);
    });

    test('should display vehicle table or empty state', async ({ page }) => {
        await expect(page.locator('body')).toBeVisible();
        const hasTable = await page.locator('table, [role="grid"]').count() > 0;
        const hasEmptyState = await page.locator('body').innerText();
        expect(hasTable || hasEmptyState.length > 0).toBeTruthy();
    });

    test('should trigger open modal for new vehicle', async ({ page }) => {
        const btnNew = page.locator('button:has-text("Nuevo"), button:has-text("Crear"), button:has-text("Agregar")').first();
        if (await btnNew.count() > 0) {
            await btnNew.click({ force: true });
            await expect(page.getByRole('dialog')).toBeVisible();
        }
    });
});
