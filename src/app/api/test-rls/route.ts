import { NextResponse } from 'next/server';
import { getAuthenticatedClient } from '@/lib/prisma-tenant';

export async function GET() {
    try {
        const db = await getAuthenticatedClient();

        // 1. Try to list ALL companies
        // If RLS is working, this should return ONLY the current user's company.
        // If RLS is broken/bypassed, this might return all companies in the DB.
        const companies = await db.empresa.findMany();

        return NextResponse.json({
            status: 'OK',
            message: 'RLS Test - You should only see YOUR company below.',
            count: companies.length,
            data: companies
        });

    } catch (error: any) {
        return NextResponse.json({
            status: 'ERROR',
            message: error.message,
            details: 'Ensure you are logged in.'
        }, { status: 500 });
    }
}
