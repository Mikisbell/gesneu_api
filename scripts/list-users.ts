import 'dotenv/config';
import { PrismaClient } from '@prisma/client';
import { PrismaPg } from '@prisma/adapter-pg';
import pkg from 'pg';
const { Pool } = pkg;

// Log the masked DB URL to confirm where we are connecting
const dbUrl = process.env.DATABASE_URL || '';
const maskedUrl = dbUrl.replace(/:([^:@]+)@/, ':****@');
console.log(`🔌 Conectando a: ${maskedUrl}`);

const pool = new Pool({ connectionString: dbUrl });
const adapter = new PrismaPg(pool);
const prisma = new PrismaClient({ adapter });

async function main() {
    try {
        const users = await prisma.usuario.findMany({
            include: { roles: { include: { rol: true } } }
        });

        console.log(`\n📊 Total de usuarios encontrados: ${users.length}`);

        if (users.length > 0) {
            console.log('\n📋 Lista de Usuarios:');
            users.forEach(u => {
                console.log(`----------------------------------------`);
                console.log(`ID: ${u.id}`);
                console.log(`Username: ${u.username}`);
                console.log(`Email: ${u.email}`);
                console.log(`Nombre: ${u.nombre_completo}`);
                console.log(`Activo: ${u.activo}`);
                console.log(`Roles: ${u.roles.map(r => r.rol.nombre).join(', ')}`);
            });
        } else {
            console.log('⚠️ No se encontraron usuarios.');
        }

    } catch (error) {
        console.error('❌ Error:', error);
    } finally {
        await prisma.$disconnect();
    }
}

main();
