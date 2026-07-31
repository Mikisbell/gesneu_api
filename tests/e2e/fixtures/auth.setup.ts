
import { test as setup, expect } from '@playwright/test';
import dotenv from 'dotenv';

dotenv.config({ path: '.env' });

const AUTH_FILE = '.auth/admin.json';

setup('authenticate', async ({ page }) => {
    // Perform authentication steps.
    // This is done only once per execution.
    const LOGIN_URL = '/login';
    const DASHBOARD_URL = '/dashboard';
    const USER = process.env.STRESS_USER || 'admin@gesneu.com';
    const PASS = process.env.STRESS_PASSWORD || 'admin123';

    console.log(`Authenticating as ${USER}...`);

    await page.goto(LOGIN_URL);
    if (page.url().includes('/dashboard')) {
        console.log('Already on dashboard. Saving session...');
        await page.context().storageState({ path: AUTH_FILE });
        return;
    }
    await page.fill('input[name="identifier"]', USER);
    await page.fill('input[name="password"]', PASS);
    await page.click('button[type="submit"]');

    // Wait for navigation to dashboard - this confirms login credentials worked
    await page.waitForURL(new RegExp(DASHBOARD_URL), { timeout: 45000 });

    // In ultra-slow environments (like this dev instance), waiting for UI elements might timeout
    // trusting the URL redirect + network idle is sufficient to capture session cookies
    try {
        await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => { });
    } catch (e) {
        console.log('Network idle timeout ignored');
    }

    // Save storage state immediately
    await page.context().storageState({ path: AUTH_FILE });
    console.log('Authentication successful. State saved to ' + AUTH_FILE);
});
