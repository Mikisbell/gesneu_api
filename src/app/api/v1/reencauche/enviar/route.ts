import { NextResponse } from 'next/server';
import { apiHandler } from '@/lib/utils/api-handler';
import { ReencaucheService } from '@/lib/services/reencauche.service';
import { z } from 'zod';

const service = new ReencaucheService();

const schema = z.object({
    neumaticoId: z.string().uuid(),
    proveedorId: z.string().uuid(),
    notas: z.string().optional()
});

export const POST = apiHandler(
    async (req, session, context, body) => {
        const data = schema.parse(body);

        if (!session.user.empresa_id) throw new Error("Empresa ID requerido");

        const result = await service.registrarEnvio(
            data.neumaticoId,
            data.proveedorId,
            session.user.id,
            session.user.empresa_id
        );

        return NextResponse.json(result);
    }
);
