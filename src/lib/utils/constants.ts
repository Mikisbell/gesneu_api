// src/lib/utils/constants.ts
export const API_VERSION = 'v1'
export const API_PREFIX = `/api/${API_VERSION}`

export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_LIMIT: 10,
  MAX_LIMIT: 100
} as const

export const CACHE_TTL = {
  CATALOGOS: 3600, // 1 hora
  USUARIOS: 1800,  // 30 minutos
  REPORTES: 300,   // 5 minutos
  HEALTH: 60       // 1 minuto
} as const

export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  TOO_MANY_REQUESTS: 429,
  INTERNAL_SERVER_ERROR: 500
} as const

export const ERROR_MESSAGES = {
  UNAUTHORIZED: 'No autorizado',
  FORBIDDEN: 'Acceso denegado',
  NOT_FOUND: 'Recurso no encontrado',
  VALIDATION_ERROR: 'Error de validación',
  INTERNAL_ERROR: 'Error interno del servidor'
} as const
