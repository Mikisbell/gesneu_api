import { Page, Locator, expect } from '@playwright/test';

/**
 * Page Object Model for Neumatico Registration Flow
 * Follows SOLID principles and provides resilient selectors
 */
export class NeumaticoPage {
    readonly page: Page;

    // Locators con data-testid para estabilidad
    readonly newNeumaticoButton: Locator;
    readonly numeroSerieInput: Locator;
    readonly modeloSelect: Locator;
    readonly dotInput: Locator;
    readonly profundidadInput: Locator;
    readonly costoInput: Locator;
    readonly fechaCompraInput: Locator;
    readonly submitButton: Locator;
    readonly cancelButton: Locator;
    readonly successToast: Locator;
    readonly errorToast: Locator;
    readonly loadingSpinner: Locator;
    readonly tableRows: Locator;

    constructor(page: Page) {
        this.page = page;

        // Navigation
        this.newNeumaticoButton = page.getByTestId('btn-new-neumatico');

        // Form inputs
        this.numeroSerieInput = page.getByTestId('input-numero-serie');
        this.modeloSelect = page.getByTestId('select-modelo');
        this.dotInput = page.getByTestId('input-dot');
        this.profundidadInput = page.getByTestId('input-profundidad-inicial');
        this.costoInput = page.getByTestId('input-costo-compra');
        this.fechaCompraInput = page.getByTestId('input-fecha-compra');

        // Actions
        this.submitButton = page.getByTestId('btn-submit-neumatico');
        this.cancelButton = page.getByTestId('btn-cancel-neumatico');

        // Feedback
        this.successToast = page.getByTestId('toast-success');
        this.errorToast = page.getByTestId('toast-error');
        this.loadingSpinner = page.getByTestId('loading-spinner');

        // List
        this.tableRows = page.getByTestId('neumatico-table-row');
    }

    /**
     * Navigate to neumaticos page
     */
    async goto() {
        await this.page.goto('/neumaticos');
        await this.waitForPageLoad();
    }

    /**
     * Wait for page to be fully loaded
     * Resilient to network latency
     */
    async waitForPageLoad() {
        await this.page.waitForLoadState('networkidle');
        await expect(this.page).toHaveTitle(/Neumáticos|GesNeu/i);
    }

    /**
     * Open new neumatico form
     */
    async openNewForm() {
        await this.newNeumaticoButton.click();
        await this.waitForFormVisible();
    }

    /**
     * Wait for form to be visible and ready
     */
    async waitForFormVisible() {
        await expect(this.numeroSerieInput).toBeVisible();
        await expect(this.submitButton).toBeEnabled();
    }

    /**
     * Wait for loading to complete
     * Max 5000ms as per requirements
     */
    async waitForLoadingComplete() {
        if (await this.loadingSpinner.isVisible({ timeout: 1000 }).catch(() => false)) {
            await this.loadingSpinner.waitFor({ state: 'hidden', timeout: 5000 });
        }
    }

    /**
     * Fill neumatico form with validation
     */
    async fillForm(data: {
        numeroSerie: string;
        modeloId?: string;
        dot?: string;
        profundidadInicial: string | number;
        costoCompra: string | number;
        fechaCompra?: string;
    }) {
        // Numero Serie
        await this.numeroSerieInput.fill(data.numeroSerie);

        // Modelo (if provided)
        if (data.modeloId) {
            await this.modeloSelect.selectOption(data.modeloId);
        }

        // DOT (optional)
        if (data.dot) {
            await this.dotInput.fill(data.dot);
        }

        // Profundidad Inicial
        await this.profundidadInput.fill(String(data.profundidadInicial));

        // Costo Compra
        await this.costoInput.fill(String(data.costoCompra));

        // Fecha Compra intentionally omitted (handled by auto-fill or server)    }
    }

    /**
     * Submit form and wait for response
     */
    async submitForm() {
        // Wait for network request to complete
        const responsePromise = this.page.waitForResponse(
            response => response.url().includes('/api/neumaticos') && response.status() !== 304,
            { timeout: 10000 }
        );

        await this.submitButton.click();

        const response = await responsePromise;
        return response;
    }

    /**
     * Submit form and expect success
     */
    async submitAndExpectSuccess() {
        const response = await this.submitForm();
        await expect(response.status()).toBeLessThan(400);
        await this.waitForSuccessToast();
    }

    /**
     * Submit form and expect error
     */
    async submitAndExpectError(expectedMessage?: string) {
        const response = await this.submitForm();
        expect(response.status()).toBeGreaterThanOrEqual(400);
        await this.waitForErrorToast();

        if (expectedMessage) {
            await expect(this.errorToast).toContainText(expectedMessage);
        }
    }

    /**
     * Wait for success toast with timeout
     */
    async waitForSuccessToast() {
        await expect(this.successToast).toBeVisible({ timeout: 5000 });
    }

    /**
     * Wait for error toast with timeout
     */
    async waitForErrorToast() {
        await expect(this.errorToast).toBeVisible({ timeout: 5000 });
    }

    /**
     * Get neumatico from table by numero_serie
     */
    async getNeumaticoFromTable(numeroSerie: string) {
        const row = this.tableRows.filter({ hasText: numeroSerie }).first();
        await expect(row).toBeVisible();
        return row;
    }

    /**
     * Verify optimistic update happened
     */
    async verifyOptimisticUpdate(numeroSerie: string) {
        // Should appear immediately (optimistic)
        const row = this.tableRows.filter({ hasText: numeroSerie }).first();
        await expect(row).toBeVisible({ timeout: 500 });
    }

    /**
     * Verify rollback happened (on error)
     */
    async verifyRollback(numeroSerie: string) {
        // Should disappear after error
        const row = this.tableRows.filter({ hasText: numeroSerie }).first();
        await expect(row).not.toBeVisible({ timeout: 2000 });
    }

    /**
     * Get validation error for specific field
     */
    async getFieldError(fieldTestId: string) {
        const errorLocator = this.page.getByTestId(`${fieldTestId}-error`);
        await expect(errorLocator).toBeVisible();
        return errorLocator.textContent();
    }
}
