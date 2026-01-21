import { handlers } from '@/lib/auth/auth';

export const runtime = 'nodejs'; // Force Node.js runtime for Prisma compatibility

export const { GET, POST } = handlers;
