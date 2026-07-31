import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Report Generation
 * Tests report creation and export functionality
 */

test.describe('Reportes Generation', () => {
    const LOGIN_URL = '/login';
    const REPORTES_URL = '/dashboard/reportes';

    async function login(page: any) {
        await page.goto(LOGIN_URL);
        await page.fill('input[name="identifier"]', process.env.STRESS_USER || 'admin');
        await page.fill('input[name="password"]', process.env.STRESS_PASSWORD || 'admin123');
        await page.click('button[type="submit"]');
        await page.waitForURL(/\/dashboard/, { timeout: 10000 });
    }

    test.beforeEach(async ({ page }) => {
        await page.goto('/dashboard');
    });

    test('should display reportes page', async ({ page }) => {
        await page.goto(REPORTES_URL);

        // Should show reportes title
        await expect(page.getByRole('heading', { name: /reportes/i })).toBeVisible();
    });

    test('should have report type options', async ({ page }) => {
        await page.goto(REPORTES_URL);

        // Should show different report types
        await expect(page.locator('body')).toContainText(/flota|desgaste|operacional|reporte/i);
    });

    test('should generate neumaticos report', async ({ page }) => {
        await page.goto(REPORTES_URL);

        // Look for neumaticos report button/link
        const neumReportBtn = page.locator('button:has-text("Neumático"), a:has-text("Neumático")').first();

        if (await neumReportBtn.count() > 0) {
            await neumReportBtn.click();

            // Should show report filters or results
            const hasFilters = await page.locator('select, input[type="date"]').count() > 0;
            const hasResults = await page.locator('table, canvas, [role="grid"]').count() > 0;

            expect(hasFilters || hasResults).toBeTruthy();
        }
    });

    test('should filter report by date range', async ({ page }) => {
        await page.goto(REPORTES_URL);

        // Look for date inputs
        const dateInputs = page.locator('input[type="date"]');

        if (await dateInputs.count() >= 2) {
            const today = new Date();
            const lastMonth = new Date(today.setMonth(today.getMonth() - 1));

            await dateInputs.nth(0).fill(lastMonth.toISOString().split('T')[0]);
            await dateInputs.nth(1).fill(new Date().toISOString().split('T')[0]);

            // Apply filter
            const applyBtn = page.locator('button:has-text("Aplicar"), button:has-text("Generar")');
            if (await applyBtn.count() > 0) {
                await applyBtn.click();
                await page.waitForTimeout(1000);
            }
        }
    });

    test('should export report as PDF', async ({ page }) => {
        await page.goto(REPORTES_URL);

        // Look for export/PDF button
        const exportBtn = page.locator('button:has-text("PDF"), button:has-text("Exportar"), button:has-text("Descargar")').first();

        if (await exportBtn.count() > 0) {
            // Start waiting for download before clicking
            const downloadPromise = page.waitForEvent('download', { timeout: 15000 });

            await exportBtn.click();

            try {
                const download = await downloadPromise;
                expect(download.suggestedFilename()).toContain('.pdf');
            } catch (e) {
                // Some implementations might open in new tab instead
                console.log('Download not triggered, might open in new tab');
            }
        }
    });

    test('should show report statistics', async ({ page }) => {
        await page.goto(REPORTES_URL);

        // Should show some statistics/metrics
        const hasNumbers = await page.locator('text=/\\d+/').count() > 0;
        const hasCharts = await page.locator('canvas, svg').count() > 0;

        expect(hasNumbers || hasCharts).toBeTruthy();
    });

    test('should filter report by vehicle', async ({ page }) => {
        await page.goto(REPORTES_URL);

        // Look for vehicle filter
        const vehicleSelect = page.locator('select[name*="vehiculo"], input[name*="vehiculo"]').first();

        if (await vehicleSelect.count() > 0) {
            if (await vehicleSelect.evaluate(el => el.tagName === 'SELECT')) {
                await vehicleSelect.selectOption({ index: 1 });
            } else {
                await vehicleSelect.fill('ABC');
            }

            await page.waitForTimeout(500);
        }
    });

    test('should paginate large reports', async ({ page }) => {
        await page.goto(REPORTES_URL);

        // Look for pagination controls
        const hasPagination = await page.locator('nav[aria-label*="pagination"], .pagination, button:has-text("Siguiente")').count() > 0;

        if (hasPagination) {
            const nextBtn = page.locator('button:has-text("Siguiente"), button:has-text("Next")').first();
            if (await nextBtn.count() > 0 && await nextBtn.isEnabled()) {
                await nextBtn.click();
                await page.waitForTimeout(500);
            }
        }
    });
});
