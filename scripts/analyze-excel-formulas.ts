
import * as XLSX from 'xlsx';
import * as fs from 'fs';
import * as path from 'path';

const filename = "CONTROL DE MANTENIMIENTO NEUMÁTICOS_Rev. A.xlsx";
const filePath = path.join(process.cwd(), filename);

if (!fs.existsSync(filePath)) {
    console.error(`❌ File not found: ${filename}`);
    process.exit(1);
}

console.log(`🧠 Forensic Analysis of: ${filename}\n`);
// Read with cellFormula: true to get formulas
const workbook = XLSX.readFile(filePath, { cellFormula: true, cellStyles: true });

function analyzeSheetLogic(sheetName: string) {
    if (!workbook.Sheets[sheetName]) return;
    const sheet = workbook.Sheets[sheetName];
    console.log(`\n============== LOGIC ANALYSIS: ${sheetName} ==============`);

    // 1. Detect Formulas
    const formulas: string[] = [];
    Object.keys(sheet).forEach(cellKey => {
        if (cellKey.startsWith('!')) return;
        const cell = sheet[cellKey];
        if (cell.f) {
            formulas.push(`${cellKey} = ${cell.f}`);
        }
    });

    if (formulas.length > 0) {
        console.log(`🧮 Formulas Detected (${formulas.length}):`);
        // Show unique formula patterns (simplified)
        const uniquePatterns = [...new Set(formulas.map(f => f.split('=')[1].replace(/\d+/g, 'N')))].slice(0, 10);
        uniquePatterns.forEach(p => console.log(`   Pattern: ${p}`));
        // Show first 5 raw examples
        formulas.slice(0, 5).forEach(f => console.log(`   Example: ${f}`));
    } else {
        console.log(`   (No formulas found - Static Data?)`);
    }

    // 2. Detect Metadata / Key-Value Pairs (common in Index/Summary sheets)
    const range = XLSX.utils.decode_range(sheet['!ref'] || 'A1:A1');
    if (range.e.r < 20) { // Small sheet? Likely config
        console.log(`   (Small Sheet - Potential Configuration/Metadata)`);
        const json = XLSX.utils.sheet_to_json(sheet, { header: 1 });
        console.log(JSON.stringify(json, null, 2));
    }
}

// Analyze specific "System" sheets
const systemSheets = [
    'Índice_Reencauche',
    'Índice_Scrap',
    'Tablas',
    'Neumaticos_Tractos'
];

systemSheets.forEach(analyzeSheetLogic);
