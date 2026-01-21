
import { PrismaClient } from '@prisma/client';

export async function seedInfrastructure(prisma: PrismaClient, empresaId: string) {
    console.log('🏭 Seeding Infrastructure (Warehouses, Cost Centers)...');

    // --- ALMACENES ---
    const almacenPrincipal = await prisma.almacen.upsert({
        where: { codigo: 'ALM-CEN' },
        update: { empresa_id: empresaId },
        create: {
            codigo: 'ALM-CEN',
            nombre: 'ALMACEN CENTRAL',
            tipo: 'PRINCIPAL',
            direccion: 'Base Central',
            empresa_id: empresaId
        }
    });

    const almacenScrap = await prisma.almacen.upsert({
        where: { codigo: 'ALM-DES' },
        update: { empresa_id: empresaId },
        create: {
            codigo: 'ALM-DES',
            nombre: 'AREA DE DESECHOS',
            tipo: 'SCRAP',
            direccion: 'Patio Trasero',
            empresa_id: empresaId
        }
    });

    // --- CENTROS DE COSTO ---
    const cecoTransporte = await prisma.centroCosto.upsert({
        where: { codigo: '650101' },
        update: {},
        create: { codigo: '650101', nombre: 'TRANSPORTE', area_negocio: 'TRANSPORTE' }
    });

    const cecoMinas = await prisma.centroCosto.upsert({
        where: { codigo: '650202' },
        update: {},
        create: { codigo: '650202', nombre: 'OPERACIONES MINA', area_negocio: 'MINA' }
    });

    return { almacenPrincipal, almacenScrap, cecoTransporte, cecoMinas };
}
