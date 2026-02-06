
const XLSX = require('xlsx');
const path = require('path');

const filePath = path.resolve(process.cwd(), 'CONTROL DE MANTENIMIENTO NEUMÁTICOS_Rev. A.xlsx');
const workbook = XLSX.readFile(filePath);

const sheetName = workbook.SheetNames.find(n => n.toUpperCase().includes('TRACTOS'));
const sheet = workbook.Sheets[sheetName];
const data = XLSX.utils.sheet_to_json(sheet, { header: 1 });

console.log(`--- Cabeceras de ${sheetName} ---`);
// Print rows 5 to 25 to see where data starts
data.slice(5, 25).forEach((row, i) => {
    console.log(`Row ${i + 5}:`, row);
});
