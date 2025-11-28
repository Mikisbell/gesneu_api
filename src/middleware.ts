// Middleware commented out - Auth is handled per-endpoint with requireAuth()
// If needed in the future, upgrade to NextAuth v5 middleware pattern

// import { NextResponse } from "next/server"
// import type { NextRequest } from "next/server"

// export function middleware(request: NextRequest) {
//     // Custom middleware logic if needed
//     return NextResponse.next()
// }

// export const config = {
//     matcher: [
//         "/dashboard/:path*",
//         "/api/v1/:path*",
//     ]
// }

export { }; // Make this file a module
