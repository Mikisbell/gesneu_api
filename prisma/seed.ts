import 'dotenv/config'
import { prisma } from '../src/lib/prisma';
import { TipoMedicionEnum, TipoEventoNeumaticoEnum, EstadoNeumaticoEnum } from '@prisma/client';

async function main() {
    console.log('🌱 Iniciando carga de datos reales ECOSEM...');

    // 1. Centros de Costo (Tablas.csv)
    const cecoTransporte = await prisma.centroCosto.upsert({
        where: { codigo: '650101' },
        update: {},
        create: { codigo: '650101', nombre: 'TRANSPORTE COMERCIAL Y DE MERCANCIAS', area_negocio: 'TRANSPORTE COMERCIAL' }
    });

    const cecoTaller = await prisma.centroCosto.upsert({
        where: { codigo: '640304' },
        update: {},
        create: { codigo: '640304', nombre: 'TALLER TRANSPORTES', area_negocio: 'MANTENIMIENTO' }
    });

    // 2. Tipos de Vehículo
    const tipoTracto = await prisma.tipoVehiculo.upsert({
        where: { nombre: 'TRACTO 6X4' },
        update: {},
        create: { nombre: 'TRACTO 6X4', descripcion: 'Tracto camión Volvo/Scania' }
    });

    const tipoVolquete = await prisma.tipoVehiculo.upsert({
        where: { nombre: 'VOLQUETE' },
        update: {},
        create: { nombre: 'VOLQUETE', descripcion: 'Volquete Volvo FMX' }
    });

    const tipoCargador = await prisma.tipoVehiculo.upsert({
        where: { nombre: 'CARGADOR FRONTAL' },
        update: {},
        create: { nombre: 'CARGADOR FRONTAL', descripcion: 'Caterpillar 966' }
    });

    // 3. Vehículos Reales (Tablas.csv)

    // TC-100: Línea Blanca (Km)
    await prisma.vehiculo.upsert({
        where: { codigo_interno: 'TC-100' },
        update: {},
        create: {
            codigo_interno: 'TC-100',
            placa: 'F8U-901',
            tipo_vehiculo_id: tipoTracto.id,
            marca: 'VOLVO',
            modelo: 'FH 440 6X4T',
            anio: 2014,
            tipo_medicion: TipoMedicionEnum.KILOMETRAJE,
            contador_actual: 672491.5,
            centro_costo_id: cecoTransporte.id
        }
    });

    // VQ-32: Volquete (Km)
    await prisma.vehiculo.upsert({
        where: { codigo_interno: 'VQ-32' },
        update: {},
        create: {
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

    // CF-01: Cargador Frontal (Horas)
    await prisma.vehiculo.upsert({
        where: { codigo_interno: 'CF-01' },
        update: {},
        create: {
            codigo_interno: 'CF-01',
            placa: null,
            numero_serie: 'FRS02106',
            tipo_vehiculo_id: tipoCargador.id,
            marca: 'CATERPILLAR',
            modelo: '966 L',
            anio: 2020,
            tipo_medicion: TipoMedicionEnum.HOROMETRO,
            contador_actual: 16094.0,
            centro_costo_id: cecoTaller.id
        }
    });

    // 4. Fabricantes y Modelos
    const fabGoodyear = await prisma.fabricanteNeumatico.upsert({
        where: { nombre: 'GOODYEAR' },
        update: {},
        create: { nombre: 'GOODYEAR' }
    });

    const fabAeolus = await prisma.fabricanteNeumatico.upsert({
        where: { nombre: 'AEOLUS' },
        update: {},
        create: { nombre: 'AEOLUS' }
    });

    // Modelos de neumáticos (usando nombre como identificador único temporal)
    const modKmaxS = await prisma.modeloNeumatico.upsert({
        where: { id: '00000000-0000-0000-0000-000000000001' },
        update: {},
        create: {
            id: '00000000-0000-0000-0000-000000000001',
            nombre: 'KMAX S',
            medida: '295/80R22.5',
            profundidad_inicial_mm: 15.8,
            fabricante_id: fabGoodyear.id
        }
    });

    const modOmnitrac = await prisma.modeloNeumatico.upsert({
        where: { id: '00000000-0000-0000-0000-000000000002' },
        update: {},
        create: {
            id: '00000000-0000-0000-0000-000000000002',
            nombre: 'OMNITRAC S',
            medida: '325/95R24',
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
