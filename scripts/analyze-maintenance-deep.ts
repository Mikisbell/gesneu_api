
import * as XLSX from 'xlsx';
import * as fs from 'fs';
import * as path from 'path';

const filename = "CONTROL DE MANTENIMIENTO NEUMÁTICOS_Rev. A.xlsx";
const filePath = path.join(process.cwd(), filename);

if (!fs.existsSync(filePath)) {
    console.error(`❌ File not found: ${filename}`);
    process.exit(1);
}

console.log(`🔍 Deep Analyzing: ${filename}\n`);
const workbook = XLSX.readFile(filePath);

// 1. Analyze 'Tablas' (Master Inventory)
const masterSheetName = 'Tablas';
if (workbook.Sheets[masterSheetName]) {
    console.log(`\n============== HOJA MAESTRA: ${masterSheetName} ==============`);
    const sheet = workbook.Sheets[masterSheetName];
    // Master data usually starts at row 0 or 1. Let's look at first 20 rows to be safe? 
    // No, previous analysis showed headers at row 0.
    const data = XLSX.utils.sheet_to_json(sheet, { header: 1, defval: '' });

    // Print Headers
    const headers = data[0] as string[];
    console.log(`📍 Headers (${headers.length}):`);
    headers.forEach((h, i) => console.log(`   [${i}] ${h}`));

    console.log(`\n📍 Sample Data (First 3 Rows):`);
    data.slice(1, 4).forEach((row: any, i) => {
        console.log(`   Row ${i + 1}: ${JSON.stringify(row)}`);
    });
    console.log(`\n--------------------------------------------------------------`);
}

// 2. Analyze History Sheets
const historySheets = [
    'Neumaticos_Tractos',
    'Neumaticos_Remolques',
    'Neumaticos_Volquete',
    'Neumaticos_Linea Amarilla',
    'Neumaticos_Livianos'
];

historySheets.forEach(sheetName => {
    if (workbook.Sheets[sheetName]) {
        console.log(`\n============== HISTORIAL: ${sheetName} ==============`);
        const sheet = workbook.Sheets[sheetName];
        const rawData = XLSX.utils.sheet_to_json(sheet, { header: 1, defval: '', blankrows: false });

        // Find header row: Look for row containing "FECHA" or "PLACA" or "POSICION"
        let headerRowIndex = -1;

        for (let i = 0; i < Math.min(20, rawData.length); i++) {
            const row = rawData[i] as string[];
            const rowStr = row.join(' ').toUpperCase();
            if (rowStr.includes('FECHA') || rowStr.includes('POSICION') || rowStr.includes('MARCA') || rowStr.includes('KILOMETRAJE')) {
                headerRowIndex = i;
                break;
            }
        }

        if (headerRowIndex !== -1) {
            console.log(`✅ Header found at Row ${headerRowIndex + 1}:`);
            const headers = rawData[headerRowIndex] as any[];
            console.log(`   Columns: ${JSON.stringify(headers)}`);

            console.log(`\n📍 Sample History Data (Next 3 rows):`);
            rawData.slice(headerRowIndex + 1, headerRowIndex + 4).forEach((row: any, i) => {
                console.log(`   Entry ${i + 1}: ${JSON.stringify(row)}`);
            });
        } else {
            console.warn(`⚠️  Could not identify standard header row in first 20 lines. Printing first 5 non-empty lines:`);
            rawData.slice(0, 5).forEach((row: any, i) => {
                console.log(`   Line ${i + 1}: ${JSON.stringify(row)}`);
            });
        }
    }
});
