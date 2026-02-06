
'use server';

import prisma from '@/lib/prisma';
import { LogLevel, Prisma } from '@prisma/client';

export type SystemLogEntry = {
    id: string;
    level: LogLevel;
    message: string;
    context: any;
    user_id: string | null;
    created_at: Date;
    user_email?: string;
};

export async function getSystemLogs(
    page: number = 1,
    pageSize: number = 50,
    level?: LogLevel
) {
    try {
        const where: Prisma.SystemLogWhereInput = level ? { level } : {};

        const [logs, total] = await Promise.all([
            prisma.systemLog.findMany({
                where,
                orderBy: { created_at: 'desc' },
                skip: (page - 1) * pageSize,
                take: pageSize,
                // Include user email if possible, but relation is manual in schema
                // We'll just fetch raw for now, join is expensive if not defined
            }),
            prisma.systemLog.count({ where })
        ]);

        // Basic enrichment (optional): Fetch users if needed manually or just display ID
        return {
            success: true,
            data: logs as SystemLogEntry[],
            pagination: {
                page,
                pageSize,
                total,
                totalPages: Math.ceil(total / pageSize)
            }
        };
    } catch (error) {
        console.error("Error fetching logs:", error);
        return { success: false, error: "Failed to fetch logs" };
    }
}
