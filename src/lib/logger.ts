
import prisma from '@/lib/prisma';
import { LogLevel } from '@prisma/client';

export type LogContext = Record<string, any>;

/**
 * System Logger
 * Stores critical logs in Postgres and prints to console.
 * Designed to be "fire and forget" to avoid blocking main execution.
 */
class LoggerService {

    private async saveToDB(level: LogLevel, message: String, context?: LogContext, userId?: string) {
        // In development, just console log is enough usually, but for testing we can save.
        // In production, we assume we want to save everything >= WARN or specific INFO

        // Safety check: Don't crash app if logging fails
        try {
            await prisma.systemLog.create({
                data: {
                    level,
                    message: String(message).substring(0, 2000), // Prevent huge logs
                    context: context ? (context as any) : undefined,
                    user_id: userId
                }
            });
        } catch (error) {
            console.error("❌ Logger failed to save to DB:", error);
        }
    }

    async info(message: string, context?: LogContext, userId?: string) {
        console.log(`ℹ️ [INFO] ${message}`, context || '');
        // Optional: Only save critical INFO or always? 
        // Let's save all for now as user requested monitoring
        await this.saveToDB('INFO', message, context, userId);
    }

    async warn(message: string, context?: LogContext, userId?: string) {
        console.warn(`⚠️ [WARN] ${message}`, context || '');
        await this.saveToDB('WARN', message, context, userId);
    }

    async error(message: string, error?: any, context?: LogContext, userId?: string) {
        console.error(`❌ [ERROR] ${message}`, error, context || '');

        const finalContext = {
            ...context,
            error_message: error?.message || String(error),
            stack: error?.stack
        };

        await this.saveToDB('ERROR', message, finalContext, userId);
    }

    async debug(message: string, context?: LogContext) {
        if (process.env.NODE_ENV === 'development') {
            console.debug(`🐞 [DEBUG] ${message}`, context || '');
        }
        // Debug logs usually not saved to DB unless configured
    }
}

export const logger = new LoggerService();
