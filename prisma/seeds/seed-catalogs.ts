
import { PrismaClient, TipoProveedorEnum } from '@prisma/client';

export async function seedCatalogs(prisma: PrismaClient, empresaId: string) {
    console.log('📚 Seeding Catalogs (Brands, Models, Types)...');

    // --- PROVEEDORES ---
    const provGoodyear = await prisma.proveedor.upsert({
        where: { ruc: '20100070970' },
        update: { empresa_id: empresaId },
        create: {
            nombre: 'GOODYEAR PERU S.A.',
            ruc: '20100070970',
            tipo: TipoProveedorEnum.FABRICANTE,
            empresa_id: empresaId
        }
    });

    const provMichelin = await prisma.proveedor.upsert({
        where: { ruc: '20500011122' },
        update: { empresa_id: empresaId },
        create: {
            nombre: 'MICHELIN PERU',
            ruc: '20500011122',
            tipo: TipoProveedorEnum.FABRICANTE,
            empresa_id: empresaId
        }
    });

    // --- FABRICANTES ---
    const fabGoodyear = await prisma.fabricanteNeumatico.upsert({
        where: { codigo_abreviado: 'GY' },
        update: {},
        create: { nombre: 'GOODYEAR', codigo_abreviado: 'GY' }
    });

    const fabMichelin = await prisma.fabricanteNeumatico.upsert({
        where: { codigo_abreviado: 'MI' },
        update: {},
        create: { nombre: 'MICHELIN', codigo_abreviado: 'MI' }
    });

    // --- MODELOS ---
    // 1. Goodyear KMAX S (Direccional)
    const modKmaxS = await prisma.modeloNeumatico.upsert({
        where: { fabricante_id_nombre_modelo_medida: { fabricante_id: fabGoodyear.id, nombre_modelo: 'KMAX S', medida: '295/80R22.5' } },
        update: {},
        create: {
            nombre_modelo: 'KMAX S',
            medida: '295/80R22.5',
            profundidad_original_mm: 15.8,
            profundidad_minima_retiro_mm: 3.0,
            fabricante_id: fabGoodyear.id,
            reencauches_maximos: 2,
            indice_carga: '152', indice_velocidad: 'M',
            patron_dibujo: 'DIRECCIONAL'
        }
    });

    // 2. Michelin X MULTI Z (Toda Posición)
    const modMultiZ = await prisma.modeloNeumatico.upsert({
        where: { fabricante_id_nombre_modelo_medida: { fabricante_id: fabMichelin.id, nombre_modelo: 'X MULTI Z', medida: '295/80R22.5' } },
        update: {},
        create: {
            nombre_modelo: 'X MULTI Z',
            medida: '295/80R22.5',
            profundidad_original_mm: 16.0,
            profundidad_minima_retiro_mm: 3.0,
            fabricante_id: fabMichelin.id,
            reencauches_maximos: 3,
            indice_carga: '152', indice_velocidad: 'M',
            patron_dibujo: 'TODA POSICION'
        }
    });

    // 3. Michelin X WORKS (Mixto/Tracción)
    const modXWorks = await prisma.modeloNeumatico.upsert({
        where: { fabricante_id_nombre_modelo_medida: { fabricante_id: fabMichelin.id, nombre_modelo: 'X WORKS', medida: '295/80R22.5' } },
        update: {},
        create: {
            nombre_modelo: 'X WORKS',
            medida: '295/80R22.5',
            profundidad_original_mm: 22.0, // Más profundo para tracción off-road
            profundidad_minima_retiro_mm: 4.0,
            fabricante_id: fabMichelin.id,
            reencauches_maximos: 2,
            indice_carga: '154', indice_velocidad: 'K',
            patron_dibujo: 'TRACCION'
        }
    });

    // --- MOTIVOS DESECHO ---
    const motivos = [
        { code: 'DN-001', name: 'DESGASTE NATURAL', desc: 'Llegó al límite' },
        { code: 'CL-001', name: 'CORTE LATERAL', desc: 'Daño irreparable', evidence: true },
        { code: 'RE-001', name: 'REVENTÓN', desc: 'Explosión operativa', evidence: true },
    ];

    for (const m of motivos) {
        await prisma.motivoDesecho.upsert({
            where: { codigo: m.code },
            update: {},
            create: { codigo: m.code, nombre: m.name, descripcion: m.desc, requiere_evidencia: m.evidence || false }
        });
    }

    return {
        provGoodyear, provMichelin,
        modKmaxS, modMultiZ, modXWorks
    };
}
