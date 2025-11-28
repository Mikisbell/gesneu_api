// src/lib/utils/api-response.ts
import { NextResponse } from 'next/server'
import { ZodError } from 'zod'
import { Prisma } from '@prisma/client'
import { HTTP_STATUS, ERROR_MESSAGES } from './constants'
import type { ApiResponse, ApiError, PaginatedResponse, PaginationMeta } from '@/lib/types/api'

export class ApiResponseHelper {
  static success<T>(data: T, message?: string): NextResponse<ApiResponse<T>> {
    return NextResponse.json({
      success: true,
      data,
      message,
      timestamp: new Date().toISOString()
    })
  }

  static created<T>(data: T, message?: string): NextResponse<ApiResponse<T>> {
    return NextResponse.json({
      success: true,
      data,
      message: message || 'Recurso creado exitosamente',
      timestamp: new Date().toISOString()
    }, { status: HTTP_STATUS.CREATED })
  }

  static paginated<T>(
    data: T[],
    pagination: PaginationMeta
  ): NextResponse<PaginatedResponse<T>> {
    return NextResponse.json({
      success: true,
      data,
      pagination,
      timestamp: new Date().toISOString()
    })
  }

  static error(
    message: string,
    status: number = HTTP_STATUS.INTERNAL_SERVER_ERROR,
    code?: string,
    details?: any
  ): NextResponse<ApiError> {
    return NextResponse.json({
      success: false,
      error: message,
      code,
      details,
      timestamp: new Date().toISOString()
    }, { status })
  }

  static unauthorized(message = ERROR_MESSAGES.UNAUTHORIZED): NextResponse<ApiError> {
    return this.error(message, HTTP_STATUS.UNAUTHORIZED, 'UNAUTHORIZED')
  }

  static forbidden(message = ERROR_MESSAGES.FORBIDDEN): NextResponse<ApiError> {
    return this.error(message, HTTP_STATUS.FORBIDDEN, 'FORBIDDEN')
  }

  static notFound(message = ERROR_MESSAGES.NOT_FOUND): NextResponse<ApiError> {
    return this.error(message, HTTP_STATUS.NOT_FOUND, 'NOT_FOUND')
  }

  static conflict(message: string): NextResponse<ApiError> {
    return this.error(message, HTTP_STATUS.CONFLICT, 'CONFLICT')
  }

  static validationError(error: ZodError): NextResponse<ApiError> {
    return this.error(
      ERROR_MESSAGES.VALIDATION_ERROR,
      HTTP_STATUS.BAD_REQUEST,
      'VALIDATION_ERROR',
      error.issues
    )
  }

  static handleError(error: unknown): NextResponse<ApiError> {
    console.error('API Error:', error)

    // Handle custom auth errors
    if (error instanceof Error) {
      if (error.message === 'UNAUTHORIZED') {
        return this.unauthorized();
      }
      if (error.message === 'FORBIDDEN') {
        return this.forbidden();
      }
    }

    if (error instanceof ZodError) {
      return this.validationError(error)
    }

    if (error instanceof Prisma.PrismaClientKnownRequestError) {
      switch (error.code) {
        case 'P2002':
          return this.conflict('El recurso ya existe')
        case 'P2025':
          return this.notFound('Recurso no encontrado')
        default:
          return this.error('Error de base de datos', HTTP_STATUS.INTERNAL_SERVER_ERROR, 'DATABASE_ERROR')
      }
    }

    if (error instanceof Error) {
      return this.error(error.message, HTTP_STATUS.INTERNAL_SERVER_ERROR, 'INTERNAL_ERROR')
    }

    return this.error(ERROR_MESSAGES.INTERNAL_ERROR, HTTP_STATUS.INTERNAL_SERVER_ERROR, 'UNKNOWN_ERROR')
  }

  static createPagination(
    page: number,
    limit: number,
    total: number
  ): PaginationMeta {
    const totalPages = Math.ceil(total / limit)

    return {
      page,
      limit,
      total,
      totalPages,
      hasNext: page < totalPages,
      hasPrev: page > 1
    }
  }
}
