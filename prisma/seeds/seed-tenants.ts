
import { PrismaClient, RolEnum } from '@prisma/client';
import bcrypt from 'bcryptjs';

export async function seedTenants(prisma: PrismaClient) {
    console.log('🏢 Seeding Tenants & Users...');

    // 1. EMPRESA TENANT
    const empresa = await prisma.empresa.upsert({
        where: { ruc: '20600112233' },
        update: {},
        create: {
            nombre: 'ECOSEM HUARAUCACA',
            ruc: '20600112233',
            direccion: 'Pasco, Peru',
            activo: true
        }
    });

    // 2. USUARIOS
    const passwordHash = await bcrypt.hash('123456', 10);

    const users = [
        { user: 'admin', role: RolEnum.ADMIN, name: 'Administrador Sistema' },
        { user: 'gestor', role: RolEnum.GESTOR, name: 'Juan Perez (Gestor)' },
        { user: 'operador', role: RolEnum.OPERADOR, name: 'Carlos Operador' },
    ];

    for (const u of users) {
        await prisma.usuario.upsert({
            where: { username: u.user },
            update: { empresa_id: empresa.id },
            create: {
                username: u.user,
                email: `${u.user}@gesneu.com`,
                nombre_completo: u.name,
                password_hash: passwordHash,
                rol: u.role,
                empresa_id: empresa.id
            }
        });
    }

    return { empresa };
}
