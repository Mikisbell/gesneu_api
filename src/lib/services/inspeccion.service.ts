import { prisma } from '@/lib/prisma';
import { CreateInspeccionDTO } from '@/lib/validators/inspeccion.validator';
import { BusinessError } from '@/lib/errors/business.error';
import { TipoEventoNeumaticoEnum, EstadoNeumaticoEnum } from '@prisma/client';
import { AlertasService } from './alertas.service';

const PRESION_MINIMA_PSI = 80; // Umbral mínimo de presión

export class InspeccionService {
    private alertasService = new AlertasService();

    async registrarManual(data: CreateInspeccionDTO, userId: string) {

        // 1. Verificar Neumático
        const neumatico = await prisma.neumatico.findUnique({
            where: { id: data.neumatico_id }
        });

        if (!neumatico) throw BusinessError.notFound('Neumático', data.neumatico_id);
        if (!neumatico.activo) throw BusinessError.badRequest('El neumático no está activo');

        // 2. Registrar Lectura
        const lectura = await prisma.lecturaPresion.create({
            data: {
                neumatico_id: data.neumatico_id,
                presion_psi: data.presion_psi,
                temperatura_c: data.temperatura_c,
                fuente: 'MANUAL',
                creado_por: userId
            }
        });

        // 3. Actualizar Estado Neumático (Snapshot)
        await prisma.neumatico.update({
            where: { id: data.neumatico_id },
            data: {
                presion_actual_psi: data.presion_psi,
                actualizado_en: new Date()
            }
        });

        // 4. Crear Evento de Inspección (Audit Trail completo)
        await prisma.eventoNeumatico.create({
            data: {
                tipo_evento: TipoEventoNeumaticoEnum.INSPECCION,
                neumatico_id: data.neumatico_id,
                fecha_evento: new Date(),
                presion_psi: data.presion_psi,
                notas: data.observaciones || 'Inspección manual de presión',
                creado_por: userId
            }
        });

        // 5. Disparar alerta si presión < mínimo
        await this.alertasService.generarAlertaPresion(
            data.neumatico_id,
            data.presion_psi,
            PRESION_MINIMA_PSI
        );

        return lectura;
    }
}
