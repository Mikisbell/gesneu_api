import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { getToken } from 'next-auth/jwt'

export async function middleware(request: NextRequest) {
    const token = await getToken({
        req: request,
        secret: process.env.NEXTAUTH_SECRET,
        // NextAuth v5 uses this cookie name format
        cookieName: process.env.NODE_ENV === 'production'
            ? '__Secure-authjs.session-token'
            : 'authjs.session-token'
    })

    const isAuthPage = request.nextUrl.pathname.startsWith('/login')
    const isDashboardPage = request.nextUrl.pathname.startsWith('/dashboard')

    // Redirect authenticated users away from login page
    if (isAuthPage && token) {
        return NextResponse.redirect(new URL('/dashboard', request.url))
    }

    // Protect dashboard routes
    if (isDashboardPage && !token) {
        const loginUrl = new URL('/login', request.url)
        loginUrl.searchParams.set('callbackUrl', request.nextUrl.pathname)
        return NextResponse.redirect(loginUrl)
    }

    // Protect API routes
    if (request.nextUrl.pathname.startsWith('/api') && !token) {
        // Allow public API routes if needed (e.g. webhooks, auth endpoints)
        const isPublicApi = request.nextUrl.pathname.startsWith('/api/v1/auth') ||
            request.nextUrl.pathname.startsWith('/api/v1/health');

        if (!isPublicApi) {
            return NextResponse.json(
                { error: 'Unauthorized', message: 'No autenticado: Token requerido' },
                { status: 401 }
            );
        }
    }

    return NextResponse.next()
}

export const config = {
    matcher: [
        '/dashboard/:path*',
        '/login',
        '/api/:path*'
    ],
}
