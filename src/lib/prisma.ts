import { PrismaClient } from '@prisma/client'
import { PrismaPg } from '@prisma/adapter-pg'
import { Pool } from 'pg'

declare global {
  var prisma: PrismaClient | undefined
}

// Configuración robusta para Supabase y CI
const connectionString = process.env.DATABASE_URL;

// SSL es requerido por Supabase pero NO por Postgres local en CI
const isLocalhost = connectionString?.includes('localhost') || connectionString?.includes('127.0.0.1');
const isCI = process.env.CI === 'true';
const useSSL = !isLocalhost && !isCI;

const pool = new Pool({
  connectionString,
  ssl: useSSL ? { rejectUnauthorized: false } : false,
  max: 10, // Límite de conexiones
})

const adapter = new PrismaPg(pool)

export const prisma =
  global.prisma ||
  new PrismaClient({
    adapter,
    log: process.env.NODE_ENV === 'development' ? ['query', 'error', 'warn'] : ['error'],
  })

if (process.env.NODE_ENV !== 'production') {
  global.prisma = prisma
}

export default prisma
