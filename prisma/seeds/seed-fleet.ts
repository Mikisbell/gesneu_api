
import { PrismaClient, TipoEjeEnum, LadoVehiculoEnum, TipoMedicionEnum } from '@prisma/client';

export async function seedFleet(
    prisma: PrismaClient,
    empresaId: string,
    cecoTransporteId: string,
    cecoMinasId: string
) {
    console.log('🚛 Seeding Fleet (Vehicles & Axle Configs)...');

    // --- 1. TIPO TRACTO 6X4 (Existente) ---
    const tipoTracto = await prisma.tipoVehiculo.upsert({ where: { nombre: 'TRACTO 6X4' }, update: {}, create: { nombre: 'TRACTO 6X4', descripcion: 'Tracto camión Volvo/Scania' } });

    // Configurar Ejes Tracto (si no existen)
    if (await prisma.configuracionEje.count({ where: { tipo_vehiculo_id: tipoTracto.id } }) === 0) {
        // Eje 1: Direccional (2 posiciones)
        const eje1 = await prisma.configuracionEje.create({
            data: { tipo_vehiculo_id: tipoTracto.id, numero_eje: 1, tipo_eje: TipoEjeEnum.DIRECCION, nombre_eje: 'Direccional', numero_posiciones: 2, permite_reencauchados: false }
        });
        await prisma.posicionNeumatico.create({ data: { configuracion_eje_id: eje1.id, codigo_posicion: '1I', lado: LadoVehiculoEnum.IZQUIERDO, posicion_relativa: 1, es_direccion: true } });
        await prisma.posicionNeumatico.create({ data: { configuracion_eje_id: eje1.id, codigo_posicion: '1D', lado: LadoVehiculoEnum.DERECHO, posicion_relativa: 1, es_direccion: true } });

        // Eje 2: Tracción (4 posiciones)
        const eje2 = await prisma.configuracionEje.create({
            data: { tipo_vehiculo_id: tipoTracto.id, numero_eje: 2, tipo_eje: TipoEjeEnum.TRACCION, nombre_eje: 'Tracción 1', numero_posiciones: 4, posiciones_duales: true }
        });
        await prisma.posicionNeumatico.create({ data: { configuracion_eje_id: eje2.id, codigo_posicion: '2EI', lado: LadoVehiculoEnum.IZQUIERDO, posicion_relativa: 1, es_traccion: true, es_interna: true } });
        await prisma.posicionNeumatico.create({ data: { configuracion_eje_id: eje2.id, codigo_posicion: '2EE', lado: LadoVehiculoEnum.IZQUIERDO, posicion_relativa: 1, es_traccion: true } });
        await prisma.posicionNeumatico.create({ data: { configuracion_eje_id: eje2.id, codigo_posicion: '2DI', lado: LadoVehiculoEnum.DERECHO, posicion_relativa: 1, es_traccion: true, es_interna: true } });
        await prisma.posicionNeumatico.create({ data: { configuracion_eje_id: eje2.id, codigo_posicion: '2DE', lado: LadoVehiculoEnum.DERECHO, posicion_relativa: 1, es_traccion: true } });

        // Eje 3: Tracción (4 posiciones)
        const eje3 = await prisma.configuracionEje.create({
            data: { tipo_vehiculo_id: tipoTracto.id, numero_eje: 3, tipo_eje: TipoEjeEnum.TRACCION, nombre_eje: 'Tracción 2', numero_posiciones: 4, posiciones_duales: true }
        });
        await prisma.posicionNeumatico.create({ data: { configuracion_eje_id: eje3.id, codigo_posicion: '3EI', lado: LadoVehiculoEnum.IZQUIERDO, posicion_relativa: 1, es_traccion: true, es_interna: true } });
        await prisma.posicionNeumatico.create({ data: { configuracion_eje_id: eje3.id, codigo_posicion: '3EE', lado: LadoVehiculoEnum.IZQUIERDO, posicion_relativa: 1, es_traccion: true } });
        await prisma.posicionNeumatico.create({ data: { configuracion_eje_id: eje3.id, codigo_posicion: '3DI', lado: LadoVehiculoEnum.DERECHO, posicion_relativa: 1, es_traccion: true, es_interna: true } });
        await prisma.posicionNeumatico.create({ data: { configuracion_eje_id: eje3.id, codigo_posicion: '3DE', lado: LadoVehiculoEnum.DERECHO, posicion_relativa: 1, es_traccion: true } });
    }

    // --- 2. TIPO VOLQUETE 8X4 (Nuevo) ---
    const tipoVolquete = await prisma.tipoVehiculo.upsert({ where: { nombre: 'VOLQUETE 8X4' }, update: {}, create: { nombre: 'VOLQUETE 8X4', descripcion: 'Volquete Minero Scania P410' } });

    if (await prisma.configuracionEje.count({ where: { tipo_vehiculo_id: tipoVolquete.id } }) === 0) {
        // Ejes 1 y 2: Direccionales (2 pos c/u)
        for (let i = 1; i <= 2; i++) {
            const eje = await prisma.configuracionEje.create({
                data: { tipo_vehiculo_id: tipoVolquete.id, numero_eje: i, tipo_eje: TipoEjeEnum.DIRECCION, nombre_eje: `Direccional ${i}`, numero_posiciones: 2, permite_reencauchados: false }
            });
            await prisma.posicionNeumatico.create({ data: { configuracion_eje_id: eje.id, codigo_posicion: `${i}I`, lado: LadoVehiculoEnum.IZQUIERDO, posicion_relativa: 1, es_direccion: true } });
            await prisma.posicionNeumatico.create({ data: { configuracion_eje_id: eje.id, codigo_posicion: `${i}D`, lado: LadoVehiculoEnum.DERECHO, posicion_relativa: 1, es_direccion: true } });
        }
        // Ejes 3 y 4: Tracción (4 pos c/u)
        for (let i = 3; i <= 4; i++) {
            const eje = await prisma.configuracionEje.create({
                data: { tipo_vehiculo_id: tipoVolquete.id, numero_eje: i, tipo_eje: TipoEjeEnum.TRACCION, nombre_eje: `Tracción ${i - 2}`, numero_posiciones: 4, posiciones_duales: true }
            });
            await prisma.posicionNeumatico.create({ data: { configuracion_eje_id: eje.id, codigo_posicion: `${i}EI`, lado: LadoVehiculoEnum.IZQUIERDO, posicion_relativa: 1, es_traccion: true, es_interna: true } });
            await prisma.posicionNeumatico.create({ data: { configuracion_eje_id: eje.id, codigo_posicion: `${i}EE`, lado: LadoVehiculoEnum.IZQUIERDO, posicion_relativa: 1, es_traccion: true } });
            await prisma.posicionNeumatico.create({ data: { configuracion_eje_id: eje.id, codigo_posicion: `${i}DI`, lado: LadoVehiculoEnum.DERECHO, posicion_relativa: 1, es_traccion: true, es_interna: true } });
            await prisma.posicionNeumatico.create({ data: { configuracion_eje_id: eje.id, codigo_posicion: `${i}DE`, lado: LadoVehiculoEnum.DERECHO, posicion_relativa: 1, es_traccion: true } });
        }
    }

    // --- 3. CREAR VEHÍCULOS ---
    const t1 = await prisma.vehiculo.upsert({
        where: { numero_economico: 'T1-001' },
        update: { empresa_id: empresaId },
        create: {
            numero_economico: 'T1-001', placa: 'F8U-901', tipo_vehiculo_id: tipoTracto.id, marca: 'VOLVO', modelo_vehiculo: 'FH 440',
            anio_fabricacion: 2014, tipo_medicion: TipoMedicionEnum.KILOMETRAJE, odometro_actual: 672491, centro_costo_id: cecoTransporteId, empresa_id: empresaId, version: 0
        }
    });

    const v1 = await prisma.vehiculo.upsert({
        where: { numero_economico: 'V8-001' },
        update: { empresa_id: empresaId },
        create: {
            numero_economico: 'V8-001', placa: 'E2A-755', tipo_vehiculo_id: tipoVolquete.id, marca: 'SCANIA', modelo_vehiculo: 'P410',
            anio_fabricacion: 2022, tipo_medicion: TipoMedicionEnum.KILOMETRAJE, odometro_actual: 125000, centro_costo_id: cecoMinasId, empresa_id: empresaId, version: 0
        }
    });

    return { tipoTracto, tipoVolquete, t1, v1 };
}
