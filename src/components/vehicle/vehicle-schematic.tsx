import React from 'react';
import { Card } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';

interface VehicleSchematicProps {
    vehiculo: any; // Using any for now to avoid complex type imports, but should be typed properly
    onPositionClick: (posicionId: string, neumaticoId?: string) => void;
}

export function VehicleSchematic({ vehiculo, onPositionClick }: VehicleSchematicProps) {
    if (!vehiculo || !vehiculo.tipo_vehiculo?.configuraciones) {
        return <div className="text-center p-4">No hay configuración disponible para este vehículo.</div>;
    }

    const configuraciones = vehiculo.tipo_vehiculo.configuraciones;
    const neumaticosInstalados = vehiculo.neumaticos_instalados || [];

    // Helper to find tire in a position
    const getTireInPosition = (posicionId: string) => {
        return neumaticosInstalados.find((n: any) => n.ubicacion_posicion_id === posicionId);
    };

    return (
        <div className="flex flex-col items-center gap-8 p-6 bg-slate-50 rounded-lg border min-h-[500px]">
            <div className="text-xl font-bold text-slate-800 border-b-2 border-slate-800 pb-1 px-4">
                {vehiculo.placa}
            </div>

            <div className="flex flex-col gap-12 w-full max-w-3xl items-center">
                {configuraciones.map((eje: any) => (
                    <div key={eje.id} className="relative w-full flex justify-center">
                        {/* Axle Line */}
                        <div className="absolute top-1/2 left-0 w-full h-1 bg-slate-300 -z-10 hidden md:block" />

                        <div className="flex gap-8 md:gap-16 items-center bg-slate-50 px-4 z-0">
                            {/* Left Side */}
                            <div className="flex gap-2">
                                {eje.posiciones
                                    .filter((p: any) => p.lado_vehiculo === 'IZQUIERDO')
                                    .sort((a: any, b: any) => a.numero_posicion - b.numero_posicion) // Outer to Inner usually? Need to check logic
                                    .map((posicion: any) => {
                                        const neumatico = getTireInPosition(posicion.id);
                                        return (
                                            <TireComponent
                                                key={posicion.id}
                                                posicion={posicion}
                                                neumatico={neumatico}
                                                onClick={() => onPositionClick(posicion.id, neumatico?.id)}
                                            />
                                        );
                                    })}
                            </div>

                            {/* Axle Indicator */}
                            <div className="flex flex-col items-center justify-center w-16 h-16 rounded-full border-4 border-slate-300 bg-white text-slate-500 font-bold">
                                Eje {eje.numero_eje}
                            </div>

                            {/* Right Side */}
                            <div className="flex gap-2">
                                {eje.posiciones
                                    .filter((p: any) => p.lado_vehiculo === 'DERECHO')
                                    .sort((a: any, b: any) => a.numero_posicion - b.numero_posicion)
                                    .map((posicion: any) => {
                                        const neumatico = getTireInPosition(posicion.id);
                                        return (
                                            <TireComponent
                                                key={posicion.id}
                                                posicion={posicion}
                                                neumatico={neumatico}
                                                onClick={() => onPositionClick(posicion.id, neumatico?.id)}
                                            />
                                        );
                                    })}
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

interface TireComponentProps {
    posicion: any;
    neumatico: any;
    onClick: () => void;
}

function TireComponent({ posicion, neumatico, onClick }: TireComponentProps) {
    const isOccupied = !!neumatico;

    return (
        <div
            onClick={onClick}
            className={cn(
                "relative flex flex-col items-center justify-center w-20 h-32 md:w-24 md:h-40 transition-all cursor-pointer hover:scale-105",
                isOccupied
                    ? "bg-blue-600 shadow-lg"
                    : "bg-slate-100 border-2 border-dashed border-slate-300 hover:border-blue-400"
            )}
        >
            {/* Tire Tread Pattern Effect */}
            {isOccupied && (
                <div className="absolute inset-y-0 left-2 right-2 border-x border-blue-500/30" />
            )}

            <div className="z-10 flex flex-col items-center text-center p-1 w-full h-full justify-between py-2">
                {isOccupied ? (
                    <>
                        <div className="bg-white/90 text-blue-900 text-xs font-bold px-1 rounded w-full truncate">
                            {neumatico.numero_serie}
                        </div>

                        <div className="flex flex-col gap-0.5 text-white text-[10px] font-medium">
                            <span>{neumatico.profundidad_actual_mm} mm</span>
                            <span>{neumatico.presion_actual_psi} PSI</span>
                        </div>

                        <Badge variant="secondary" className="text-[9px] h-4 px-1 bg-blue-800 text-white border-none">
                            {neumatico.modelo?.medida}
                        </Badge>
                    </>
                ) : (
                    <div className="text-slate-400 text-xs font-medium flex flex-col items-center justify-center h-full">
                        <span>Pos. {posicion.numero_posicion}</span>
                        <span className="text-[10px] mt-1">Vacío</span>
                    </div>
                )}
            </div>
        </div>
    );
}
