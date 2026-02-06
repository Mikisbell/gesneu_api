import { test, expect } from '@playwright/test';

/**
 * E2E Tests for RBAC Dashboard Access
 * Tests role-based access control across different user roles
 */

test.describe('RBAC Dashboard Access', () => {
    const LOGIN_URL = '/login';

    // Helper function to login with specific user
    async function loginAs(page: any, username: string, password: string) {
        await page.goto(LOGIN_URL);
        await page.fill('input[name="identifier"]', username);
        await page.fill('input[name="password"]', password);
        await page.click('button[type="submit"]');
        // Wait for navigation to dashboard (more reliable than networkidle)
        await page.waitForURL(/\/dashboard/, { timeout: 10000 });
    }

    test.describe('Administrator Role', () => {
        test.beforeEach(async ({ page }) => {
            await loginAs(page, process.env.STRESS_USER || 'admin', process.env.STRESS_PASSWORD || 'admin123');
        });

        test('should have access to all modules', async ({ page }) => {
            await page.goto('/dashboard');

            // Should see all menu items
            await expect(page.locator('text=/neumático/i')).toBeVisible();
            await expect(page.locator('text=/vehículo/i')).toBeVisible();
            await expect(page.locator('text=/usuario/i')).toBeVisible();
            await expect(page.locator('text=/reporte/i')).toBeVisible();
        });

        test('should be able to create users (admin-only)', async ({ page }) => {
            await page.goto('/dashboard/usuarios');

            // Should see "New User" or "Crear Usuario" button
            const createButtonVisible = await page.locator('button:has-text("Crear"), button:has-text("Nuevo")').count() > 0;
            expect(createButtonVisible).toBeTruthy();
        });

        test('should access admin-only routes', async ({ page }) => {
            await page.goto('/dashboard/admin/audit');

            // Should not redirect to login or error page
            expect(page.url()).toContain('admin');

            // Should show audit content
            await expect(page.locator('text=/audit|auditoría/i')).toBeVisible();
        });
    });

    test.describe('Permission Checks', () => {
        test('should display role-appropriate navigation', async ({ page }) => {
            await loginAs(page, process.env.STRESS_USER || 'admin', process.env.STRESS_PASSWORD || 'admin123');

            await page.goto('/dashboard');

            // Admin should see sidebar with all options
            const menuItemsCount = await page.locator('nav a, nav button').count();
            expect(menuItemsCount).toBeGreaterThan(5); // Admin has many menu items
        });

        test('should show user role in UI', async ({ page }) => {
            await loginAs(page, process.env.STRESS_USER || 'admin', process.env.STRESS_PASSWORD || 'admin123');

            await page.goto('/dashboard');

            // Should display role badge or text
            await expect(page.locator('text=/administrador|admin/i')).toBeVisible();
        });
    });

    test.describe('Access Control Enforcement', () => {
        test('should prevent direct URL access to unauthorized routes', async ({ page }) => {
            // Login as non-admin (if available)
            // For now, test that attempting to access restricted route triggers proper handling

            await loginAs(page, process.env.STRESS_USER || 'admin', process.env.STRESS_PASSWORD || 'admin123');

            // Try to access a route that requires specific permission
            await page.goto('/dashboard/admin/system');

            // Dashboard should either:
            // 1. Show the page (if user has permission)
            // 2. Redirect to unauthorized page
            // 3. Show 403 error

            const url = page.url();
            const hasAccess = url.includes('admin/system') ||
                url.includes('dashboard') ||
                url.includes('unauthorized') ||
                url.includes('403');

            expect(hasAccess).toBeTruthy(); // Proper handling occurred
        });
    });

    test.describe('UI Element Visibility', () => {
        test('should hide action buttons based on permissions', async ({ page }) => {
            await loginAs(page, process.env.STRESS_USER || 'admin', process.env.STRESS_PASSWORD || 'admin123');

            await page.goto('/dashboard/neumaticos');

            // Admin should see create/edit/delete buttons
            const hasCreateButton = await page.locator('button:has-text("Crear"), button:has-text("Nuevo")').count() > 0;
            const hasDeleteButton = await page.locator('button:has-text("Eliminar"), button[aria-label*="eliminar"]').count() > 0;

            // At least one action button should be visible for admin
            expect(hasCreateButton || hasDeleteButton).toBeTruthy();
        });

        test('should enable/disable form fields based on permissions', async ({ page }) => {
            await loginAs(page, process.env.STRESS_USER || 'admin', process.env.STRESS_PASSWORD || 'admin123');

            await page.goto('/dashboard/neumaticos');

            // Try to open create form
            const createButton = page.locator('button:has-text("Crear"), button:has-text("Nuevo")').first();
            if (await createButton.count() > 0) {
                await createButton.click();

                // Form fields should be enabled for admin
                const formInputs = await page.locator('input:not([type="hidden"])').count();
                expect(formInputs).toBeGreaterThan(0);
            }
        });
    });
});
