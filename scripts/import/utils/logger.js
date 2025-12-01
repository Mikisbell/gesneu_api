const fs = require('fs');
const path = require('path');

class Logger {
    constructor(logDir = 'logs') {
        this.logDir = logDir;
        if (!fs.existsSync(logDir)) {
            fs.mkdirSync(logDir, { recursive: true });
        }

        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        this.logFile = path.join(logDir, `import-${timestamp}.log`);
        this.stats = {
            started: new Date(),
            phases: {},
            errors: [],
            warnings: []
        };
    }

    log(level, message, data = {}) {
        const entry = {
            timestamp: new Date().toISOString(),
            level,
            message,
            ...data
        };

        const logLine = `[${entry.timestamp}] [${level}] ${message}${Object.keys(data).length > 0 ? ' ' + JSON.stringify(data) : ''
            }\n`;

        fs.appendFileSync(this.logFile, logLine);

        // Console output con colores
        const color = {
            INFO: '\x1b[36m',    // Cyan
            SUCCESS: '\x1b[32m', // Green
            WARNING: '\x1b[33m', // Yellow
            ERROR: '\x1b[31m',   // Red
            RESET: '\x1b[0m'
        };

        console.log(`${color[level] || ''}${logLine.trim()}${color.RESET}`);
    }

    info(message, data) {
        this.log('INFO', message, data);
    }

    success(message, data) {
        this.log('SUCCESS', message, data);
    }

    warning(message, data) {
        this.log('WARNING', message, data);
        this.stats.warnings.push({ message, data });
    }

    error(message, error) {
        const errorData = {
            message: error?.message || error,
            stack: error?.stack
        };
        this.log('ERROR', message, errorData);
        this.stats.errors.push({ message, error: errorData });
    }

    startPhase(phaseName) {
        this.currentPhase = phaseName;
        this.stats.phases[phaseName] = {
            started: new Date(),
            processed: 0,
            inserted: 0,
            updated: 0,
            skipped: 0,
            failed: 0
        };
        this.info(`========== FASE: ${phaseName} ==========`);
    }

    endPhase() {
        if (this.currentPhase) {
            this.stats.phases[this.currentPhase].ended = new Date();
            const phase = this.stats.phases[this.currentPhase];
            const duration = (phase.ended - phase.started) / 1000;

            this.success(`Fase completada en ${duration}s`, {
                processed: phase.processed,
                inserted: phase.inserted,
                updated: phase.updated,
                skipped: phase.skipped,
                failed: phase.failed
            });
        }
    }

    incrementPhase(action) {
        if (this.currentPhase && this.stats.phases[this.currentPhase]) {
            this.stats.phases[this.currentPhase][action]++;
        }
    }

    getSummary() {
        const duration = (new Date() - this.stats.started) / 1000;
        return {
            duration,
            phases: this.stats.phases,
            totalErrors: this.stats.errors.length,
            totalWarnings: this.stats.warnings.length
        };
    }

    printSummary() {
        const summary = this.getSummary();
        console.log('\n' + '='.repeat(80));
        console.log('📊 RESUMEN DE IMPORTACIÓN');
        console.log('='.repeat(80));
        console.log(`Duración total: ${summary.duration.toFixed(2)}s`);
        console.log(`Errores: ${summary.totalErrors}`);
        console.log(`Advertencias: ${summary.totalWarnings}`);
        console.log('\nFases:');
        Object.entries(summary.phases).forEach(([name, data]) => {
            console.log(`  ${name}:`);
            console.log(`    Procesados: ${data.processed}`);
            console.log(`    Insertados: ${data.inserted}`);
            console.log(`    Actualizados: ${data.updated}`);
            console.log(`    Omitidos: ${data.skipped}`);
            console.log(`    Fallidos: ${data.failed}`);
        });
        console.log('='.repeat(80));
        console.log(`📝 Log completo: ${this.logFile}\n`);
    }
}

module.exports = Logger;
