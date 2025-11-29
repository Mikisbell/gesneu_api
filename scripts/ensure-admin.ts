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

    const hashedPassword = await hash(adminPassword, 12);

    // Check if user exists
    const existingUser = await prisma.usuario.findUnique({
        where: { email: adminEmail }
    });

    if (existingUser) {
        console.log('Updating existing admin user...');
        await prisma.usuario.update({
            where: { id: existingUser.id },
            data: {
                password_hash: hashedPassword,
                activo: true,
                rol: 'ADMIN' // Direct rol assignment
            }
        });
    } else {
        console.log('Creating new admin user...');
        await prisma.usuario.create({
            data: {
                username: 'admin_qa',
                email: adminEmail,
                password_hash: hashedPassword,
                nombre_completo: 'Admin QA',
                activo: true,
                rol: 'ADMIN' // Direct rol assignment
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
