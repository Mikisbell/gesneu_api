import 'dotenv/config';
import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcryptjs';
const { hash } = bcrypt;

import { PrismaPg } from '@prisma/adapter-pg';
import pkg from 'pg';
const { Pool } = pkg;

const pool = new Pool({ connectionString: process.env.DATABASE_URL });
const adapter = new PrismaPg(pool);
const prisma = new PrismaClient({ adapter });

async function main() {
    const adminEmail = 'admin@gesneu.com';
    const adminPassword = 'admin123';

    console.log('Checking for admin user...');

    // Ensure wildcard permission exists
    let wildcardPerm = await prisma.permiso.findUnique({
        where: { codigo: '*' }
    });

    if (!wildcardPerm) {
        console.log('Creating wildcard permission...');
        wildcardPerm = await prisma.permiso.create({
            data: {
                codigo: '*',
                nombre: 'Super Admin',
                recurso: '*',
                accion: '*',
                descripcion: 'Super Admin Permission'
            }
        });
    }

    // Ensure Admin Role exists
    let adminRole = await prisma.rol.findFirst({
        where: { nombre: 'ADMINISTRADOR' },
        include: { permisos: true }
    });

    if (!adminRole) {
        console.log('Creating ADMINISTRADOR role...');
        adminRole = await prisma.rol.create({
            data: {
                nombre: 'ADMINISTRADOR',
                descripcion: 'Acceso total al sistema',
                permisos: {
                    create: {
                        permiso_id: wildcardPerm.id
                    }
                }
            },
            include: { permisos: true }
        });
    } else {
        // Check if it has the permission
        const hasPerm = adminRole.permisos.some((p: any) => p.permiso_id === wildcardPerm!.id);
        if (!hasPerm) {
            console.log('Assigning wildcard permission to existing Admin role...');
            await prisma.rolPermiso.create({
                data: {
                    rol_id: adminRole.id,
                    permiso_id: wildcardPerm.id
                }
            });
        }
    }

    const hashedPassword = await hash(adminPassword, 12);

    // Check if user exists
    const existingUser = await prisma.usuario.findUnique({
        where: { email: adminEmail },
        include: { roles: true }
    });

    if (existingUser) {
        console.log('Updating existing admin user...');
        await prisma.usuario.update({
            where: { id: existingUser.id },
            data: {
                password_hash: hashedPassword,
                activo: true
            }
        });

        // Check if user has the role
        const hasRole = existingUser.roles.some((r: any) => r.rol_id === adminRole!.id);
        if (!hasRole) {
            console.log('Assigning Admin role to user...');
            await prisma.usuarioRol.create({
                data: {
                    usuario_id: existingUser.id,
                    rol_id: adminRole!.id
                }
            });
        }
    } else {
        console.log('Creating new admin user...');
        await prisma.usuario.create({
            data: {
                username: 'admin_qa',
                email: adminEmail,
                password_hash: hashedPassword,
                nombre_completo: 'Admin QA',
                activo: true,
                roles: {
                    create: {
                        rol_id: adminRole!.id
                    }
                }
            }
        });
    }

    console.log('✅ Admin user ensured: admin_qa /', adminPassword);
}

main()
    .catch((e) => {
        console.error(e);
        process.exit(1);
    })
    .finally(async () => {
        await prisma.$disconnect();
    });
