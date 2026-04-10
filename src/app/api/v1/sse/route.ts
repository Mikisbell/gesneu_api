import { NextRequest } from 'next/server';
import { requireAuth } from '@/lib/auth/authorization';
import { sseEmitter } from '@/lib/services/sse-emitter.service';

/**
 * @swagger
 * /api/v1/sse:
 *   get:
 *     summary: Server-Sent Events Connection
 *     description: >
 *       Establishes a Server-Sent Events (SSE) connection for real-time dashboard updates.
 *       Clients receive invalidate, alert, and update events when data changes.
 *       The connection is kept alive until the client disconnects.
 *     tags:
 *       - Real-Time
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: SSE connection established
 *         content:
 *           text/event-stream:
 *             schema:
 *               type: string
 *               example: |
 *                 data: {"type":"connected","message":"SSE connection established","clientId":"abc-123","timestamp":1234567890}
 *
 *                 data: {"type":"invalidate","queryKeys":["neumaticos","alertas-unread"],"timestamp":1234567891}
 *       401:
 *         description: No autenticado
 */
export async function GET(request: NextRequest) {
    try {
        const session = await requireAuth();

        const userId = session.user.id;
        const empresaId = session.user.empresa_id || '';

        // Create a ReadableStream for SSE
        const stream = new ReadableStream({
            start(controller) {
                const clientId = `${userId}-${Date.now()}-${Math.random().toString(36).substring(7)}`;

                // Register client with SSE emitter service
                sseEmitter.addClient({
                    id: clientId,
                    userId,
                    controller,
                    empresaId,
                });

                // Send initial connection message
                const welcomeData = JSON.stringify({
                    type: 'connected',
                    message: 'SSE connection established',
                    clientId,
                    timestamp: Date.now(),
                });
                controller.enqueue(new TextEncoder().encode(`data: ${welcomeData}\n\n`));

                // Handle client disconnect
                request.signal.addEventListener('abort', () => {
                    sseEmitter.removeClient(clientId);
                    controller.close();
                });
            },
        });

        return new Response(stream, {
            headers: {
                'Content-Type': 'text/event-stream',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no', // Disable nginx buffering
            },
        });
    } catch (error: any) {
        if (error.message === 'UNAUTHORIZED') {
            return new Response(JSON.stringify({ error: 'No autenticado' }), {
                status: 401,
                headers: { 'Content-Type': 'application/json' },
            });
        }
        console.error('[SSE] Error:', error);
        return new Response(JSON.stringify({ error: 'Error interno del servidor' }), {
            status: 500,
            headers: { 'Content-Type': 'application/json' },
        });
    }
}
