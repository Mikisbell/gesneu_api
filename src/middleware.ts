import { withAuth } from "next-auth/middleware"
import { NextResponse } from "next/server"

export default withAuth(
    function middleware(req) {
        // Log request for Vercel/System logs
        console.log(`[${req.method}] ${req.nextUrl.pathname} - User: ${req.nextauth.token?.email || 'Guest'}`)
        return NextResponse.next()
    },
    {
        callbacks: {
            authorized: ({ token }) => !!token,
        },
    }
)

export const config = {
    matcher: [
        "/dashboard/:path*",
        "/api/v1/neumaticos/:path*",
        "/api/v1/operaciones/:path*",
        "/api/v1/vehiculos/:path*",
        "/api/v1/catalogos/:path*",
    ]
}
