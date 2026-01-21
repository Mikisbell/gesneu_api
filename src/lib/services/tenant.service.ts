
import { prisma } from '@/lib/prisma';
import { Empresa, RolEnum } from '@prisma/client';

export type CreateTenantInput = {
    nombre: string;
    ruc: string;
    direccion?: string;
    adminEmail: string;
    adminName: string;
    adminPasswordHash: string;
};

export class TenantService {
    /**
     * Crea una nueva empresa y su usuario administrador inicial.
     * Ejecuta un proceso de "bootstrap" para crear datos base (Almacén principal, etc.)
     */
    static async createTenant(input: CreateTenantInput) {
        return await prisma.$transaction(async (tx) => {
            // 0. Generar ID y Establecer contexto para RLS ANTES de insertar
            const newTenantId = crypto.randomUUID();

            // Inject context to satisfy RLS
            await tx.$executeRawUnsafe(`SELECT set_config('app.current_tenant', '${newTenantId}', true)`);
            // Use new ID as user ID temporarily for bypass
            await tx.$executeRawUnsafe(`SELECT set_config('app.current_user_id', '${newTenantId}', true)`);

            // 1. Crear la Empresa con ID manual
            const empresa = await tx.empresa.create({
                data: {
                    id: newTenantId,
                    nombre: input.nombre,
                    ruc: input.ruc,
                    direccion: input.direccion,
                    activo: true,
                },
            });

            // 3. Crear Usuario Administrador
            const adminUser = await tx.usuario.create({
                data: {
                    empresa_id: empresa.id,
                    email: input.adminEmail,
                    username: input.adminEmail.split('@')[0],
                    nombre_completo: input.adminName,
                    password_hash: input.adminPasswordHash,
                    rol: 'ADMIN',
                    activo: true,
                },
            });

            // 4. Boostrap: Almacén Principal
            await tx.almacen.create({
                data: {
                    empresa_id: empresa.id,
                    codigo: 'ALM-PRINCIPAL',
                    nombre: 'Almacén Principal',
                    tipo: 'CENTRAL',
                    direccion: input.direccion || 'Dirección Principal',
                    activo: true,
                },
            });

            // 5. Configs (Optional)

            return { empresa, adminUser };
        });
    }

    /**
     * Obtiene lista de todas las empresas (Solo para Superadmin)
     */
    static async getAllTenants() {
        return await prisma.empresa.findMany({
            orderBy: { creado_en: 'desc' },
            include: {
                _count: {
                    select: { usuarios: true, vehiculos: true, neumaticos: true }
                }
            }
        });
    }

    /**
     * Suspender o Reactivar una empresa
     */
    static async toggleTenantStatus(id: string, activo: boolean) {
        return await prisma.empresa.update({
            where: { id },
            data: { activo },
        });
    }
}
