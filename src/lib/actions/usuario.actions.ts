'use server';

import { prisma } from '@/lib/prisma';
import { requireAuth } from '@/lib/auth/authorization';
import { CreateUsuarioDTO, UpdateUsuarioDTO } from '@/lib/validators/usuarios';
import { hash } from 'bcryptjs';
import { revalidatePath } from 'next/cache';
import { RolEnum } from '@prisma/client';

export async function getUsuarios() {
    const session = await requireAuth();
    // En multi-tenant real filtraríamos por empresa_id
    // Si es ADMIN de sistema ve todo, si es GESTOR ve su empresa.
    // Asumiremos filtro simple por ahora si la sesión tiene empresa_id
    const where = session.user.empresa_id
        ? { empresa_id: session.user.empresa_id }
        : {};

    return await prisma.usuario.findMany({
        where,
        orderBy: { creado_en: 'desc' },
        select: {
            id: true,
            nombre_completo: true,
            email: true,
            username: true,
            rol: true,
            activo: true,
            creado_en: true,
            empresa: {
                select: { nombre: true }
            }
        }
    });
}

export async function createUsuario(data: CreateUsuarioDTO) {
    const session = await requireAuth();

    // Validar duplicados
    const existing = await prisma.usuario.findFirst({
        where: {
            OR: [
                { email: data.email },
                { username: data.username }
            ]
        }
    });

    if (existing) {
        throw new Error('El email o nombre de usuario ya está registrado');
    }

    const hashedPassword = await hash(data.password, 10);
    const empresaId = session.user.empresa_id;

    if (!empresaId) {
        throw new Error('No se puede crear usuario sin contexto de empresa');
    }

    await prisma.usuario.create({
        data: {
            username: data.username,
            nombre_completo: data.nombre_completo,
            email: data.email,
            password_hash: hashedPassword,
            rol: data.rol as RolEnum,
            empresa_id: empresaId
        }
    });

    revalidatePath('/dashboard/usuarios');
}

export async function updateUsuario(id: string, data: UpdateUsuarioDTO) {
    await requireAuth();

    const updateData: any = { ...data };

    if (data.password) {
        updateData.password_hash = await hash(data.password, 10);
        delete updateData.password;
    }

    await prisma.usuario.update({
        where: { id },
        data: updateData
    });

    revalidatePath('/dashboard/usuarios');
}

export async function toggleUsuarioEstado(id: string, activo: boolean) {
    const session = await requireAuth();

    if (id === session.user.id) {
        throw new Error('No puedes desactivar tu propio usuario');
    }

    await prisma.usuario.update({
        where: { id },
        data: { activo }
    });

    revalidatePath('/dashboard/usuarios');
}

export async function deleteUsuario(id: string) {
    const session = await requireAuth();

    if (id === session.user.id) {
        throw new Error('No puedes eliminar tu propio usuario');
    }

    // Schema only has 'activo', no soft delete fields like eliminado_en
    await prisma.usuario.update({
        where: { id },
        data: {
            activo: false
        }
    });

    revalidatePath('/dashboard/usuarios');
}
