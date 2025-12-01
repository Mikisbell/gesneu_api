require('dotenv').config({ path: '.env.local' });

const { PrismaClient } = require('@prisma/client');
const { PrismaPg } = require('@prisma/adapter-pg');
const { Pool } = require('pg');

const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: { rejectUnauthorized: false },
    max: 20, // Más conexiones para import
});

const adapter = new PrismaPg(pool);
const prisma = new PrismaClient({
    adapter,
    log: ['error', 'warn']
});

module.exports = prisma;
