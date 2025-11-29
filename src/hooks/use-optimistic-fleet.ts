'use client';

import { useOptimistic, useTransition } from 'react';
import { toast } from 'sonner';
import { useRouter } from 'next/navigation';
import { INeumatico } from '@/types/domain/neumatico.types';
import { TipoEventoNeumaticoEnum } from '@prisma/client';

// Tipos para las acciones que la UI puede "predecir"
type FleetAction =
    | { type: 'MOUNT'; neumatico: INeumatico; posicionId: string; fecha: Date }
    | { type: 'DISMOUNT'; neumaticoId: string; posicionId: string; fecha: Date }
    | { type: 'ROTATE'; origenPosId: string; destinoPosId: string; fecha: Date };

export function useOptimisticFleet(initialTires: INeumatico[]) {
    const router = useRouter();
    const [isPending, startTransition] = useTransition();

    // 1. EL ESTADO OPTIMISTA
    // Este es el "gemelo digital" que se actualiza instantáneamente
    const [optimisticTires, applyOptimisticAction] = useOptimistic(
        initialTires,
        (currentTires, action: FleetAction) => {
            switch (action.type) {
                case 'MOUNT':
                    // Agregamos visualmente el neumático a la posición
                    return [
                        ...currentTires,
                        {
                            ...action.neumatico,
                            ubicacion_posicion_id: action.posicionId,
                            estado_actual: 'INSTALADO'
                        } as INeumatico
                    ];

                case 'DISMOUNT':
                    // Lo quitamos del esquema visualmente
                    return currentTires.filter(t => t.id !== action.neumaticoId);

                case 'ROTATE':
                    // Intercambiamos posiciones visualmente (Swap complejo)
                    const tireA = currentTires.find(t => t.ubicacion_posicion_id === action.origenPosId);
                    const tireB = currentTires.find(t => t.ubicacion_posicion_id === action.destinoPosId);

                    return currentTires.map(t => {
                        if (t.id === tireA?.id) return { ...t, ubicacion_posicion_id: action.destinoPosId };
                        if (t.id === tireB?.id) return { ...t, ubicacion_posicion_id: action.origenPosId };
                        return t;
                    });

                default:
                    return currentTires;
            }
        }
    );

    // 2. LAS FUNCIONES "TRIGGER" (Disparadores)
    // Estas son las que tu UI llamará al hacer Drag & Drop

    const mountTire = async (neumatico: INeumatico, posicionId: string, vehiculoId: string) => {
        // A. Predicción Visual (Instantáneo)
        startTransition(() => {
            applyOptimisticAction({
                type: 'MOUNT',
                neumatico,
                posicionId,
                fecha: new Date()
            });
        });

        // B. Realidad Backend (Asíncrono)
        try {
            const response = await fetch('/api/v1/neumaticos/eventos', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    tipo_evento: TipoEventoNeumaticoEnum.INSTALACION,
                    neumatico_id: neumatico.id,
                    vehiculo_id: vehiculoId,
                    posicion_montaje_id: posicionId,
                    fecha_evento: new Date().toISOString()
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error("Backend Error:", errorData);
                throw new Error(errorData.error || 'Falló el montaje');
            }

            toast.success(`Neumático ${neumatico.numero_serie} montado`);
            router.refresh(); // Sincroniza la verdad oficial

        } catch (error) {
            // C. Rollback Automático (Si falla, React revierte el estado optimista solo)
            toast.error('Error al montar: Revirtiendo cambios...');
            console.error(error);
        }
    };

    const rotateTires = async (origenPosId: string, destinoPosId: string, vehiculoId: string) => {
        const tire = optimisticTires.find(t => t.ubicacion_posicion_id === origenPosId);
        if (!tire) return;

        startTransition(() => {
            applyOptimisticAction({ type: 'ROTATE', origenPosId, destinoPosId, fecha: new Date() });
        });

        try {
            const response = await fetch('/api/v1/neumaticos/eventos', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    tipo_evento: TipoEventoNeumaticoEnum.ROTACION,
                    neumatico_id: tire.id,
                    vehiculo_id: vehiculoId,
                    posicion_montaje_id: destinoPosId,
                    // kilometraje_vehiculo: ... (puedes pedirlo en un modal antes si es obligatorio)
                })
            });

            if (!response.ok) throw new Error('Falló la rotación');
            toast.success('Rotación registrada');
            router.refresh();

        } catch (error) {
            toast.error('Error en rotación: Posición inválida o regla de negocio');
        }
    };

    return {
        tires: optimisticTires, // Usa ESTO en tu render, no la data raw
        mountTire,
        rotateTires,
        isPending
    };
}
