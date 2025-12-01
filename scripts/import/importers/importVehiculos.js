const ExcelParser = require('../utils/excelParser');
const prisma = require('../utils/prismaClient');
const config = require('../config');

class VehiculosImporter {
    constructor(logger) {
        this.logger = logger;
        this.parser = new ExcelParser(config.FILES.CONTROL_MANTENIMIENTO);
    }

    async import() {
        this.logger.startPhase('Vehículos');

        try {
            const vehiculos = await this.loadAndMapVehiculos();
            await this.insertVehiculos(vehiculos);

            this.logger.endPhase();
            return true;
        } catch (error) {
            this.logger.error('Error en Fase 2', error);
            throw error;
        }
    }

    async loadAndMapVehiculos() {
        this.logger.info('Cargando vehículos del Excel...');

        const data = this.parser.getSheetData(config.SHEETS.TABLAS);
        this.logger.info(`${data.length} vehículos encontrados`);

        const vehiculos = [];

        for (const row of data) {
            try {
                const vehiculo = await this.mapVehiculo(row);
                if (vehiculo) {
                    vehiculos.push(vehiculo);
                }
            } catch (error) {
                this.logger.warning(`Error mapeando vehículo ${row['COD EQUIPO']}`, { error: error.message });
            }
        }

        this.logger.info(`${vehiculos.length} vehículos mapeados correctamente`);
        return vehiculos;
    }

    async mapVehiculo(row) {
        const codigo = row['COD EQUIPO'];
        const placa = row['PLACA'];
        const descripcion = row['DESCRIPCION'];

        if (!codigo || !descripcion) {
            return null;
        }

        // Determinar tipo_medicion
        const tipo_medicion = this.derivarTipoMedicion(descripcion);

        // Buscar tipo de vehículo
        const tipoVehiculo = await prisma.tipoVehiculo.findUnique({
            where: { nombre: descripcion }
        });

        // Buscar centro de costo
        let centroCosto = null;
        if (row['COD_CECO']) {
            centroCosto = await prisma.centroCosto.findUnique({
                where: { codigo: String(row['COD_CECO']) }
            });
        }

        return {
            codigo_interno: codigo,
            placa: placa || null,
            marca: row['MARCA'] || null,
            modelo: row['MODELO'] || null,
            anio: row['AÑO'] ? parseInt(row['AÑO']) : null,
            numero_serie: row['Nº SERIE'] || null,
            tipo_medicion,
            contador_actual: 0,
            activo: true,
            tipo_vehiculo_id: tipoVehiculo?.id || null,
            centro_costo_id: centroCosto?.id || null
        };
    }

    derivarTipoMedicion(descripcion) {
        const desc = descripcion.toUpperCase();

        if (config.TIPOS_KILOMETRAJE.some(tipo => desc.includes(tipo))) {
            return 'KILOMETRAJE';
        }

        if (config.TIPOS_HOROMETRO.some(tipo => desc.includes(tipo))) {
            return 'HOROMETRO';
        }

        // Default a KILOMETRAJE
        this.logger.warning(`Tipo de medición no determinado para "${descripcion}", usando KILOMETRAJE`);
        return 'KILOMETRAJE';
    }

    async insertVehiculos(vehiculos) {
        this.logger.info(`Insertando ${vehiculos.length} vehículos...`);

        const batchSize = config.BATCH_SIZE;
        let inserted = 0;
        let updated = 0;
        let failed = 0;

        for (let i = 0; i < vehiculos.length; i += batchSize) {
            const batch = vehiculos.slice(i, i + batchSize);

            this.logger.info(`Procesando batch ${Math.floor(i / batchSize) + 1}/${Math.ceil(vehiculos.length / batchSize)}`);

            for (const vehiculo of batch) {
                try {
                    const existing = await prisma.vehiculo.findUnique({
                        where: { codigo_interno: vehiculo.codigo_interno }
                    });

                    if (existing) {
                        // Actualizar
                        await prisma.vehiculo.update({
                            where: { id: existing.id },
                            data: vehiculo
                        });
                        updated++;
                        this.logger.incrementPhase('updated');
                    } else {
                        // Insertar
                        await prisma.vehiculo.create({
                            data: vehiculo
                        });
                        inserted++;
                        this.logger.incrementPhase('inserted');
                    }

                    this.logger.incrementPhase('processed');
                } catch (error) {
                    this.logger.warning(`Error guardando vehículo ${vehiculo.codigo_interno}`, {
                        error: error.message
                    });
                    failed++;
                    this.logger.incrementPhase('failed');
                }
            }
        }

        this.logger.success(`✓ Vehículos: ${inserted} insertados, ${updated} actualizados, ${failed} fallidos`);
    }
}

module.exports = VehiculosImporter;
