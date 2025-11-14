import { NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import { HealthCheckResponse } from '@/lib/types'

export async function GET() {
  const healthCheck: HealthCheckResponse = {
    status: 'ok',
    message: 'GesNeu API - Next.js + Supabase',
    timestamp: new Date().toISOString(),
    version: '1.0.0'
  }

  try {
    // Verificar conexión con la base de datos
    await prisma.$queryRaw`SELECT 1`
    healthCheck.database = {
      connected: true,
      message: 'PostgreSQL conectado exitosamente'
    }
  } catch (error) {
    healthCheck.status = 'error'
    healthCheck.database = {
      connected: false,
      message: error instanceof Error ? error.message : 'Error desconocido'
    }
  }

  const status = healthCheck.status === 'ok' ? 200 : 503

  return NextResponse.json(healthCheck, { status })
}
