import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { getToken } from 'next-auth/jwt'

export async function middleware(request: NextRequest) {
    const token = await getToken({
        req: request,
        secret: process.env.NEXTAUTH_SECRET
    })

    const isAuthPage = request.nextUrl.pathname.startsWith('/login')
    const isDashboardPage = request.nextUrl.pathname.startsWith('/dashboard')
    const isApiPage = request.nextUrl.pathname.startsWith('/api')

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

    return NextResponse.next()
}

export const config = {
    matcher: [
        '/dashboard/:path*',
        '/login',
        // Add other protected routes here if needed
    ],
}
