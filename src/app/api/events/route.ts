import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/lib/auth/auth';
import { sseEmitter } from '@/lib/services/sse-emitter.service';
import { randomUUID } from 'crypto';

/**
 * Server-Sent Events endpoint for real-time updates
 * 
 * Clients connect here and receive push notifications when data changes.
 * This replaces polling with event-driven updates.
 */
export async function GET(req: NextRequest) {
    try {
        // Authenticate the user
        const session = await auth();

        if (!session?.user?.id) {
            return NextResponse.json(
                { error: 'Unauthorized', message: 'Authentication required' },
                { status: 401 }
            );
        }

        const encoder = new TextEncoder();
        const clientId = randomUUID();

        // Get empresa_id safely
        const empresaId = (session.user as any).empresa_id || '';

        // Create a readable stream for SSE
        const stream = new ReadableStream({
            start(controller) {
                // Register client with the SSE emitter
                sseEmitter.addClient({
                    id: clientId,
                    userId: session.user!.id!,
                    empresaId,
                    controller,
                });

                // Send initial connection message
                const data = JSON.stringify({
                    type: 'connected',
                    timestamp: Date.now(),
                    clientId,
                });
                controller.enqueue(encoder.encode(`data: ${data}\n\n`));

                // Keep-alive ping every 30 seconds
                const keepAlive = setInterval(() => {
                    try {
                        controller.enqueue(encoder.encode(`: ping\n\n`));
                    } catch {
                        clearInterval(keepAlive);
                    }
                }, 30000);

                // Clean up on close
                req.signal.addEventListener('abort', () => {
                    clearInterval(keepAlive);
                    sseEmitter.removeClient(clientId);
                    try {
                        controller.close();
                    } catch { /* ignore */ }
                });
            },
        });

        return new Response(stream, {
            headers: {
                'Content-Type': 'text/event-stream',
                'Cache-Control': 'no-cache, no-transform',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no',
            },
        });
    } catch (error) {
        console.error('[SSE] Endpoint error:', error);
        return NextResponse.json(
            { error: 'Internal Server Error' },
            { status: 500 }
        );
    }
}

// Disable static generation for this route
export const dynamic = 'force-dynamic';
export const runtime = 'nodejs'; // Force Node.js runtime for SSE
