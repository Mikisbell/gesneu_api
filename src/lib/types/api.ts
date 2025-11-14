// src/lib/types/api.ts
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  timestamp: string
}

export interface ApiError {
  success: false
  error: string
  code?: string
  details?: any
  timestamp: string
}

export interface PaginationMeta {
  page: number
  limit: number
  total: number
  totalPages: number
  hasNext: boolean
  hasPrev: boolean
}

export interface PaginatedResponse<T> {
  success: true
  data: T[]
  pagination: PaginationMeta
  timestamp: string
}

export interface HealthCheckResponse {
  status: 'healthy' | 'unhealthy'
  timestamp: string
  version: string
  environment: string
  uptime: number
  responseTime: number
  checks: {
    database: boolean
    redis: boolean
    external_apis: boolean
  }
  memory: NodeJS.MemoryUsage
  cpu: NodeJS.CpuUsage
}

export interface AuthUser {
  id: string
  username: string
  email: string
  nombre_completo: string
  roles: Array<{
    id: string
    nombre: string
    permisos: string[]
  }>
  permissions: string[]
}
