import { NextResponse } from 'next/server'
import { ApiResponse, PaginatedResponse } from './types'

export class ApiResponseHelper {
  static success<T>(data: T, message?: string): NextResponse<ApiResponse<T>> {
    return NextResponse.json({
      success: true,
      data,
      message
    })
  }

  static created<T>(data: T, message?: string): NextResponse<ApiResponse<T>> {
    return NextResponse.json({
      success: true,
      data,
      message
    }, { status: 201 })
  }

  static error(error: string, status: number = 500): NextResponse<ApiResponse> {
    return NextResponse.json(
      {
        success: false,
        error
      },
      { status }
    )
  }

  static paginated<T>(
    data: T[],
    page: number,
    pageSize: number,
    total: number
  ): NextResponse<PaginatedResponse<T>> {
    return NextResponse.json({
      success: true,
      data,
      pagination: {
        page,
        pageSize,
        total,
        totalPages: Math.ceil(total / pageSize)
      }
    })
  }

  static notFound(message: string = 'Recurso no encontrado'): NextResponse<ApiResponse> {
    return NextResponse.json(
      {
        success: false,
        error: message
      },
      { status: 404 }
    )
  }

  static badRequest(message: string = 'Solicitud inválida'): NextResponse<ApiResponse> {
    return NextResponse.json(
      {
        success: false,
        error: message
      },
      { status: 400 }
    )
  }

  static unauthorized(message: string = 'No autorizado'): NextResponse<ApiResponse> {
    return NextResponse.json(
      {
        success: false,
        error: message
      },
      { status: 401 }
    )
  }
}
