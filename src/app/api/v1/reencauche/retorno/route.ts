import { NextResponse } from 'next/server';
import { apiHandler } from '@/lib/utils/api-handler';
import { ReencaucheService } from '@/lib/services/reencauche.service';
import { z } from 'zod';

const service = new ReencaucheService();

const schema = z.object({
    neumaticoId: z.string().uuid(),
    profundidadNueva: z.number().min(0),
    proveedorId: z.string().uuid(),
    costo: z.number().min(0),
    almacenDestinoId: z.string().uuid(),
    disenoBanda: z.string().optional()
});

export const POST = apiHandler(async (req, session, context, body) => {
    const data = body;

    if (!session.user.empresa_id) throw new Error("Empresa ID requerido");

    const result = await service.registrarRetorno(
        data.neumaticoId,
        {
            profundidad_nueva: data.profundidadNueva,
            proveedor_id: data.proveedorId,
            costo: data.costo,
            almacen_destino_id: data.almacenDestinoId,
            diseno_banda: data.disenoBanda
        },
        session.user.id,
        session.user.empresa_id
    );

    return NextResponse.json(result);
}, { schema });
