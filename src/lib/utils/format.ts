/**
 * Utility functions for formatting values
 */

/**
 * Formats a number as currency (USD by default)
 */
export function formatCurrency(
    value: number | null | undefined,
    currency: string = 'USD',
    locale: string = 'es-PE'
): string {
    if (value === null || value === undefined) {
        return '-';
    }

    return new Intl.NumberFormat(locale, {
        style: 'currency',
        currency,
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    }).format(value);
}

/**
 * Formats a number with thousand separators
 */
export function formatNumber(
    value: number | null | undefined,
    decimals: number = 0,
    locale: string = 'es-PE'
): string {
    if (value === null || value === undefined) {
        return '-';
    }

    return new Intl.NumberFormat(locale, {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals,
    }).format(value);
}

/**
 * Formats a number as percentage
 */
export function formatPercentage(
    value: number | null | undefined,
    decimals: number = 1
): string {
    if (value === null || value === undefined) {
        return '-';
    }

    return `${value.toFixed(decimals)}%`;
}

/**
 * Formats a date to a readable string
 */
export function formatDate(
    date: Date | string | null | undefined,
    options?: Intl.DateTimeFormatOptions
): string {
    if (!date) {
        return '-';
    }

    const d = typeof date === 'string' ? new Date(date) : date;

    return d.toLocaleDateString('es-PE', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        ...options,
    });
}
