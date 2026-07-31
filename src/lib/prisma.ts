import { PrismaClient } from '@prisma/client'
import { PrismaPg } from '@prisma/adapter-pg'
import { Pool } from 'pg'

declare global {
  var prisma: PrismaClient | undefined
}

const connectionString = process.env.DATABASE_URL;
const isLocalhost = connectionString?.includes('localhost') || connectionString?.includes('127.0.0.1');
const isCI = process.env.CI === 'true';
const useSSL = !isLocalhost && !isCI;

const maxPoolSize = process.env.DATABASE_POOL_SIZE 
  ? Number(process.env.DATABASE_POOL_SIZE) 
  : (process.env.VERCEL ? 1 : 5);

const pool = new Pool({
  connectionString,
  ssl: useSSL ? { rejectUnauthorized: false } : false,
  max: maxPoolSize, // 1 en Vercel, 5 en local para no saturar Supabase Session Mode (pool_size: 15)
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 10000,
})

const adapter = new PrismaPg(pool)

export const prisma =
  global.prisma ||
  new PrismaClient({
    adapter,
    // IMPORTANT: Disable query logging - causes massive slowdown
    log: ['error'],
  })

if (process.env.NODE_ENV !== 'production') {
  global.prisma = prisma
}

export default prisma
