import 'dotenv/config'
import { prisma } from '../src/lib/prisma';
import { TipoMedicionEnum, TipoEventoNeumaticoEnum, EstadoNeumaticoEnum } from '@prisma/client';

async function main() {
    console.log('🌱 Iniciando carga de datos reales ECOSEM...');

    // 1. Centros de Costo (Tablas.csv)
    const cecoTransporte = await prisma.centroCosto.create({
        data: { codigo: '650101', nombre: 'TRANSPORTE COMERCIAL Y DE MERCANCIAS', area_negocio: 'TRANSPORTE COMERCIAL' }
    });

    const cecoTaller = await prisma.centroCosto.create({
        data: { codigo: '640304', nombre: 'TALLER TRANSPORTES', area_negocio: 'MANTENIMIENTO' }
    });

    // 2. Tipos de Vehículo
    const tipoTracto = await prisma.tipoVehiculo.create({
        data: { nombre: 'TRACTO 6X4', descripcion: 'Tracto camión Volvo/Scania', activo: true }
    });

    const tipoVolquete = await prisma.tipoVehiculo.create({
        data: { nombre: 'VOLQUETE', descripcion: 'Volquete Volvo FMX', activo: true }
    });

    const tipoCargador = await prisma.tipoVehiculo.create({
        data: { nombre: 'CARGADOR FRONTAL', descripcion: 'Caterpillar 966', activo: true }
    });

    // 3. Vehículos Reales (Tablas.csv)

    // TC-100: Línea Blanca (Km)
    await prisma.vehiculo.create({
        data: {
            codigo_interno: 'TC-100',
            placa: 'F8U-901',
            tipo_vehiculo_id: tipoTracto.id,
            marca: 'VOLVO',
            modelo: 'FH 440 6X4T',
            anio: 2014,
            tipo_medicion: TipoMedicionEnum.KILOMETRAJE,
            contador_actual: 672491.5, // Dato real de tu CSV
            centro_costo_id: cecoTransporte.id
        }
    });

    // VQ-32: Volquete (Km) - Línea Amarilla/Construcción
    await prisma.vehiculo.create({
        data: {
            codigo_interno: 'VQ-32',
            placa: 'ATW-862',
            tipo_vehiculo_id: tipoVolquete.id,
            marca: 'VOLVO',
            modelo: 'FMX 6X4 R',
            anio: 2017,
            tipo_medicion: TipoMedicionEnum.KILOMETRAJE,
            contador_actual: 55246.7,
            centro_costo_id: cecoTaller.id
        }
    });

    // CF-01: Cargador Frontal (Horas) 🚜
    await prisma.vehiculo.create({
        data: {
            codigo_interno: 'CF-01',
            placa: null, // Maquinaria a veces no usa placa
            numero_serie: 'FRS02106',
            tipo_vehiculo_id: tipoCargador.id,
            marca: 'CATERPILLAR',
            modelo: '966 L',
            anio: 2020,
            tipo_medicion: TipoMedicionEnum.HOROMETRO, // 🚨 ¡Clave!
            contador_actual: 16094.0, // Horas, no Km
            centro_costo_id: cecoTaller.id
        }
    });

    // 4. Fabricantes y Modelos (Neumaticos_Tractos.csv)
    const fabGoodyear = await prisma.fabricanteNeumatico.create({ data: { nombre: 'GOODYEAR' } });
    const fabAeolus = await prisma.fabricanteNeumatico.create({ data: { nombre: 'AEOLUS' } });

    // Modelo Línea Blanca
    const modKmaxS = await prisma.modeloNeumatico.create({
        data: {
            nombre: 'KMAX S',
            medida: '295/80R22.5',
            profundidad_inicial_mm: 15.8, // Dato real (NSK Original)
            fabricante_id: fabGoodyear.id
        }
    });

    // Modelo Línea Amarilla (OTR)
    const modOmnitrac = await prisma.modeloNeumatico.create({
        data: {
            nombre: 'OMNITRAC S',
            medida: '325/95R24', // Medida de volquete
            profundidad_inicial_mm: 20.0,
            fabricante_id: fabGoodyear.id
        }
    });

    console.log('✅ Datos reales de ECOSEM cargados exitosamente.');
}

main()
    .catch((e) => {
        console.error(e);
        process.exit(1);
    })
    .finally(async () => {
        await prisma.$disconnect();
    });
