'use client';

import { DndContext, DragEndEvent, DragOverlay, useSensor, useSensors, PointerSensor } from '@dnd-kit/core';
import { useState } from 'react';
import { InventorySidebar } from '@/components/fleet/inventory-sidebar';
import { VehicleSchematic } from '@/components/vehicle/vehicle-schematic';
import { useOptimisticFleet } from '@/hooks/use-optimistic-fleet';
import { INeumatico } from '@/types/domain/neumatico.types';
import { IVehiculo } from '@/types/domain/vehiculo.types';

interface MontajeClientProps {
    vehiculo: any; // Accepts IVehiculo or VehiculoResponse
    stock: INeumatico[];
    neumaticosInstalados: INeumatico[];
}

export default function MontajeClient({ vehiculo, stock, neumaticosInstalados }: MontajeClientProps) {
    const { tires, mountTire } = useOptimisticFleet(neumaticosInstalados);
    const [activeDragItem, setActiveDragItem] = useState<any>(null);

    const sensors = useSensors(
        useSensor(PointerSensor, {
            activationConstraint: {
                distance: 8,
            },
        })
    );

    const handleDragStart = (event: any) => {
        setActiveDragItem(event.active.data.current?.neumatico);
    };

    const handleDragEnd = (event: DragEndEvent) => {
        const { active, over } = event;
        setActiveDragItem(null);

        if (!over) return;

        // Si soltamos un neumático de inventario sobre una posición del esquema
        if (active.data.current?.type === 'INVENTORY_TIRE') {
            const neumatico = active.data.current.neumatico;
            const posicionId = over.id;

            // ¡Aquí ocurre la magia instantánea!
            mountTire(neumatico, posicionId as string, vehiculo.id);
        }
    };

    return (
        <DndContext id="montaje-dnd-context" sensors={sensors} onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
            <div className="flex h-[calc(100vh-4rem)] overflow-hidden">

                {/* Panel Izquierdo: Inventario */}
                <InventorySidebar neumaticos={stock} />

                {/* Panel Central: Camión */}
                <div className="flex-1 p-8 bg-slate-100 overflow-auto flex flex-col items-center">
                    <h1 className="text-2xl font-bold mb-6 text-slate-800">Montaje de Neumáticos - {vehiculo.placa}</h1>
                    <div className="bg-white p-8 rounded-xl shadow-sm">
                        <VehicleSchematic
                            vehiculo={vehiculo}
                            neumaticos={tires} // Versión optimista
                            isInteractive={true}
                            draggingRetread={activeDragItem?.es_reencauchado}
                        />
                    </div>
                </div>

                {/* Overlay para que se vea la tarjeta mientras la arrastras por el aire */}
                <DragOverlay>
                    {activeDragItem ? (
                        <div className="w-32 bg-blue-600 text-white p-2 rounded-lg shadow-2xl opacity-90 border-2 border-blue-400 rotate-3 cursor-grabbing">
                            <div className="font-bold text-sm">{activeDragItem.numero_serie}</div>
                            {/* Assuming marca and medida are available or optional chaining */}
                            <div className="text-[10px] opacity-90">{activeDragItem.marca}</div>
                            <div className="mt-1 text-[9px] bg-white/20 px-1 rounded w-fit">
                                {activeDragItem.modelo?.medida || activeDragItem.medida}
                            </div>
                        </div>
                    ) : null}
                </DragOverlay>

            </div>
        </DndContext>
    );
}
