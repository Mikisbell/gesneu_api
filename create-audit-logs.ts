import { PrismaClient } from '@prisma/client';
import * as dotenv from 'dotenv';

dotenv.config();

const prisma = new PrismaClient();

async function createAuditLogTable() {
    console.log('🔄 Creating audit_logs table...');

    try {
        await prisma.$executeRawUnsafe(`
      CREATE TABLE IF NOT EXISTS "audit_logs" (
        "id" UUID NOT NULL DEFAULT gen_random_uuid(),
        "user_id" UUID,
        "action" VARCHAR(100) NOT NULL,
        "resource" VARCHAR(100) NOT NULL,
        "details" JSONB,
        "ip_address" VARCHAR(45),
        "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
        
        CONSTRAINT "audit_logs_pkey" PRIMARY KEY ("id")
      );
    `);

        console.log('✅ audit_logs table created');

        // Add foreign key
        await prisma.$executeRawUnsafe(`
      DO $$ 
      BEGIN
        IF NOT EXISTS (
          SELECT 1 FROM pg_constraint WHERE conname = 'audit_logs_user_id_fkey'
        ) THEN
          ALTER TABLE "audit_logs" 
          ADD CONSTRAINT "audit_logs_user_id_fkey" 
          FOREIGN KEY ("user_id") REFERENCES "usuarios"("id") 
          ON DELETE SET NULL ON UPDATE CASCADE;
        END IF;
      END $$;
    `);

        console.log('✅ Foreign key constraint added');

        // Create indexes
        await prisma.$executeRawUnsafe(`
      CREATE INDEX IF NOT EXISTS "audit_logs_user_id_idx" ON "audit_logs"("user_id");
    `);

        await prisma.$executeRawUnsafe(`
      CREATE INDEX IF NOT EXISTS "audit_logs_created_at_idx" ON "audit_logs"("created_at");
    `);

        console.log('✅ Indexes created');
        console.log('🎉 Migration completed successfully!');

    } catch (error) {
        console.error('❌ Error creating audit_logs table:', error);
        throw error;
    } finally {
        await prisma.$disconnect();
    }
}

createAuditLogTable();
