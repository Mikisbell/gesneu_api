'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import { useDroppable } from '@dnd-kit/core';

interface VehicleSchematicProps {
    vehiculo: any;
    // Ahora recibimos los neumáticos optimistas, no los del vehículo directamente
    neumaticos?: any[];
    onPositionClick?: (posicionId: string, neumaticoId?: string) => void;
    isInteractive?: boolean; // Nuevo prop para activar el modo Drag & Drop
    draggingRetread?: boolean; // Nuevo prop para validación visual
}

export function VehicleSchematic({
    vehiculo,
    neumaticos,
    onPositionClick,
    isInteractive = false,
    draggingRetread = false
}: VehicleSchematicProps) {
    if (!vehiculo || !vehiculo.tipo_vehiculo?.configuraciones) {
        return <div className="text-center p-4">No hay configuración disponible.</div>;
    }

    const configuraciones = vehiculo.tipo_vehiculo.configuraciones;
    // Usamos la lista optimista si existe, si no, la del vehículo
    const currentTires = neumaticos || vehiculo.neumaticos_instalados || [];

    const getTireInPosition = (posicionId: string) => {
        return currentTires.find((n: any) => n.ubicacion_posicion_id === posicionId);
    };

    // Separar ejes regulares de ejes de repuesto (Tipo OTRO)
    const regularAxles = configuraciones.filter((e: any) => e.tipo_eje !== 'OTRO');
    const spareAxles = configuraciones.filter((e: any) => e.tipo_eje === 'OTRO');

    return (
        <div className="flex flex-col items-center gap-8 p-6 bg-slate-50 rounded-lg border min-h-[500px]">
            <div className="text-xl font-bold text-slate-800 border-b-2 border-slate-800 pb-1 px-4">
                {vehiculo.placa}
            </div>

            {/* ESQUEMA PRINCIPAL (Ejes Regulares) */}
            <div className="flex flex-col gap-12 w-full max-w-3xl items-center">
                {regularAxles.map((eje: any) => (
                    <div key={eje.id} className="relative w-full flex justify-center">
                        {/* Línea de Eje */}
                        <div className="absolute top-1/2 left-0 w-full h-1 bg-slate-300 -z-10 hidden md:block" />

                        <div className="flex gap-8 md:gap-16 items-center bg-slate-50 px-4 z-0">
                            {/* Lado Izquierdo */}
                            <div className="flex gap-2">
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
                                            draggingRetread={draggingRetread}
                                        />
                                    ))}
                            </div>

                            {/* Indicador de Eje */}
                            <div className="flex flex-col items-center justify-center w-24 h-24 rounded-full border-4 border-slate-300 bg-white text-slate-600 shadow-sm z-10">
                                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Eje {eje.numero_eje}</span>
                                <span className="text-[10px] font-bold text-blue-600 mt-1">{eje.tipo_eje}</span>
                            </div>

                            {/* Lado Derecho */}
                            <div className="flex gap-2">
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
                                            draggingRetread={draggingRetread}
                                        />
                                    ))}
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* ZONA DE REPUESTOS (Ejes Tipo OTRO) */}
            {spareAxles.length > 0 && (
                <div className="mt-8 w-full max-w-3xl border-t-2 border-dashed border-slate-300 pt-8">
                    <h3 className="text-center text-sm font-bold text-slate-500 uppercase tracking-widest mb-6">
                        Zona de Repuestos (Portallantas)
                    </h3>
                    <div className="flex flex-wrap justify-center gap-8">
                        {spareAxles.map((eje: any) => (
                            <div key={eje.id} className="flex gap-4 p-4 bg-slate-100 rounded-xl border border-slate-200">
                                {eje.posiciones.map((posicion: any) => (
                                    <DroppablePosition
                                        key={posicion.id}
                                        posicion={posicion}
                                        neumatico={getTireInPosition(posicion.id)}
                                        eje={eje}
                                        onClick={() => onPositionClick && onPositionClick(posicion.id)}
                                        isInteractive={isInteractive}
                                        draggingRetread={draggingRetread}
                                    />
                                ))}
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

// --- SUB-COMPONENTE CON DROPPABLE ---

interface DroppablePositionProps {
    posicion: any;
    neumatico: any;
    eje: any;
    onClick: () => void;
    isInteractive: boolean;
    draggingRetread?: boolean;
}

function DroppablePosition({ posicion, neumatico, eje, onClick, isInteractive, draggingRetread }: DroppablePositionProps) {
    // 1. Hook useDroppable: Convierte este div en una zona de aterrizaje
    const { setNodeRef, isOver } = useDroppable({
        id: posicion.id, // El ID de la posición será lo que recibamos en 'handleDragEnd'
        disabled: !isInteractive || !!neumatico, // Deshabilitar si ya tiene llanta (o lógica de swap futura)
        data: {
            acceptsRetread: eje.permite_reencauchados, // Metadatos para validación visual
            type: 'POSITION'
        }
    });

    const isOccupied = !!neumatico;
    const isRetreadForbidden = !eje.permite_reencauchados;

    // Lógica de validación visual
    const showForbidden = draggingRetread && isRetreadForbidden;
    const showAllowed = draggingRetread && !isRetreadForbidden;

    return (
        <div
            ref={setNodeRef} // CONECTAR EL REF AQUÍ
            onClick={onClick}
            className={cn(
                "relative flex flex-col items-center justify-center w-20 h-32 md:w-24 md:h-40 transition-all rounded-md overflow-hidden",
                // Estilos Base
                isOccupied
                    ? "bg-gradient-to-b from-blue-600 to-blue-800 shadow-lg border border-blue-900 cursor-grab"
                    : "bg-slate-100 border-2 border-dashed border-slate-300 hover:border-blue-400 hover:bg-blue-50 cursor-pointer",

                // Estilos Interactivos (Drag & Drop)
                isOver && !isOccupied && !showForbidden && "bg-green-100 border-green-500 scale-110 shadow-[0_0_15px_rgba(34,197,94,0.5)] z-20",

                // Feedback Visual de Validación (Semáforo)
                !isOccupied && showForbidden && "opacity-50 bg-slate-200 border-slate-300 cursor-not-allowed grayscale",
                !isOccupied && showAllowed && isInteractive && "border-green-400 bg-green-50/50",

                isOver && showForbidden && "bg-red-100 border-red-500 ring-2 ring-red-400 scale-105", // Feedback fuerte al intentar soltar en prohibido
            )}
        >
            <div className="z-10 flex flex-col items-center text-center p-1 w-full h-full justify-between py-2 pointer-events-none">
                {isOccupied ? (
                    <>
                        <div className="bg-white/95 text-blue-900 text-xs font-bold px-1.5 py-0.5 rounded shadow-sm w-[90%] truncate">
                            {neumatico.numero_serie}
                        </div>
                        <div className="flex flex-col gap-1 w-full items-center">
                            <Badge variant="secondary" className="text-[9px] h-4 px-1 bg-blue-900/50 text-white border-none">
                                {neumatico.modelo?.medida || neumatico.medida}
                            </Badge>
                            {neumatico.es_reencauchado && (
                                <Badge variant="outline" className="text-[8px] h-3.5 px-1 border-orange-300 text-orange-200 bg-orange-900/30">
                                    REENC.
                                </Badge>
                            )}
                        </div>
                    </>
                ) : (
                    <div className="text-slate-400 text-xs font-medium flex flex-col items-center justify-center h-full gap-2">
                        {isOver ? (
                            <span className="text-green-600 font-bold scale-125 transition-transform">SOLTAR</span>
                        ) : (
                            <>
                                <span className="font-bold text-slate-500">Pos. {posicion.numero_posicion}</span>
                                {isRetreadForbidden && (
                                    <span className="text-[8px] text-red-400 bg-red-50 px-1 rounded border border-red-100">
                                        Solo Nuevos
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
