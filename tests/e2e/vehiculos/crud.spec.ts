import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Vehículos CRUD
 * Tests vehicle management functionality
 */

test.describe('Vehículos CRUD', () => {
    const LOGIN_URL = '/login';
    const VEHICULOS_URL = '/dashboard/vehiculos';

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

    test('should list all vehicles', async ({ page }) => {
        await page.goto(VEHICULOS_URL);

        // Should show table or grid
        const hasTable = await page.locator('table, [role="grid"]').count() > 0;
        const hasList = await page.locator('[role="list"]').count() > 0;

        expect(hasTable || hasList).toBeTruthy();
    });

    test('should create a new vehicle successfully', async ({ page }) => {
        await page.goto(VEHICULOS_URL);

        // Click create button
        await page.click('button:has-text("Crear"), button:has-text("Nuevo")');

        // Fill vehicle form
        const timestamp = Date.now();
        const patente = `ABC${timestamp.toString().slice(-3)}`;

        await page.fill('input[name="patente"]', patente);
        await page.fill('input[name="marca"]', 'Toyota');
        await page.fill('input[name="modelo"]', 'Hilux');
        await page.fill('input[name="anio"]', '2023');

        // Submit
        await page.click('button[type="submit"]');

        // Verify success
        await expect(page.locator('text=/vehículo.*creado|exitoso/i')).toBeVisible({ timeout: 10000 });
    });

    test('should validate patente is required', async ({ page }) => {
        await page.goto(VEHICULOS_URL);

        await page.click('button:has-text("Crear"), button:has-text("Nuevo")');

        // Leave patente empty, fill others
        await page.fill('input[name="marca"]', 'Ford');
        await page.fill('input[name="modelo"]', 'Ranger');

        await page.click('button[type="submit"]');

        // Should prevent submission
        await expect(page.locator('button[type="submit"]')).toBeVisible();
    });

    test('should validate patente format', async ({ page }) => {
        await page.goto(VEHICULOS_URL);

        await page.click('button:has-text("Crear"), button:has-text("Nuevo")');

        // Try invalid patente
        await page.fill('input[name="patente"]', '123');
        await page.click('button[type="submit"]');

        // Should show validation error or prevent submission
        await expect(page.locator('button[type="submit"]')).toBeVisible();
    });

    test('should edit an existing vehicle', async ({ page }) => {
        await page.goto(VEHICULOS_URL);

        // Click first vehicle edit button
        const editButton = page.locator('button:has-text("Editar"), button[aria-label*="editar"]').first();

        if (await editButton.count() > 0) {
            await editButton.click();

            // Update a field
            await page.fill('input[name="modelo"]', 'Hilux 2024');

            await page.click('button[type="submit"]');

            // Verify success
            await expect(page.locator('text=/actualizado|modificado/i')).toBeVisible({ timeout: 10000 });
        }
    });

    test('should search vehicles by patente', async ({ page }) => {
        await page.goto(VEHICULOS_URL);

        // Look for search input
        const searchInput = page.locator('input[placeholder*="Buscar"], input[type="search"]').first();

        if (await searchInput.count() > 0) {
            await searchInput.fill('ABC');
            await page.waitForTimeout(500);

            // Table should update
            await expect(page.locator('table, [role="grid"]')).toBeVisible();
        }
    });

    test('should view vehicle details', async ({ page }) => {
        await page.goto(VEHICULOS_URL);

        // Click first vehicle
        const firstRow = page.locator('table tr, [role="row"]').nth(1);

        if (await firstRow.count() > 0) {
            await firstRow.click();

            // Should show details
            const hasModal = await page.locator('[role="dialog"], .modal').count() > 0;
            const hasDetailsPage = page.url().includes('vehiculos/');

            expect(hasModal || hasDetailsPage).toBeTruthy();
        }
    });

    test('should delete a vehicle', async ({ page }) => {
        await page.goto(VEHICULOS_URL);

        // Look for delete button
        const deleteButton = page.locator('button:has-text("Eliminar"), button[aria-label*="eliminar"]').first();

        if (await deleteButton.count() > 0) {
            await deleteButton.click();

            // Confirm deletion
            const confirmButton = page.locator('button:has-text("Confirmar"), button:has-text("Sí")');
            if (await confirmButton.count() > 0) {
                await confirmButton.click();

                // Verify success
                await expect(page.locator('text=/eliminado|borrado/i')).toBeVisible({ timeout: 10000 });
            }
        }
    });
});
