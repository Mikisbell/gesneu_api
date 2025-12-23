const ExcelJS = require('exceljs');

class ExcelParser {
    constructor(filePath) {
        this.filePath = filePath;
        this.workbook = new ExcelJS.Workbook();
        this.isLoaded = false;
    }

    async init() {
        if (!this.isLoaded) {
            await this.workbook.xlsx.readFile(this.filePath);
            this.isLoaded = true;
        }
    }

    getSheetNames() {
        return this.workbook.worksheets.map(ws => ws.name);
    }

    async getSheetData(sheetName, options = {}) {
        await this.init();
        const worksheet = this.workbook.getWorksheet(sheetName);
        if (!worksheet) {
            throw new Error(`Sheet "${sheetName}" not found in ${this.filePath}`);
        }

        const data = [];
        const headerRowIndex = options.headerRow || 1;

        let headers = [];
        if (!options.header || options.header === true) {
            // Asumir fila 1 como headers
            const headerRow = worksheet.getRow(headerRowIndex);
            headerRow.eachCell((cell, colNumber) => {
                headers[colNumber] = cell.value;
            });
        }

        worksheet.eachRow((row, rowNumber) => {
            if (rowNumber <= headerRowIndex) return; // Skip header

            const rowData = {};
            row.eachCell({ includeEmpty: true }, (cell, colNumber) => {
                const header = headers[colNumber];
                if (header) {
                    rowData[header] = cell.value;
                }
            });
            data.push(rowData);
        });

        return data;
    }

    /**
     * Obtiene valores únicos de una columna
     */
    async getUniqueValues(sheetName, columnName) {
        const data = await this.getSheetData(sheetName);
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
     * Obtiene datos crudos como array de arrays (equivalente a header: 1)
     */
    async getRawData(sheetName) {
        await this.init();
        const worksheet = this.workbook.getWorksheet(sheetName);
        if (!worksheet) {
            // Retorna array vacío si no existe la hoja
            return [];
        }

        const data = [];
        worksheet.eachRow((row, rowNumber) => {
            // ExcelJS values array starts at index 1, slice to get 0-indexed array
            // row.values returns [undefined, val1, val2, ...]
            const rowValues = row.values;
            if (Array.isArray(rowValues)) {
                // Eliminar el primer elemento vacío que pone exceljs
                data.push(rowValues.slice(1));
            }
        });
        return data;
    }

    /**
     * Agrupa datos por una columna
     */
    async groupBy(sheetName, columnName) {
        const data = await this.getSheetData(sheetName);
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
