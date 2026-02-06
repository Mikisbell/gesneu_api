const { PrismaClient } = require('@prisma/client');
const { PrismaPg } = require('@prisma/adapter-pg');
const { Pool } = require('pg');
const bcrypt = require('bcryptjs');
require('dotenv').config();

const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: { rejectUnauthorized: false }
});
const adapter = new PrismaPg(pool);
const prisma = new PrismaClient({ adapter });

async function verifyAdmin() {
    try {
        console.log('🔍 Checking for user: admin');
        const user = await prisma.usuario.findUnique({
            where: { username: 'admin' }
        });

        const targetPassword = 'admin123';
        const salt = await bcrypt.genSalt(10);
        const hashedPassword = await bcrypt.hash(targetPassword, salt);

        if (!user) {
            console.log('❌ User "admin" not found. Creating...');
            // Create minimal admin user
            // Need an Empresa/Tenant first?
            let empresa = await prisma.empresa.findFirst();
            if (!empresa) {
                console.log('⚠️ No Company found. Creating default tenant...');
                empresa = await prisma.empresa.create({
                    data: {
                        razon_social: 'GESNEU STRESS TEST CORP',
                        ruc: '20000000001'
                    }
                });
            }

            await prisma.usuario.create({
                data: {
                    username: 'admin',
                    email: 'admin@gesneu.com',
                    password_hash: hashedPassword,
                    nombre_completo: 'Admin Stress Test',
                    rol: 'ADMIN',
                    activo: true,
                    empresa_id: empresa.id
                }
            });
            console.log('✅ User "admin" created with password "admin123"');
        } else {
            console.log('✅ User "admin" found.');
            // Always reset password to ensure test consistency
            await prisma.usuario.update({
                where: { id: user.id },
                data: {
                    password_hash: hashedPassword,
                    activo: true
                }
            });
            console.log('🔄 Password reset to "admin123" to ensure match.');
        }

        // Verify immediately
        const updatedUser = await prisma.usuario.findUnique({ where: { username: 'admin' } });
        const isMatch = await bcrypt.compare(targetPassword, updatedUser.password_hash);
        console.log(`🔐 Verification Check: Password "admin123" matches hash? ${isMatch ? '✅ YES' : '❌ NO'}`);
        if (!isMatch) console.log('⚠️ HASH MISMATCH detected immediately after save!');

    } catch (err) {
        console.error('❌ Error:', err);
    } finally {
        await prisma.$disconnect();
        await pool.end();
    }
}

verifyAdmin();
