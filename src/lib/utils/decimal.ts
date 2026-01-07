/**
 * Utilidades para conversión segura de tipos Prisma Decimal a number
 * 
 * Prisma devuelve Decimal para campos numéricos de precisión,
 * pero muchos componentes React esperan number primitivo.
 */

/**
 * Convierte un valor Decimal, number o null/undefined a number
 * @param val - Valor a convertir (puede ser Prisma Decimal, number, null o undefined)
 * @param defaultValue - Valor por defecto si es null/undefined (default: 0)
 * @returns number primitivo
 */
export function toNumber(
    val: { toNumber(): number } | number | null | undefined,
    defaultValue: number = 0
): number {
    if (val === null || val === undefined) return defaultValue;
    if (typeof val === 'number') return val;
    // Prisma Decimal tiene método toNumber()
    if (typeof val === 'object' && 'toNumber' in val && typeof val.toNumber === 'function') {
        return val.toNumber();
    }
    return defaultValue;
}

/**
 * Formatea un Decimal como string con precisión fija
 * @param val - Valor Decimal
 * @param decimals - Cantidad de decimales (default: 2)
 * @returns String formateado
 */
export function formatDecimal(
    val: { toNumber(): number } | number | null | undefined,
    decimals: number = 2
): string {
    const num = toNumber(val);
    return num.toFixed(decimals);
}

/**
 * Compara dos valores numéricos (soporta Decimal y number)
 */
export function compareNumbers(
    a: { toNumber(): number } | number | null | undefined,
    b: { toNumber(): number } | number | null | undefined
): number {
    return toNumber(a) - toNumber(b);
}
