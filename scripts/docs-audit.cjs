#!/usr/bin/env node

/**
 * docs:audit - Auditoría de Documentación
 * Verifica integridad de la documentación del proyecto
 */

const fs = require('fs');
const path = require('path');

const DOCS_DIR = path.join(__dirname, '../docs');
const ROOT_DIR = path.join(__dirname, '..');
const INDEX_FILE = path.join(DOCS_DIR, '00_INDEX.md');

const EXPECTED_DOCS = [
    '00_INDEX.md',
    '01_ARQUITECTURA.md',
    '02_MODELO_NEGOCIO.md',
    '03_API_REFERENCE.md',
    '04_BASE_DATOS.md',
    '05_SEGURIDAD.md',
    '06_TESTING.md',
    '07_DEPLOY.md',
    '99_CHANGELOG.md'
];

const ROOT_DOCS = [
    'AGENT.md',
    'PROMPT_PRINCIPAL.md',
    'ROADMAP.md',
    'README.md'
];

let warnings = 0;
let errors = 0;

console.log('\n📚 GesNeu Documentation Audit\n');
console.log('='.repeat(50));

// Check /docs directory exists
if (!fs.existsSync(DOCS_DIR)) {
    console.error('❌ ERROR: /docs directory does not exist');
    process.exit(1);
}

// Check expected docs in /docs
console.log('\n📁 Checking /docs files...\n');
for (const doc of EXPECTED_DOCS) {
    const filePath = path.join(DOCS_DIR, doc);
    if (fs.existsSync(filePath)) {
        const stats = fs.statSync(filePath);
        const daysSinceModified = (Date.now() - stats.mtime.getTime()) / (1000 * 60 * 60 * 24);

        if (daysSinceModified > 90) {
            console.log(`⚠️  ${doc} - Last modified ${Math.floor(daysSinceModified)} days ago`);
            warnings++;
        } else {
            console.log(`✅ ${doc}`);
        }
    } else {
        console.log(`❌ ${doc} - MISSING`);
        errors++;
    }
}

// Check root docs
console.log('\n📄 Checking root documentation...\n');
for (const doc of ROOT_DOCS) {
    const filePath = path.join(ROOT_DIR, doc);
    if (fs.existsSync(filePath)) {
        console.log(`✅ ${doc}`);
    } else {
        console.log(`❌ ${doc} - MISSING`);
        errors++;
    }
}

// Summary
console.log('\n' + '='.repeat(50));
console.log('\n📊 Summary:\n');
console.log(`   ✅ Passed: ${EXPECTED_DOCS.length + ROOT_DOCS.length - errors - warnings}`);
console.log(`   ⚠️  Warnings: ${warnings}`);
console.log(`   ❌ Errors: ${errors}`);

if (errors > 0) {
    console.log('\n❌ Audit FAILED - Missing documentation files\n');
    process.exit(1);
} else if (warnings > 0) {
    console.log('\n⚠️  Audit PASSED with warnings\n');
    process.exit(0);
} else {
    console.log('\n✅ Audit PASSED\n');
    process.exit(0);
}
