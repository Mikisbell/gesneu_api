
const XLSX = require('xlsx');
const fs = require('fs');

const filename = 'Data Inspección SOLTRAK - Abr24 ECOSEM.xlsx';

if (!fs.existsSync(filename)) {
    console.error(`File ${filename} not found!`);
    process.exit(1);
}

const workbook = XLSX.readFile(filename);
const sheetNames = workbook.SheetNames;

console.log(`Analyzing ${filename}`);
console.log(`Found ${sheetNames.length} sheets: ${sheetNames.join(', ')}`);
console.log('---------------------------------------------------');

sheetNames.forEach(sheetName => {
    console.log(`\nSHEET: "${sheetName}"`);
    const worksheet = workbook.Sheets[sheetName];
    // Convert to JSON (header: 1 means array of arrays, header: A means object with properties)
    // Let's use array of arrays to spy the first row (headers) and first data row
    const data = XLSX.utils.sheet_to_json(worksheet, { header: 1, range: 0, defval: null });

    if (data.length > 0) {
        console.log(`HEADERS (${data[0].length}):`, data[0]);
        if (data.length > 1) {
            console.log('SAMPLE ROW 1:', data[1]);
        }
    } else {
        console.log('Sheet is empty');
    }
    console.log('---------------------------------------------------');
});
