import 'dotenv/config';
import { prisma } from './src/lib/prisma';

async function main() {
    try {
        console.log('Adding fabricante_id column...');
        await prisma.$executeRawUnsafe(`
            ALTER TABLE "modelos_neumatico" 
            ADD COLUMN IF NOT EXISTS "fabricante_id" UUID;
        `);
        console.log('Column added.');

        console.log('Adding reencauches_maximos column...');
        await prisma.$executeRawUnsafe(`
            ALTER TABLE "modelos_neumatico" 
            ADD COLUMN IF NOT EXISTS "reencauches_maximos" INTEGER DEFAULT 0;
        `);
        console.log('Column reencauches_maximos added.');

        console.log('Adding activo column...');
        await prisma.$executeRawUnsafe(`
            ALTER TABLE "modelos_neumatico" 
            ADD COLUMN IF NOT EXISTS "activo" BOOLEAN DEFAULT true;
        `);

        console.log('Adding creado_en column...');
        await prisma.$executeRawUnsafe(`
            ALTER TABLE "modelos_neumatico" 
            ADD COLUMN IF NOT EXISTS "creado_en" TIMESTAMPTZ(6) DEFAULT CURRENT_TIMESTAMP;
        `);

        console.log('Adding actualizado_en column...');
        await prisma.$executeRawUnsafe(`
            ALTER TABLE "modelos_neumatico" 
            ADD COLUMN IF NOT EXISTS "actualizado_en" TIMESTAMPTZ(6);
        `);

        console.log('Adding indice_carga column...');
        await prisma.$executeRawUnsafe(`
            ALTER TABLE "modelos_neumatico" 
            ADD COLUMN IF NOT EXISTS "indice_carga" VARCHAR(10);
        `);

        console.log('Adding indice_velocidad column...');
        await prisma.$executeRawUnsafe(`
            ALTER TABLE "modelos_neumatico" 
            ADD COLUMN IF NOT EXISTS "indice_velocidad" VARCHAR(5);
        `);

        console.log('Adding tipo_construccion column...');
        await prisma.$executeRawUnsafe(`
            ALTER TABLE "modelos_neumatico" 
            ADD COLUMN IF NOT EXISTS "tipo_construccion" VARCHAR(20);
        `);

        console.log('Dropping marca_id column...');
        await prisma.$executeRawUnsafe(`
            ALTER TABLE "modelos_neumatico" 
            DROP COLUMN IF EXISTS "marca_id" CASCADE;
        `);

        console.log('Checking columns...');
        const columns = await prisma.$queryRaw`
            SELECT column_name, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'modelos_neumatico';
        `;
        console.log('Checking triggers...');
        const triggers = await prisma.$queryRaw`
            SELECT trigger_name 
            FROM information_schema.triggers 
            WHERE event_object_table = 'modelos_neumatico';
        `;
        // console.log('Checking constraints...');
        // const constraints = await prisma.$queryRaw`
        //     SELECT conname, contype, pg_get_constraintdef(oid) 
        //     FROM pg_constraint 
        //     WHERE conrelid = 'modelos_neumatico'::regclass;
        // `;
        // console.log('Constraints:', constraints);
        console.log('Checking column type for estado_actual...');
        const columnType = await prisma.$queryRaw`
            SELECT column_name, udt_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'neumaticos' AND column_name = 'estado_actual';
        `;
        console.log('Column Type:', columnType);

        console.log('Checking columns for fabricantes_neumatico...');
        const colsFabricante = await prisma.$queryRaw`
            SELECT column_name, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'fabricantes_neumatico';
        `;
        console.log('Cols Fabricante:', colsFabricante);

        console.log('Checking columns for almacenes...');
        const colsAlmacen = await prisma.$queryRaw`
            SELECT column_name, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'almacenes';
        `;
        console.log('Cols Almacen:', colsAlmacen);

        console.log('Checking columns for vehiculos...');
        const colsVehiculo = await prisma.$queryRaw`
            SELECT column_name, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'vehiculos';
        `;
        console.log('Cols Vehiculo:', colsVehiculo);

        console.log('Checking columns for posiciones_neumatico...');
        const colsPosicion = await prisma.$queryRaw`
            SELECT column_name, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'posiciones_neumatico';
        `;
        console.log('Adding descripcion to almacenes...');
        await prisma.$executeRawUnsafe(`
            ALTER TABLE "almacenes" 
            ADD COLUMN IF NOT EXISTS "descripcion" TEXT;
        `);

        console.log('Adding numero_posicion to posiciones_neumatico...');
        await prisma.$executeRawUnsafe(`
            ALTER TABLE "posiciones_neumatico" 
            ADD COLUMN IF NOT EXISTS "numero_posicion" INTEGER DEFAULT 1;
        `);

        console.log('Adding lado_vehiculo to posiciones_neumatico...');
        // Check if type exists first, usually handled by enum check but we assume it exists
        await prisma.$executeRawUnsafe(`
            ALTER TABLE "posiciones_neumatico" 
            ADD COLUMN IF NOT EXISTS "lado_vehiculo" "lado_vehiculo_enum" DEFAULT 'IZQUIERDO';
        `);

        console.log('Fixing tipo for proveedores...');

        // Drop column first
        await prisma.$executeRawUnsafe(`
            ALTER TABLE "proveedores" 
            DROP COLUMN IF EXISTS "tipo";
        `);

        // Drop wrong enum if exists
        await prisma.$executeRawUnsafe(`
            DROP TYPE IF EXISTS "tipo_proveedor_enum";
        `);

        // Create correct enum
        await prisma.$executeRawUnsafe(`
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipoproveedorenum') THEN
                    CREATE TYPE "tipoproveedorenum" AS ENUM ('FABRICANTE', 'DISTRIBUIDOR', 'SERVICIO_REPARACION', 'SERVICIO_REENCAUCHE', 'OTRO');
                END IF;
            END
            $$;
        `);

        // Add column with correct type
        await prisma.$executeRawUnsafe(`
            ALTER TABLE "proveedores" 
            ADD COLUMN "tipo" "tipoproveedorenum" NOT NULL DEFAULT 'OTRO';
        `);

        await prisma.$executeRawUnsafe(`
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'modelos_neumatico_fabricante_id_fkey') THEN
                    ALTER TABLE "modelos_neumatico"
                    ADD CONSTRAINT "modelos_neumatico_fabricante_id_fkey"
                    FOREIGN KEY ("fabricante_id")
                    REFERENCES "fabricantes_neumatico"("id")
                    ON DELETE RESTRICT ON UPDATE CASCADE;
                END IF;
            END
            $$;
        `);
        console.log('FK constraint added.');

    } catch (e) {
        console.error('Error:', e);
    } finally {
        await prisma.$disconnect();
    }
}

main();
