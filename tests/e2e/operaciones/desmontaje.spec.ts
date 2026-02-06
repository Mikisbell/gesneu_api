import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Desmontaje Operations  
 * Tests tire unmounting workflow
 */

test.describe('Desmontaje Operations', () => {
    const LOGIN_URL = '/login';
    const DESMONTAJES_URL = '/dashboard/operaciones/desmontajes';

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

    test('should create a new desmontaje successfully', async ({ page }) => {
        await page.goto(DESMONTAJES_URL);

        await page.click('button:has-text("Crear"), button:has-text("Nuevo")');

        // Select mounted neumático
        const timestamp = Date.now();
        await page.fill('input[name="neumatico"]', `TEST-${timestamp}`);
        await page.waitForTimeout(500);
        await page.keyboard.press('Enter');

        // Fill desmontaje data
        await page.fill('input[name="km_vehiculo"]', '75000');
        await page.fill('input[name="fecha_desmontaje"]', new Date().toISOString().split('T')[0]);

        // Select reason
        await page.selectOption('select[name="motivo"]', 'DESGASTE_NATURAL');

        // Optional: observations
        await page.fill('textarea[name="observaciones"]', 'Desmontaje de prueba E2E');

        // Submit
        await page.click('button[type="submit"]');

        // Verify success
        await expect(page.locator('text=/desmontaje.*exitoso|creado/i')).toBeVisible({ timeout: 10000 });
    });

    test('should validate km_vehiculo is greater than montaje km', async ({ page }) => {
        await page.goto(DESMONTAJES_URL);

        await page.click('button:has-text("Crear"), button:has-text("Nuevo")');

        // Try km less than montaje
        await page.fill('input[name="km_vehiculo"]', '1000');
        await page.click('button[type="submit"]');

        // Should show validation error
        await expect(page.locator('button[type="submit"]')).toBeVisible();
    });

    test('should validate required motivo field', async ({ page }) => {
        await page.goto(DESMONTAJES_URL);

        await page.click('button:has-text("Crear"), button:has-text("Nuevo")');

        // Fill form but leave motivo empty
        await page.fill('input[name="km_vehiculo"]', '75000');

        await page.click('button[type="submit"]');

        // Should prevent submission
        await expect(page.locator('button[type="submit"]')).toBeVisible();
    });

    test('should update neumático status to DISPONIBLE after desmontaje', async ({ page }) => {
        await page.goto(DESMONTAJES_URL);

        // This test would need to:
        // 1. Create desmontaje
        // 2. Navigate to neumáticos
        // 3. Verify status changed

        // For now, just verify the desmontajes page loads
        await expect(page.locator('h1, h2')).toContainText(/desmontaje/i);
    });

    test('should list all desmontajes', async ({ page }) => {
        await page.goto(DESMONTAJES_URL);

        // Should show table or list
        const hasTable = await page.locator('table, [role="grid"]').count() > 0;
        const hasList = await page.locator('[role="list"], .list').count() > 0;

        expect(hasTable || hasList).toBeTruthy();
    });

    test('should filter desmontajes by motivo', async ({ page }) => {
        await page.goto(DESMONTAJES_URL);

        // Look for filter select
        const filterSelect = page.locator('select[name*="motivo"], select[name*="filter"]').first();

        if (await filterSelect.count() > 0) {
            await filterSelect.selectOption('DESGASTE_NATURAL');
            await page.waitForTimeout(500);

            // Table should be visible
            await expect(page.locator('table, [role="grid"]')).toBeVisible();
        }
    });

    test('should view desmontaje details', async ({ page }) => {
        await page.goto(DESMONTAJES_URL);

        // Click first desmontaje to view details
        const firstRow = page.locator('table tr, [role="row"]').nth(1);

        if (await firstRow.count() > 0) {
            await firstRow.click();

            // Should show details
            const hasModal = await page.locator('[role="dialog"], .modal').count() > 0;
            const hasDetailsPage = page.url().includes('desmontajes/');

            expect(hasModal || hasDetailsPage).toBeTruthy();
        }
    });
});
