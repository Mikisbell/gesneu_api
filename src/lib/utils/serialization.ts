export function safeSerialize(obj: any): any {
    if (obj === null || obj === undefined) {
        return obj;
    }

    if (typeof obj === 'bigint') {
        return obj.toString();
    }

    if (obj instanceof Date) {
        return obj.toISOString();
    }

    // Handle Prisma Decimal (which behaves like an object/string)
    if (typeof obj === 'object' && obj !== null) {
        // If it's a Decimal (has d, e, s properties usually, or check constructor name)
        // Easiest is to check if it has .toNumber() or .toFixed() but isn't a simple number
        if (typeof obj.toNumber === 'function') {
            return obj.toNumber();
        }

        if (Array.isArray(obj)) {
            return obj.map(safeSerialize);
        }

        const newObj: any = {};
        for (const key in obj) {
            if (Object.prototype.hasOwnProperty.call(obj, key)) {
                newObj[key] = safeSerialize(obj[key]);
            }
        }
        return newObj;
    }

    return obj;
}
