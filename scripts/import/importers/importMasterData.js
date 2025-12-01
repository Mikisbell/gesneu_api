const ExcelParser = require('../utils/excelParser');
const prisma = require('../utils/prismaClient');
const config = require('../config');

class MasterDataImporter {
    constructor(logger) {
        this.logger = logger;
        this.parser = new ExcelParser(config.FILES.CONTROL_MANTENIMIENTO);
    }

    async import() {
        this.logger.startPhase('Datos Maestros');

        try {
            await this.importCentrosCosto();
            await this.importFabricantes();
            await this.importTiposVehiculo();
            await this.importModelosNeumatico();
            await this.importAlmacenes();

            this.logger.endPhase();
            return true;
        } catch (error) {
            this.logger.error('Error en Fase 1', error);
            throw error;
        }
    }

    async importCentrosCosto() {
        this.logger.info('Importando Centros de Costo...');

        const data = this.parser.getSheetData(config.SHEETS.TABLAS);
        const centrosCostoMap = new Map();

        // Extraer centros de costo únicos
        data.forEach(row => {
            const codigo = row['COD_CECO'];
            const nombre = row['CENTRO DE COSTO'];
            const area = row['AREA'];

            if (codigo && nombre) {
                centrosCostoMap.set(codigo, { codigo, nombre, area_negocio: area });
            }
        });

        this.logger.info(`Encontrados ${centrosCostoMap.size} centros de costo únicos`);

        for (const [codigo, data] of centrosCostoMap) {
            try {
                await prisma.centroCosto.upsert({
                    where: { codigo: String(codigo) },
                    create: {
                        codigo: String(codigo),
                        nombre: data.nombre,
                        area_negocio: data.area_negocio || null
                    },
                    update: {
                        nombre: data.nombre,
                        area_negocio: data.area_negocio || null
                    }
                });

                this.logger.incrementPhase('inserted');
            } catch (error) {
                this.logger.warning(`Error importando centro de costo ${codigo}`, { error: error.message });
                this.logger.incrementPhase('failed');
            }
        }

        this.logger.success(`✓ ${centrosCostoMap.size} centros de costo procesados`);
    }

    async importFabricantes() {
        this.logger.info('Importando Fabricantes de Neumáticos...');

        const fabricantes = this.parser.getUniqueValues(config.SHEETS.TABLAS, 'MARACA'); // typo en Excel
        this.logger.info(`Encontrados ${fabricantes.length} fabricantes únicos`);

        for (const nombre of fabricantes) {
            if (!nombre) continue;

            try {
                await prisma.fabricanteNeumatico.upsert({
                    where: { nombre },
                    create: { nombre },
                    update: {}
                });

                this.logger.incrementPhase('inserted');
            } catch (error) {
                this.logger.warning(`Error importando fabricante ${nombre}`, { error: error.message });
                this.logger.incrementPhase('failed');
            }
        }

        this.logger.success(`✓ ${fabricantes.length} fabricantes procesados`);
    }

    async importTiposVehiculo() {
        this.logger.info('Importando Tipos de Vehículo...');

        const descripciones = this.parser.getUniqueValues(config.SHEETS.TABLAS, 'DESCRIPCION');
        this.logger.info(`Encontrados ${descripciones.length} tipos únicos`);

        for (const nombre of descripciones) {
            if (!nombre) continue;

            try {
                await prisma.tipoVehiculo.upsert({
                    where: { nombre },
                    create: { nombre },
                    update: {}
                });

                this.logger.incrementPhase('inserted');
            } catch (error) {
                this.logger.warning(`Error importando tipo vehículo ${nombre}`, { error: error.message });
                this.logger.incrementPhase('failed');
            }
        }

        this.logger.success(`✓ ${descripciones.length} tipos de vehículo procesados`);
    }

    async importModelosNeumatico() {
        this.logger.info('Importando Modelos de Neumáticos...');

        const data = this.parser.getSheetData(config.SHEETS.TABLAS);
        const modelosMap = new Map();

        data.forEach(row => {
            const medida = row['MEDIDA'];
            const diseno = row['DISEÑO'];
            const fabricante = row['MARACA'];
            const nsk = row['NSK'];
            const nskReen = row['NSK Reen'];

            if (medida && fabricante) {
                const key = `${medida}-${diseno || 'STD'}`;
                modelosMap.set(key, {
                    nombre: diseno ? `${medida} ${diseno}` : medida,
                    medida,
                    profundidad_inicial_mm: nsk || 20,
                    reencauches_maximos: nskReen || 0,
                    fabricante
                });
            }
        });

        this.logger.info(`Encontrados ${modelosMap.size} modelos únicos`);

        for (const [key, modelo] of modelosMap) {
            try {
                // Buscar fabricante
                const fabricante = await prisma.fabricanteNeumatico.findUnique({
                    where: { nombre: modelo.fabricante }
                });

                if (!fabricante) {
                    this.logger.warning(`Fabricante no encontrado: ${modelo.fabricante}`);
                    this.logger.incrementPhase('failed');
                    continue;
                }

                // Buscar modelo existente
                const existing = await prisma.modeloNeumatico.findFirst({
                    where: {
                        nombre: modelo.nombre,
                        medida: modelo.medida,
                        fabricante_id: fabricante.id
                    }
                });

                if (existing) {
                    // Actualizar
                    await prisma.modeloNeumatico.update({
                        where: { id: existing.id },
                        data: {
                            profundidad_inicial_mm: parseFloat(modelo.profundidad_inicial_mm),
                            reencauches_maximos: parseInt(modelo.reencauches_maximos)
                        }
                    });
                    this.logger.incrementPhase('updated');
                } else {
                    // Crear nuevo
                    await prisma.modeloNeumatico.create({
                        data: {
                            nombre: modelo.nombre,
                            medida: modelo.medida,
                            profundidad_inicial_mm: parseFloat(modelo.profundidad_inicial_mm),
                            reencauches_maximos: parseInt(modelo.reencauches_maximos),
                            fabricante_id: fabricante.id
                        }
                    });
                    this.logger.incrementPhase('inserted');
                }
            } catch (error) {
                this.logger.warning(`Error importando modelo ${modelo.nombre}`, { error: error.message });
                this.logger.incrementPhase('failed');
            }
        }

        this.logger.success(`✓ ${modelosMap.size} modelos procesados`);
    }

    async importAlmacenes() {
        this.logger.info('Creando Almacenes por defecto...');

        for (const almacen of config.DEFAULT_ALMACENES) {
            try {
                const existing = await prisma.almacen.findFirst({
                    where: { nombre: almacen.nombre }
                });

                if (existing) {
                    await prisma.almacen.update({
                        where: { id: existing.id },
                        data: {} // No actualizamos nada por ahora
                    });
                    this.logger.incrementPhase('updated');
                } else {
                    await prisma.almacen.create({
                        data: {
                            nombre: almacen.nombre,
                            tipo: almacen.tipo,
                            ubicacion: almacen.ubicacion
                        }
                    });
                    this.logger.incrementPhase('inserted');
                }
            } catch (error) {
                this.logger.warning(`Error creando almacén ${almacen.nombre}`, { error: error.message });
                this.logger.incrementPhase('failed');
            }
        }

        this.logger.success(`✓ ${config.DEFAULT_ALMACENES.length} almacenes creados`);
    }
}

module.exports = MasterDataImporter;
