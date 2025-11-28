import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { getToken } from 'next-auth/jwt'

export async function middleware(request: NextRequest) {
    console.log('🔒 [MIDDLEWARE] Checking authentication for:', request.nextUrl.pathname);

    const token = await getToken({
        req: request,
        secret: process.env.NEXTAUTH_SECRET,
        // NextAuth v5 uses this cookie name format
        cookieName: process.env.NODE_ENV === 'production'
            ? '__Secure-authjs.session-token'
            : 'authjs.session-token'
    })

    console.log('🔒 [MIDDLEWARE] Token found:', !!token);
    if (token) {
        console.log('🔒 [MIDDLEWARE] User:', token.email);
    }

    const isAuthPage = request.nextUrl.pathname.startsWith('/login')
    const isDashboardPage = request.nextUrl.pathname.startsWith('/dashboard')
    const isApiPage = request.nextUrl.pathname.startsWith('/api')

    // Redirect authenticated users away from login page
    if (isAuthPage && token) {
        console.log('🔒 [MIDDLEWARE] Redirecting authenticated user to dashboard');
        return NextResponse.redirect(new URL('/dashboard', request.url))
    }

    // Protect dashboard routes
    if (isDashboardPage && !token) {
        console.log('🔒 [MIDDLEWARE] No token, redirecting to login');
        const loginUrl = new URL('/login', request.url)
        loginUrl.searchParams.set('callbackUrl', request.nextUrl.pathname)
        return NextResponse.redirect(loginUrl)
    }

    return NextResponse.next()
}

export const config = {
    matcher: [
        '/dashboard/:path*',
        '/login',
        // Add other protected routes here if needed
    ],
}
