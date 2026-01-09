import { NextResponse } from 'next/server';

/**
 * @swagger
 * /api/v1/health:
 *   get:
 *     summary: Health check
 *     description: Returns 200 OK if service is up.
 *     tags: [System]
 *     responses:
 *       200:
 *         description: Service is healthy
 */
export async function GET() {
    return NextResponse.json({
        status: 'ok',
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
    });
}
