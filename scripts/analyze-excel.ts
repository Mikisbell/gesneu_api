
import * as XLSX from 'xlsx';
import * as fs from 'fs';
import * as path from 'path';

const files = [
    "Data Inspección SOLTRAK - Abr24 ECOSEM.xlsx",
    "CONTROL DE MANTENIMIENTO NEUMÁTICOS_Rev. A.xlsx"
];

files.forEach(filename => {
    const filePath = path.join(process.cwd(), filename);
    if (!fs.existsSync(filePath)) {
        console.error(`❌ File not found: ${filename}`);
        return;
    }

    console.log(`\n📂 Analyzing: ${filename}`);
    const workbook = XLSX.readFile(filePath);

    workbook.SheetNames.forEach(sheetName => {
        console.log(`   📄 Sheet: ${sheetName}`);
        const worksheet = workbook.Sheets[sheetName];
        const data = XLSX.utils.sheet_to_json(worksheet, { header: 1, defval: '' });

        // Print header and first 2 rows
        const preview = data.slice(0, 3);
        console.log(JSON.stringify(preview, null, 2));
    });
});
