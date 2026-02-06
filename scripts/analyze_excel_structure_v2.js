
const XLSX = require('xlsx');
const fs = require('fs');

const filename = 'CONTROL DE MANTENIMIENTO NEUMÁTICOS_Rev. A.xlsx';
console.log(`Loading file: ${filename}...`);
const workbook = XLSX.readFile(filename);

const sheetNames = workbook.SheetNames;
console.log(`\nTOTAL SHEETS FOUND: ${sheetNames.length}`);
console.log('SHEET LIST:');
sheetNames.forEach((name, idx) => console.log(` ${idx + 1}. ${name}`));

function scanSheet(sheetName) {
    console.log(`\n>>> ANALYZING SHEET: "${sheetName}" <<<`);
    const worksheet = workbook.Sheets[sheetName];
    // Get range to see dimensions
    const range = XLSX.utils.decode_range(worksheet['!ref']);
    console.log(`    Dimensions: Rows ${range.e.r + 1}, Cols ${range.e.c + 1}`);

    const data = XLSX.utils.sheet_to_json(worksheet, { header: 1, range: 0, defval: '' });

    console.log('--- First 10 Rows Sample ---');
    data.slice(0, 10).forEach((row, idx) => {
        const cleanRow = row.map(c => c ? String(c).trim() : '').filter(c => c !== '');
        if (cleanRow.length > 0) {
            console.log(`[Row ${idx}]:`, cleanRow.join(' | ').substring(0, 200) + (cleanRow.join(' | ').length > 200 ? '...' : ''));
        }
    });
}

sheetNames.forEach(name => scanSheet(name));
