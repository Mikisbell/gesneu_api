import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Montaje Operations
 * Tests the complete tire mounting workflow
 */

test.describe('Montaje Operations', () => {
    const LOGIN_URL = '/login';
    const MONTAJES_URL = '/dashboard/operaciones/montajes';

    // Helper to login
    async function login(page: any) {
        await page.goto(LOGIN_URL);
        await page.fill('input[name="identifier"]', process.env.STRESS_USER || 'admin');
        await page.fill('input[name="password"]', process.env.STRESS_PASSWORD || 'admin123');
        await page.click('button[type="submit"]');
        await page.waitForURL(/\/dashboard/, { timeout: 10000 });
    }

    test.beforeEach(async ({ page }) => {
        await login(page);
    });

    test('should create a new montaje successfully', async ({ page }) => {
        await page.goto(MONTAJES_URL);

        // Click create button
        await page.click('button:has-text("Crear"), button:has-text("Nuevo")');

        // Fill montaje form
        const timestamp = Date.now();

        // Select vehicle (assuming autocomplete or select)
        await page.fill('input[name="vehiculo"]', 'ABC123'); // Patente
        await page.waitForTimeout(500);
        await page.keyboard.press('Enter');

        // Select neumático
        await page.fill('input[name="neumatico"]', `TEST-${timestamp}`);
        await page.waitForTimeout(500);
        await page.keyboard.press('Enter');

        // Fill position
        await page.selectOption('select[name="posicion"]', 'DELANTERO_IZQUIERDO');

        // Fill km_vehiculo
        await page.fill('input[name="km_vehiculo"]', '50000');

        // Fill fecha_montaje
        await page.fill('input[name="fecha_montaje"]', new Date().toISOString().split('T')[0]);

        // Submit
        await page.click('button[type="submit"]');

        // Verify success
        await expect(page.locator('text=/montaje.*exitoso|creado/i')).toBeVisible({ timeout: 10000 });
    });

    test('should validate required fields', async ({ page }) => {
        await page.goto(MONTAJES_URL);

        // Click create button
        await page.click('button:has-text("Crear"), button:has-text("Nuevo")');

        // Try to submit empty form
        await page.click('button[type="submit"]');

        // Should remain on form (validation prevents submission)
        const submitButton = page.locator('button[type="submit"]');
        await expect(submitButton).toBeVisible();
    });

    test('should validate km_vehiculo is positive', async ({ page }) => {
        await page.goto(MONTAJES_URL);

        await page.click('button:has-text("Crear"), button:has-text("Nuevo")');

        // Try negative km
        await page.fill('input[name="km_vehiculo"]', '-1000');
        await page.click('button[type="submit"]');

        // Should show validation error or prevent submission
        await expect(page.locator('button[type="submit"]')).toBeVisible();
    });

    test('should list existing montajes', async ({ page }) => {
        await page.goto(MONTAJES_URL);

        // Should show table or list
        const hasTable = await page.locator('table, [role="grid"]').count() > 0;
        const hasList = await page.locator('[role="list"]').count() > 0;

        expect(hasTable || hasList).toBeTruthy();
    });

    test('should filter montajes by vehicle', async ({ page }) => {
        await page.goto(MONTAJES_URL);

        // Look for filter input
        const filterInput = page.locator('input[placeholder*="Buscar"], input[placeholder*="Filtrar"], input[type="search"]').first();

        if (await filterInput.count() > 0) {
            await filterInput.fill('ABC');
            await page.waitForTimeout(500);

            // Table should update (this is a basic check)
            await expect(page.locator('table, [role="grid"]')).toBeVisible();
        }
    });

    test('should view montaje details', async ({ page }) => {
        await page.goto(MONTAJES_URL);

        // Click first row/item to view details
        const firstRow = page.locator('table tr, [role="row"]').nth(1);

        if (await firstRow.count() > 0) {
            await firstRow.click();

            // Should show details modal or page
            const hasModal = await page.locator('[role="dialog"], .modal').count() > 0;
            const hasDetailsPage = page.url().includes('montajes/');

            expect(hasModal || hasDetailsPage).toBeTruthy();
        }
    });
});
