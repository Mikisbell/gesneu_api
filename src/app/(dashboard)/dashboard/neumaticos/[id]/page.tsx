'use client';

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useParams, useRouter } from 'next/navigation';
import { neumaticosApi } from '@/lib/api/neumaticos';
import { PressureHistoryChart } from '@/components/charts/PressureHistoryChart';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Thermometer, Gauge } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { DownloadCertificateButton } from '@/components/reports/DownloadCertificateButton';

export default function NeumaticoDetallePage() {
    const params = useParams<{ id: string }>();
    const router = useRouter();
    const id = params.id;

    // React Query para obtener el detalle del neumático
    const { data: neumatico, isLoading } = useQuery({
        queryKey: ['neumatico', id],
        queryFn: async () => {
            const res = await fetch(`/api/v1/neumaticos/${id}`);
            if (!res.ok) throw new Error('Neumático no encontrado');
            const json = await res.json();
            return json.data;
        }
    });

    if (isLoading) return <div className="p-8 space-y-4">
        <Skeleton className="h-12 w-1/3" />
        <Skeleton className="h-[300px] w-full" />
    </div>;

    if (!neumatico) return <div className="p-8">Neumático no encontrado</div>;

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <Button variant="ghost" size="icon" onClick={() => router.back()}>
                        <ArrowLeft className="h-4 w-4" />
                    </Button>
                    <div>
                        <h1 className="text-2xl font-bold tracking-tight">
                            Neumático {neumatico.numero_serie}
                        </h1>
                        <div className="text-muted-foreground flex items-center gap-2">
                            {neumatico.modelo?.nombre} - {neumatico.modelo?.fabricante?.nombre}
                            <Badge variant="outline">{neumatico.estado_actual}</Badge>
                        </div>
                    </div>
                </div>
                {/* Botón de Reporte PDF (Ya implementado) */}
                <div className="flex gap-2">
                    {neumatico.ubicacion_vehiculo_id && (
                        <DownloadCertificateButton vehicleId={neumatico.ubicacion_vehiculo_id} />
                    )}
                </div>
            </div>

            {/* KPIs Rápidos */}
            <div className="grid gap-4 md:grid-cols-3">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Presión Actual</CardTitle>
                        <Gauge className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{neumatico.presion_actual_psi || '-'} psi</div>
                        <p className="text-xs text-muted-foreground">Última lectura manual</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Profundidad</CardTitle>
                        <Thermometer className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{neumatico.profundidad_remanente_actual_mm || '-'} mm</div>
                        <p className="text-xs text-muted-foreground">Remanente promedio</p>
                    </CardContent>
                </Card>
                {/* ... más kpis */}
            </div>

            {/* Gráfico Histórico */}
            <div className="grid gap-4 md:grid-cols-1">
                <PressureHistoryChart neumaticoId={id} />
            </div>
        </div>
    );
}
