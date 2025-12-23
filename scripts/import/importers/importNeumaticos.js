const ExcelParser = require('../utils/excelParser');
const prisma = require('../utils/prismaClient');
const config = require('../config');
// const XLSX = require('xlsx'); // Removed
const path = require('path');

class NeumaticosImporter {
    constructor(logger) {
        this.logger = logger;
        this.parser = new ExcelParser(config.FILES.CONTROL_MANTENIMIENTO);
        this.vehiculosMap = new Map(); // Code -> ID
        this.modelosMap = new Map();   // Name -> ID
    }

    async import() {
// ... (omitted)
    async importSheet(sheetName) {
            try {
                const filePath = path.join(process.cwd(), config.DATA_DIR, config.FILES.NEUMATICOS);

                // Usar nueva instancia de parser para este archivo específico
                const sheetParser = new ExcelParser(filePath);
                const rawData = await sheetParser.getRawData(sheetName);

                if (!rawData || rawData.length === 0) {
                    this.logger.warn(`Hoja ${sheetName} no encontrada o vacía`);
                    return;
                }

                // const rawData = XLSX.utils.sheet_to_json(worksheet, { header: 1, defval: null }); // Replaced

                let currentVehicleId = null;
                let processedCount = 0;

                // Iterar filas
                for (let i = 0; i < rawData.length; i++) {
                    const row = rawData[i];
                    if (!row || row.length === 0) continue;

                    const firstCol = String(row[0] || '').trim();

                    // 1. Detectar Vehículo
                    if (this.vehiculosMap.has(firstCol)) {
                        currentVehicleId = this.vehiculosMap.get(firstCol);
                        continue;
                    }

                    // 2. Detectar Headers (ignorar)
                    if (firstCol === 'POSICION') continue;

                    // 3. Procesar Datos (si tenemos vehículo y parece una fila de datos)
                    // Asumimos fila de datos si empieza con P (P1, P2) o es numérico, Y tenemos vehículo
                    if (currentVehicleId && (firstCol.startsWith('P') || !isNaN(parseInt(firstCol)))) {
                        try {
                            // Bloque 1 (Actual)
                            await this.processBlock(row, 0, currentVehicleId, sheetName);

                            // Bloque 2 (Anterior) - Offset 9 columnas (aprox)
                            // Headers: POSICION(0), CODIGO(1), MARCA(2), MODELO(3), FECHA(4), MEDIDA(5), KM(6), HR(7), OT(8)
                            // Next Block: CODIGO(9)...
                            await this.processBlock(row, 9, currentVehicleId, sheetName, true);

                            processedCount++;
                            if (processedCount % 50 === 0) process.stdout.write('.');
                        } catch (error) {
                            // Silent catch to continue processing
                        }
                    }
                }

                console.log('');
                this.logger.success(`✓ ${processedCount} filas procesadas en ${sheetName}`);
            } catch (error) {
                this.logger.error(`Error procesando hoja ${sheetName}`, error);
            }
        }

    async processBlock(row, offset, vehicleId, sheetName, isPrevious = false) {
            // Indices relativos al offset
            // Block 1: POSICION(0), CODIGO(1), MARCA(2), MODELO(3), FECHA(4), MEDIDA(5), KM(6), HR(7), OT(8)
            // Block 2: CODIGO(0), MARCA(1), MODELO(2), FECHA(3), MEDIDA(4), KM(5), HR(6), OT(7) -> NO TIENE POSICION

            let codigo, marca, modeloNombre, fechaRaw, medida, km, hr, ot, posicion;

            if (offset === 0) {
                posicion = row[0];
                codigo = row[1];
                marca = row[2];
                modeloNombre = row[3];
                fechaRaw = row[4];
                medida = row[5];
                km = row[6];
                hr = row[7];
                ot = row[8];
            } else {
                // El segundo bloque empieza en col 9 (CODIGO)
                codigo = row[offset];
                marca = row[offset + 1];
                modeloNombre = row[offset + 2];
                fechaRaw = row[offset + 3];
                medida = row[offset + 4];
                km = row[offset + 5];
                hr = row[offset + 6];
                ot = row[offset + 7];
                posicion = row[0]; // Usamos la misma posición del bloque 1
            }

            if (!codigo) return;

            let fecha = this.parseExcelDate(fechaRaw);

            // Si es el bloque actual y no tiene fecha, asumimos que es una instalación vigente sin fecha registrada
            // Usamos una fecha por defecto antigua para no alterar estadísticas recientes, o la fecha actual
            if (!fecha && offset === 0) {
                fecha = new Date('2024-01-01'); // Fecha default para importación inicial sin fecha
            }

            // 1. Buscar o Crear Neumático
            let neumatico = await prisma.neumatico.findUnique({
                where: { numero_serie: String(codigo) }
            });

            if (!neumatico) {
                // Buscar modelo
                let modelo = null;
                if (modeloNombre) {
                    // Intentar match exacto o parcial
                    const searchName = String(modeloNombre).toUpperCase();
                    modelo = this.modelosMap.get(searchName);

                    if (!modelo) {
                        // Búsqueda laxa
                        for (const [name, m] of this.modelosMap) {
                            if (name.includes(searchName) || searchName.includes(name)) {
                                modelo = m;
                                break;
                            }
                        }
                    }
                }

                if (!modelo) modelo = this.defaultModelo;

                if (modelo) {
                    neumatico = await prisma.neumatico.create({
                        data: {
                            numero_serie: String(codigo),
                            modelo_id: modelo.id,
                            estado_actual: 'INSTALADO',
                            profundidad_inicial_mm: modelo.profundidad_inicial_mm,
                            vida_actual: 1,
                            kilometraje_acumulado: 0,
                            horas_acumuladas: 0,
                            costo_compra: 0,
                            fecha_compra: fecha || new Date(),
                            activo: true
                        }
                    });
                    this.logger.incrementPhase('inserted');
                }
            }

            if (!neumatico) return;

            // 2. Crear Evento
            if (fecha) {
                const existingEvent = await prisma.eventoNeumatico.findFirst({
                    where: {
                        neumatico_id: neumatico.id,
                        tipo_evento: 'INSTALACION',
                        fecha_evento: fecha
                    }
                });

                if (!existingEvent) {
                    await prisma.eventoNeumatico.create({
                        data: {
                            neumatico_id: neumatico.id,
                            vehiculo_id: vehicleId,
                            tipo_evento: 'INSTALACION',
                            fecha_evento: fecha,
                            contador_vehiculo: parseFloat(km) || parseFloat(hr) || 0,
                            notas: `Importado de ${sheetName}. Pos: ${posicion}. ${isPrevious ? '(Histórico)' : ''}`,
                            creado_en: fecha
                        }
                    });

                    // Actualizar ubicación solo si es el evento más reciente (simplificado: siempre actualizamos si es bloque 1)
                    if (!isPrevious) {
                        await prisma.neumatico.update({
                            where: { id: neumatico.id },
                            data: {
                                ubicacion_vehiculo_id: vehicleId,
                                estado_actual: 'INSTALADO'
                            }
                        });
                    }

                    this.logger.incrementPhase('updated');
                }
            }
        }

        parseExcelDate(excelDate) {
            if (!excelDate) return null;
            if (excelDate instanceof Date) return excelDate;
            if (typeof excelDate === 'number') {
                return new Date(Math.round((excelDate - 25569) * 86400 * 1000));
            }
            const date = new Date(excelDate);
            return isNaN(date.getTime()) ? null : date;
        }
    }

module.exports = NeumaticosImporter;
