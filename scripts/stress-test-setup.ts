import { PrismaClient } from '@prisma/client';
import * as bcrypt from 'bcryptjs';

const prisma = new PrismaClient();

async function main() {
    console.log('🚀 Setting up Stress Test Environment...');

    // 1. Create Company
    const empresa = await prisma.empresa.upsert({
        where: { nombre_legal: 'Stress Test Co.' },
        update: {},
        create: {
            nombre_legal: 'Stress Test Co.',
            nombre_comercial: 'StressCorp',
            ruc: '99999999999',
            direccion: 'Test Lab',
            telefono: '555-0000',
            email_contacto: 'admin@stress.test',
            activo: true
        }
    });

    console.log(`✅ Organization ready: ${empresa.id}`);

    // 2. Create User
    const hashedPassword = await bcrypt.hash('StressPassword123!', 10);
    const user = await prisma.usuario.upsert({
        where: { email: 'admin@stress.test' },
        update: {
            password_hash: hashedPassword, // Reset password to ensure we know it
            activo: true,
            empresa_id: empresa.id
        },
        create: {
            email: 'admin@stress.test',
            username: 'stress_admin',
            password_hash: hashedPassword,
            nombre_completo: 'Stress Admin',
            rol: 'ADMIN',
            empresa_id: empresa.id,
            activo: true
        }
    });

    console.log(`✅ User ready: ${user.email} / StressPassword123!`);
    console.log('Setup complete.');
}

main()
    .catch((e) => {
        console.error(e);
        process.exit(1);
    })
    .finally(async () => {
        await prisma.$disconnect();
    });
