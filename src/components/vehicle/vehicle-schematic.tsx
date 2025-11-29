'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import { useDroppable } from '@dnd-kit/core';

interface VehicleSchematicProps {
    vehiculo: any;
    neumaticos?: any[];
    onPositionClick?: (posicionId: string, neumaticoId?: string) => void;
    isInteractive?: boolean;
}

export function VehicleSchematic({
    vehiculo,
    neumaticos,
    onPositionClick,
    isInteractive = false
}: VehicleSchematicProps) {
    if (!vehiculo || !vehiculo.tipo_vehiculo?.configuraciones) {
        return (
            <div className="flex flex-col items-center justify-center h-64 text-slate-400 border-2 border-dashed rounded-lg">
                <p>No hay configuración disponible.</p>
            </div>
        );
    }

    const configuraciones = vehiculo.tipo_vehiculo.configuraciones;
    const currentTires = neumaticos || vehiculo.neumaticos_instalados || [];

    const getTireInPosition = (posicionId: string) => {
        return currentTires.find((n: any) => n.ubicacion_posicion_id === posicionId);
    };

    return (
        <div className="flex flex-col items-center gap-8 p-6 bg-slate-50 rounded-lg border min-h-[500px] shadow-sm">
            <div className="flex flex-col items-center border-b-2 border-slate-200 pb-4 w-full">
                <div className="text-2xl font-bold text-slate-800">{vehiculo.codigo_interno || vehiculo.placa}</div>
                <div className="text-xs text-slate-500 mt-1 uppercase tracking-wider">
                    {vehiculo.marca} {vehiculo.modelo} • {vehiculo.tipo_medicion}
                </div>
            </div>

            <div className="flex flex-col gap-16 w-full max-w-3xl items-center py-8">
                {configuraciones.map((eje: any) => (
                    <div key={eje.id} className="relative w-full flex justify-center group">
                        {/* Línea de Eje */}
                        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 w-[60%] h-3 bg-slate-300 -z-10 rounded-full" />

                        <div className="flex gap-8 md:gap-16 items-center z-0 relative">
                            {/* Lado Izquierdo */}
                            <div className="flex gap-3">
                                {eje.posiciones
                                    .filter((p: any) => p.lado_vehiculo === 'IZQUIERDO')
                                    .sort((a: any, b: any) => a.numero_posicion - b.numero_posicion)
                                    .map((posicion: any) => (
                                        <DroppablePosition
                                            key={posicion.id}
                                            posicion={posicion}
                                            neumatico={getTireInPosition(posicion.id)}
                                            eje={eje}
                                            onClick={() => onPositionClick && onPositionClick(posicion.id)}
                                            isInteractive={isInteractive}
                                        />
                                    ))}
                            </div>

                            {/* Indicador de Eje Central */}
                            <div className="flex flex-col items-center justify-center w-12 h-12 bg-white border-2 border-slate-300 rounded-full shadow-sm z-10">
                                <span className="text-[10px] font-bold text-slate-400">{eje.numero_eje}</span>
                            </div>

                            {/* Lado Derecho */}
                            <div className="flex gap-3">
                                {eje.posiciones
                                    .filter((p: any) => p.lado_vehiculo === 'DERECHO')
                                    .sort((a: any, b: any) => a.numero_posicion - b.numero_posicion)
                                    .map((posicion: any) => (
                                        <DroppablePosition
                                            key={posicion.id}
                                            posicion={posicion}
                                            neumatico={getTireInPosition(posicion.id)}
                                            eje={eje}
                                            onClick={() => onPositionClick && onPositionClick(posicion.id)}
                                            isInteractive={isInteractive}
                                        />
                                    ))}
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

interface DroppablePositionProps {
    posicion: any;
    neumatico: any;
    eje: any;
    onClick: () => void;
    isInteractive: boolean;
}

function DroppablePosition({ posicion, neumatico, eje, onClick, isInteractive }: DroppablePositionProps) {
    const { setNodeRef, isOver, active } = useDroppable({
        id: posicion.id,
        disabled: !isInteractive || !!neumatico,
        data: {
            acceptsRetread: eje.permite_reencauchados,
            type: 'POSITION'
        }
    });

    // Lógica Visual de Validación
    const isOccupied = !!neumatico;
    const isRetreadForbidden = !eje.permite_reencauchados;

    // ¿Lo que arrastran es reencauchado?
    const draggingRetread = active?.data?.current?.neumatico?.es_reencauchado;
    // ¿Es un movimiento inválido? (Arrastrar reencauchado a eje prohibido)
    const isInvalidDrop = isOver && draggingRetread && isRetreadForbidden;

    return (
        <div
            ref={setNodeRef}
            onClick={onClick}
            className={cn(
                "relative flex flex-col items-center justify-center w-20 h-32 md:w-24 md:h-40 transition-all rounded-xl overflow-hidden border-2",
                // Estado Base
                isOccupied
                    ? "bg-slate-800 border-slate-900 shadow-md cursor-pointer hover:scale-105"
                    : "bg-white border-dashed border-slate-300 hover:border-blue-400",

                // Estado Drag & Drop (Feedback Visual)
                isOver && !isOccupied && !isInvalidDrop && "bg-green-50 border-green-500 scale-110 shadow-lg shadow-green-100",
                isInvalidDrop && "bg-red-50 border-red-500 scale-105 shadow-red-100 opacity-70", // Feedback de error
            )}
        >
            <div className="z-10 flex flex-col items-center text-center p-1 w-full h-full justify-between py-3 pointer-events-none">
                {isOccupied ? (
                    <>
                        <div className="w-full px-1">
                            <div className="bg-white text-slate-900 text-[10px] font-bold py-1 rounded shadow-sm truncate">
                                {neumatico.numero_serie}
                            </div>
                        </div>

                        <div className="flex flex-col gap-0.5 w-full">
                            <div className="flex justify-between px-2 text-[9px] text-slate-300 font-mono">
                                <span>DOT</span>
                                <span>{neumatico.dot}</span>
                            </div>

                            {/* Indicador visual de salud (Profundidad) */}
                            <div className="w-full h-1.5 bg-slate-700 rounded-full overflow-hidden mt-1">
                                <div
                                    className={cn("h-full",
                                        (neumatico.profundidad_actual_mm || 0) > 10 ? "bg-green-500" :
                                            (neumatico.profundidad_actual_mm || 0) > 5 ? "bg-yellow-500" : "bg-red-500"
                                    )}
                                    style={{ width: `${Math.min(((neumatico.profundidad_actual_mm || 0) / 20) * 100, 100)}%` }}
                                />
                            </div>
                        </div>

                        <div className="flex gap-1">
                            {neumatico.es_reencauchado && (
                                <Badge variant="destructive" className="text-[8px] h-4 px-1 bg-orange-500 hover:bg-orange-600">
                                    R{neumatico.reencauches_realizados}
                                </Badge>
                            )}
                            <Badge variant="secondary" className="text-[8px] h-4 px-1 bg-slate-600 text-white border-none">
                                {neumatico.profundidad_actual_mm}mm
                            </Badge>
                        </div>
                    </>
                ) : (
                    <div className="text-slate-400 text-xs font-medium flex flex-col items-center justify-center h-full gap-1">
                        {isInvalidDrop ? (
                            <>
                                <span className="text-2xl">🚫</span>
                                <span className="text-[9px] text-red-500 font-bold">No Apto</span>
                            </>
                        ) : isOver ? (
                            <span className="text-green-600 font-bold text-xs animate-pulse">SOLTAR</span>
                        ) : (
                            <>
                                <span className="text-2xl opacity-20">+</span>
                                <span className="text-[10px] uppercase">Pos {posicion.numero_posicion}</span>
                                {isRetreadForbidden && (
                                    <span className="text-[8px] text-amber-600 bg-amber-50 px-1 rounded border border-amber-100 mt-1">
                                        Solo Nuevo
                                    </span>
                                )}
                            </>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
