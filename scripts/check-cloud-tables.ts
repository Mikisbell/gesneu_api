import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
    console.log('📡 CONECTANDO A SUPABASE CLOUD (AWS US-WEST-2)...\n');

    try {
        // Consulta directa a los metadatos de Postgres
        const result = await prisma.$queryRaw`
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
      `;

        console.log('✅ CONEXIÓN EXITOSA. TABLAS EN LA NUBE:');
        console.log('---------------------------------------');

        const tables = result as any[];
        if (tables.length === 0) {
            console.log('⚠️  No se encontraron tablas en el esquema public.');
        } else {
            tables.forEach((t, i) => {
                console.log(`${i + 1}. ${t.table_name}`);
            });
        }
        console.log('---------------------------------------');
        console.log(`Total: ${tables.length} tablas encontradas en la nube.`);

    } catch (error: any) {
        console.error('❌ ERROR DE CONEXIÓN:', error.message);
    }
}

main()
    .finally(async () => {
        await prisma.$disconnect();
    });
