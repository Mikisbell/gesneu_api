'use client';

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from '@/components/ui/scroll-area';
import { DraggableTire } from './draggable-tire';
import { INeumatico } from '@/types/domain/neumatico.types';
import { Badge } from "@/components/ui/badge";

interface InventorySidebarProps {
    neumaticos: INeumatico[];
}

export function InventorySidebar({ neumaticos = [] }: InventorySidebarProps) {
    // 1. Separación Lógica de Grupos segura
    const isRetread = (n: any) => Boolean(n?.condicion?.esReencauchado || n?.es_reencauchado || n?.esReencauchado);
    const originales = neumaticos.filter(n => !isRetread(n));
    const reencauchados = neumaticos.filter(n => isRetread(n));

    return (
        <div className="w-80 h-[calc(100vh-4rem)] border-r border-slate-200 bg-white flex flex-col shadow-sm z-20">
            <div className="p-4 border-b border-slate-100">
                <h3 className="font-bold text-slate-800 text-lg">Inventario</h3>
                <p className="text-xs text-slate-500">Arrastra al vehículo para montar</p>
            </div>

            {/* 2. Sistema de Pestañas para Grupos */}
            <Tabs defaultValue="nuevas" className="flex-1 flex flex-col">
                <div className="px-4 pt-2">
                    <TabsList className="w-full grid grid-cols-2">
                        <TabsTrigger value="nuevas" className="text-xs">
                            Originales
                            <Badge variant="secondary" className="ml-1.5 h-5 px-1.5 text-[10px] bg-slate-200 text-slate-700">
                                {originales.length}
                            </Badge>
                        </TabsTrigger>
                        <TabsTrigger value="reencauche" className="text-xs">
                            Reencauchadas
                            <Badge variant="secondary" className="ml-1.5 h-5 px-1.5 text-[10px] bg-orange-100 text-orange-700 border-orange-200">
                                {reencauchados.length}
                            </Badge>
                        </TabsTrigger>
                    </TabsList>
                </div>

                {/* Grupo 1: Originales */}
                <TabsContent value="nuevas" className="flex-1 overflow-hidden mt-0">
                    <ScrollArea className="h-full p-3">
                        <div className="space-y-2 pb-4">
                            {originales.length === 0 ? (
                                <EmptyState text="No hay llantas originales en stock" />
                            ) : (
                                originales.map((neumatico) => (
                                    <DraggableTire key={neumatico.id} neumatico={neumatico} />
                                ))
                            )}
                        </div>
                    </ScrollArea>
                </TabsContent>

                {/* Grupo 2: Reencauchadas (Tu requerimiento) */}
                <TabsContent value="reencauche" className="flex-1 overflow-hidden mt-0">
                    <ScrollArea className="h-full p-3 bg-orange-50/30">
                        <div className="space-y-2 pb-4">
                            {reencauchados.length === 0 ? (
                                <EmptyState text="No hay llantas reencauchadas disponibles" />
                            ) : (
                                reencauchados.map((neumatico) => (
                                    <DraggableTire key={neumatico.id} neumatico={neumatico} />
                                ))
                            )}
                        </div>
                    </ScrollArea>
                </TabsContent>
            </Tabs>
        </div>
    );
}

function EmptyState({ text }: { text: string }) {
    return (
        <div className="flex flex-col items-center justify-center py-10 px-4 text-center border-2 border-dashed border-slate-100 rounded-lg bg-slate-50">
            <span className="text-2xl mb-2">📦</span>
            <p className="text-xs text-slate-400 font-medium">{text}</p>
        </div>
    );
}
