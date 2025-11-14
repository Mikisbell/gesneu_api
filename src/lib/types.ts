// Tipos básicos para la API

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

export interface PaginatedResponse<T = any> {
  success: boolean
  data: T[]
  pagination: {
    page: number
    pageSize: number
    total: number
    totalPages: number
  }
}

export interface HealthCheckResponse {
  status: 'ok' | 'error'
  message: string
  timestamp: string
  version: string
  database?: {
    connected: boolean
    message?: string
  }
}
