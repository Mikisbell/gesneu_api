'use client';

import { useDraggable } from '@dnd-kit/core';
import { CSS } from '@dnd-kit/utilities';
import { INeumatico } from '@/types/domain/neumatico.types';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { toNumber } from '@/lib/utils/decimal';

interface DraggableTireProps {
    neumatico: INeumatico;
}

export function DraggableTire({ neumatico }: DraggableTireProps) {
    // Configuración de DND Kit
    const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
        id: `tire-${neumatico.id}`, // ID único para el sistema
        data: {
            type: 'INVENTORY_TIRE', // Identificador de tipo para saber qué estamos soltando
            neumatico, // Pasamos el objeto completo para usarlo al soltar
        },
    });

    // Estilos dinámicos para el movimiento
    const style = {
        transform: CSS.Translate.toString(transform),
        opacity: isDragging ? 0.5 : 1, // Se hace semitransparente al arrastrar
        zIndex: isDragging ? 50 : 'auto',
    };

    // Lógica de color según estado (Semáforo de salud)
    const getHealthColor = (mm: number) => {
        if (mm > 10) return 'bg-green-500'; // Nuevo
        if (mm > 5) return 'bg-yellow-500'; // Usado
        return 'bg-red-500 animate-pulse';  // Crítico
    };

    return (
        <div
            ref={setNodeRef}
            style={style}
            {...listeners}
            {...attributes}
            className={cn(
                "relative p-3 mb-2 bg-white rounded-lg border shadow-sm cursor-grab active:cursor-grabbing hover:shadow-md transition-all select-none group",
                isDragging && "ring-2 ring-blue-500 shadow-xl opacity-80",
                // Borde naranja si es reencauchada para diferenciar visualmente
                neumatico.es_reencauchado ? "border-l-4 border-l-orange-400" : "border-l-4 border-l-blue-500"
            )}
        >
            <div className="pl-2 flex justify-between items-start">
                <div>
                    <div className="flex items-center gap-1.5">
                        <p className="font-bold text-sm text-slate-800">{neumatico.numero_serie}</p>
                        {/* Badge distintivo */}
                        {neumatico.es_reencauchado && (
                            <span className="text-[9px] font-bold bg-orange-100 text-orange-700 px-1.5 py-0.5 rounded-full border border-orange-200">
                                R{neumatico.reencauches_realizados}
                            </span>
                        )}
                    </div>
                    <p className="text-xs text-slate-500 mt-0.5">{neumatico.modelo?.nombre_modelo}</p>
                </div>

                {/* Indicador de Profundidad */}
                <Badge variant="outline" className={cn(
                    "text-[10px] h-5",
                    toNumber(neumatico.profundidad_remanente_actual_mm) < 5 ? "border-red-200 bg-red-50 text-red-700" : "border-slate-200"
                )}>
                    {toNumber(neumatico.profundidad_remanente_actual_mm)}mm
                </Badge>
            </div>

            {/* Detalles extra (Marca, DOT) */}
            <div className="pl-2 mt-2 flex gap-2 text-[10px] text-slate-400">
                <span>DOT: {neumatico.dot}</span>
                <span>•</span>
                <span>{neumatico.modelo?.medida}</span>
            </div>
        </div>
    );
}
