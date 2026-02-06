'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Loader2, Info } from 'lucide-react';
import Link from 'next/link';

interface TireCell {
    serie: string;
    mm: number;
    estado: 'OK' | 'WARNING' | 'CRITICAL';
    color: string;
}

interface VehicleRow {
    placa: string;
    tipo: string;
    neumaticos: Record<string, TireCell>;
}

// Mapa de posiciones visual (simplificado para MVP tractor 6x4 + remolque)
// En producción esto debería venir de la configuración dinámica del tipo de vehículo
const POS_ORDER = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'];

export default function SemaforoPage() {
    const { data: matrix, isLoading, error } = useQuery<VehicleRow[]>({
        queryKey: ['reporte-semaforo'],
        queryFn: () => apiClient<VehicleRow[]>('/reportes/flota/semaforo'),
    });

    if (error) return <div className="p-8 text-center text-red-500">Error cargando matriz</div>;
    if (isLoading) return <div className="p-8 flex justify-center"><Loader2 className="animate-spin h-8 w-8" /></div>;

    return (
        <div className="space-y-6 container mx-auto py-6">
            <div className="flex items-center gap-4">
                <Link href="/dashboard/reportes">
                    <Button variant="ghost" size="icon">
                        <ArrowLeft className="h-4 w-4" />
                    </Button>
                </Link>
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Semáforo de Flota</h1>
                    <p className="text-muted-foreground">Mapa de calor de inspecciones. Rojo = Crítico (Cambio inmediato).</p>
                </div>
            </div>

            <div className="flex gap-4 mb-4">
                <div className="flex items-center gap-2"><div className="w-4 h-4 rounded bg-green-500"></div> <span className="text-sm">Operativo</span></div>
                <div className="flex items-center gap-2"><div className="w-4 h-4 rounded bg-amber-500"></div> <span className="text-sm">Advertencia (Prox. Cambio)</span></div>
                <div className="flex items-center gap-2"><div className="w-4 h-4 rounded bg-red-500"></div> <span className="text-sm">Crítico (Retiro)</span></div>
            </div>

            <div className="grid gap-6">
                {matrix?.map((vehicle) => (
                    <Card key={vehicle.placa} className="overflow-hidden">
                        <CardHeader className="bg-muted/50 py-3">
                            <div className="flex justify-between items-center">
                                <CardTitle className="text-lg">{vehicle.placa}</CardTitle>
                                <span className="text-sm text-muted-foreground">{vehicle.tipo}</span>
                            </div>
                        </CardHeader>
                        <CardContent className="p-4">
                            <div className="grid grid-cols-6 md:grid-cols-12 gap-2">
                                {POS_ORDER.map((posCode) => {
                                    const tire = vehicle.neumaticos[posCode];
                                    return (
                                        <div
                                            key={posCode}
                                            className={`
                                                relative p-2 rounded border flex flex-col items-center justify-center min-h-[80px] text-center transition-colors
                                                ${!tire ? 'bg-gray-50 border-dashed opacity-50' : ''}
                                                ${tire?.estado === 'CRITICAL' ? 'bg-red-50 border-red-200' : ''}
                                                ${tire?.estado === 'WARNING' ? 'bg-amber-50 border-amber-200' : ''}
                                            `}
                                        >
                                            <span className="absolute top-1 left-1 text-[10px] text-muted-foreground font-mono">{posCode}</span>
                                            {tire ? (
                                                <>
                                                    <span className={`text-xl font-bold mb-1`} style={{ color: tire.color }}>
                                                        {tire.mm}<span className="text-[10px]">mm</span>
                                                    </span>
                                                    <span className="text-[10px] text-muted-foreground truncate w-full">{tire.serie}</span>
                                                </>
                                            ) : (
                                                <span className="text-xs text-muted-foreground">-</span>
                                            )}
                                        </div>
                                    );
                                })}
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>
        </div>
    );
}
