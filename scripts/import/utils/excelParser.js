const XLSX = require('xlsx');

class ExcelParser {
    constructor(filePath) {
        this.filePath = filePath;
        this.workbook = XLSX.readFile(filePath);
    }

    getSheetNames() {
        return this.workbook.SheetNames;
    }

    getSheetData(sheetName, options = {}) {
        const worksheet = this.workbook.Sheets[sheetName];
        if (!worksheet) {
            throw new Error(`Sheet "${sheetName}" not found in ${this.filePath}`);
        }

        // Por defecto, convertir a JSON con headers
        const data = XLSX.utils.sheet_to_json(worksheet, {
            raw: false, // Convertir fechas a strings
            defval: null, // Valores por defecto para celdas vacías
            ...options
        });

        return data;
    }

    /**
     * Obtiene valores únicos de una columna
     */
    getUniqueValues(sheetName, columnName) {
        const data = this.getSheetData(sheetName);
        const values = new Set();

        data.forEach(row => {
            const value = row[columnName];
            if (value !== null && value !== undefined && value !== '') {
                values.add(value);
            }
        });

        return Array.from(values);
    }

    /**
     * Agrupa datos por una columna
     */
    groupBy(sheetName, columnName) {
        const data = this.getSheetData(sheetName);
        const grouped = {};

        data.forEach(row => {
            const key = row[columnName];
            if (!grouped[key]) {
                grouped[key] = [];
            }
            grouped[key].push(row);
        });

        return grouped;
    }
}

module.exports = ExcelParser;
