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

const pool = new Pool({
  connectionString,
  ssl: useSSL ? { rejectUnauthorized: false } : false,
  max: 10, // Reduced for concurrency (was 20)
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 20000, // Increased timeout for queueing
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
