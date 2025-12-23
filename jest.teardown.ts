/**
 * Jest Global Teardown
 * Ensures all database connections are properly closed after all tests complete
 */
import { prisma } from './src/lib/prisma';

export default async function globalTeardown() {
    // Ensure any lingering Prisma connections are closed
    await prisma.$disconnect();
}
