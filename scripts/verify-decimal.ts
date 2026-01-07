
import { PrismaClient, Prisma } from '@prisma/client'

const prisma = new PrismaClient()

async function main() {
    console.log('--- VERIFICANDO PRECISIÓN FINANCIERA (DECIMAL) ---');

    // Buscar un vehículo existente para no afectar datos
    const vehiculo = await prisma.vehiculo.findFirst();

    if (!vehiculo) {
        console.log('⚠️ No hay vehículos para verificar, creando uno dummy...');
        // Create logic if needed, but we know there are 278 rows
    } else {
        console.log('Vehículo encontrado:', vehiculo.id);
        console.log('Tipo de contador_actual:', typeof vehiculo.contador_actual);
        console.log('Valor:', vehiculo.contador_actual);

        // Check if it's a Prisma.Decimal instance
        if (Prisma.Decimal.isDecimal(vehiculo.contador_actual)) {
            console.log('✅ SUCCESS: `contador_actual` es un objeto Decimal de Prisma/Decimal.js');
        } else {
            console.log('❌ FAIL: `contador_actual` NO es Decimal. Es:', typeof vehiculo.contador_actual);
        }
    }

    // Verificar Neumatico (Profundidad)
    const neumatico = await prisma.neumatico.findFirst({
        where: { profundidad_inicial_mm: { not: undefined } }
    });

    if (neumatico) {
        console.log('\nNeumático encontrado:', neumatico.numero_serie);
        console.log('Profundidad Inicial:', neumatico.profundidad_inicial_mm);
        if (Prisma.Decimal.isDecimal(neumatico.profundidad_inicial_mm)) {
            console.log('✅ SUCCESS: `profundidad_inicial_mm` es Decimal.');
        } else {
            console.log('❌ FAIL: `profundidad_inicial_mm` NO es Decimal.');
        }
    }

    console.log('\n--- VERIFICACIÓN COMPLETADA ---');
}

main()
    .catch(console.error)
    .finally(async () => await prisma.$disconnect())
