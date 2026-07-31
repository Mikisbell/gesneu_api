import { test, expect } from '@playwright/test';
import path from 'path';

/**
 * Screenshot Capture Script for Documentation
 * Captures key screens for README
 */

test.describe('Documentation Screenshots', () => {
    const LOGIN_URL = '/login';
    const SCREENSHOTS_DIR = path.join(process.cwd(), 'docs', 'screenshots');

    async function login(page: any) {
        await page.goto('/dashboard');
        if (page.url().includes('/login')) {
            await page.fill('input[name="identifier"]', process.env.STRESS_USER || 'admin@gesneu.com');
            await page.fill('input[name="password"]', process.env.STRESS_PASSWORD || 'admin123');
            await page.click('button[type="submit"]');
            await page.waitForURL(/\/dashboard/, { timeout: 10000 });
        }
    }

    test('capture dashboard home', async ({ page }) => {
        await login(page);
        await page.goto('/dashboard');
        await page.waitForTimeout(2000);

        await page.screenshot({
            path: path.join(SCREENSHOTS_DIR, 'dashboard-home.png'),
            fullPage: true
        });
    });

    test('capture neumaticos list', async ({ page }) => {
        await login(page);
        await page.goto('/dashboard/neumaticos');
        await page.waitForTimeout(2000);

        await page.screenshot({
            path: path.join(SCREENSHOTS_DIR, 'neumaticos-list.png'),
            fullPage: true
        });
    });

    test('capture operations montaje', async ({ page }) => {
        await login(page);
        await page.goto('/dashboard/operaciones/montajes');
        await page.waitForTimeout(2000);

        await page.screenshot({
            path: path.join(SCREENSHOTS_DIR, 'operaciones-montaje.png'),
            fullPage: true
        });
    });

    test('capture vehiculos list', async ({ page }) => {
        await login(page);
        await page.goto('/dashboard/vehiculos');
        await page.waitForTimeout(2000);

        await page.screenshot({
            path: path.join(SCREENSHOTS_DIR, 'vehiculos-list.png'),
            fullPage: true
        });
    });

    test('capture reportes', async ({ page }) => {
        await login(page);
        await page.goto('/dashboard/reportes');
        await page.waitForTimeout(2000);

        await page.screenshot({
            path: path.join(SCREENSHOTS_DIR, 'reportes.png'),
            fullPage: true
        });
    });
});
