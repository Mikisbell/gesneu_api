import { NextResponse } from 'next/server';
import { apiHandler } from '@/lib/utils/api-handler';
import { ReencaucheService } from '@/lib/services/reencauche.service';

const service = new ReencaucheService();

export const GET = apiHandler(async (req, session) => {
    if (!session.user.empresa_id) throw new Error("Empresa ID requerido");

    const result = await service.getIndiceReencauchabilidad(session.user.empresa_id);

    return NextResponse.json(result);
});
