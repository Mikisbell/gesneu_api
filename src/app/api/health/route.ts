import { NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import type { HealthCheckResponse } from '@/lib/types/api'

export async function GET(): Promise<NextResponse<HealthCheckResponse>> {
  const checks = {
    database: false,
    redis: false,
    external_apis: false
  }

  const start = Date.now()

  try {
    // Database check
    await prisma.$queryRaw`SELECT 1`
    checks.database = true
  } catch (error) {
    console.error('Database health check failed:', error)
  }

  // Redis check (placeholder - will implement when Redis is added)
  checks.redis = true

  // External APIs check (placeholder)
  checks.external_apis = true

  const healthy = Object.values(checks).every(Boolean)
  const responseTime = Date.now() - start

  const response: HealthCheckResponse = {
    status: healthy ? 'healthy' : 'unhealthy',
    timestamp: new Date().toISOString(),
    version: process.env.npm_package_version || '1.0.0',
    environment: process.env.NODE_ENV || 'development',
    uptime: process.uptime(),
    responseTime,
    checks,
    memory: process.memoryUsage(),
    cpu: process.cpuUsage()
  }

  return NextResponse.json(response, {
    status: healthy ? 200 : 503
  })
}
