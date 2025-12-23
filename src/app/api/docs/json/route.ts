import { NextResponse } from 'next/server';
import { getApiDocs } from '@/lib/swagger-helper';

export async function GET() {
    const spec = await getApiDocs();
    return NextResponse.json(spec);
}
