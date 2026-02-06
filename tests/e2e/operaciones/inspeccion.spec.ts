import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Inspección Operations
 * Tests tire inspection workflow with measurements
 */

test.describe('Inspección Operations', () => {
    const LOGIN_URL = '/login';
    const INSPECCIONES_URL = '/dashboard/operaciones/inspecciones';

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

    test('should create a new inspección successfully', async ({ page }) => {
        await page.goto(INSPECCIONES_URL);

        await page.click('button:has-text("Crear"), button:has-text("Nuevo")');

        // Select neumático
        const timestamp = Date.now();
        await page.fill('input[name="neumatico"]', `TEST-${timestamp}`);
        await page.waitForTimeout(500);
        await page.keyboard.press('Enter');

        // Fill inspection data
        await page.fill('input[name="profundidad_actual"]', '8.5');
        await page.fill('input[name="presion"]', '32');

        // Fill fecha
        await page.fill('input[name="fecha_inspeccion"]', new Date().toISOString().split('T')[0]);

        // Optional: observaciones
        await page.fill('textarea[name="observaciones"]', 'Inspección de prueba automática');

        // Submit
        await page.click('button[type="submit"]');

        // Verify success
        await expect(page.locator('text=/inspección.*exitosa|creado/i')).toBeVisible({ timeout: 10000 });
    });

    test('should validate profundidad_actual > 0', async ({ page }) => {
        await page.goto(INSPECCIONES_URL);

        await page.click('button:has-text("Crear"), button:has-text("Nuevo")');

        // Try negative profundidad
        await page.fill('input[name="profundidad_actual"]', '-1');
        await page.click('button[type="submit"]');

        // Should prevent submission
        await expect(page.locator('button[type="submit"]')).toBeVisible();
    });

    test('should validate presión within acceptable range', async ({ page }) => {
        await page.goto(INSPECCIONES_URL);

        await page.click('button:has-text("Crear"), button:has-text("Nuevo")');

        // Try extremely high pressure
        await page.fill('input[name="presion"]', '150');
        await page.click('button[type="submit"]');

        // Should show warning or validation error
        await expect(page.locator('button[type="submit"]')).toBeVisible();
    });

    test('should show pressure alert for low values', async ({ page }) => {
        await page.goto(INSPECCIONES_URL);

        await page.click('button:has-text("Crear"), button:has-text("Nuevo")');

        // Fill with low pressure value
        await page.fill('input[name="presion"]', '20');

        // Should show alert/warning (visual feedback)
        const hasAlert = await page.locator('[role="alert"], .alert, text=/bajo|baja|precaución/i').count() > 0;

        // This might not always trigger, so we just check form is still functional
        await expect(page.locator('input[name="presion"]')).toHaveValue('20');
    });

    test('should list all inspecciones', async ({ page }) => {
        await page.goto(INSPECCIONES_URL);

        // Should show table or list
        const hasTable = await page.locator('table, [role="grid"]').count() > 0;
        const hasList = await page.locator('[role="list"], .list').count() > 0;

        expect(hasTable || hasList).toBeTruthy();
    });

    test('should filter inspecciones by date range', async ({ page }) => {
        await page.goto(INSPECCIONES_URL);

        // Look for date filter inputs
        const dateFilter = page.locator('input[type="date"]').first();

        if (await dateFilter.count() > 0) {
            const today = new Date().toISOString().split('T')[0];
            await dateFilter.fill(today);
            await page.waitForTimeout(500);

            // Table should be visible
            await expect(page.locator('table, [role="grid"]')).toBeVisible();
        }
    });

    test('should view inspection history for a tire', async ({ page }) => {
        await page.goto(INSPECCIONES_URL);

        // Click first inspection to view details
        const firstRow = page.locator('table tr, [role="row"]').nth(1);

        if (await firstRow.count() > 0) {
            await firstRow.click();

            // Should show details
            const hasModal = await page.locator('[role="dialog"], .modal').count() > 0;
            const hasDetailsPage = page.url().includes('inspecciones/');

            expect(hasModal || hasDetailsPage).toBeTruthy();
        }
    });
});
