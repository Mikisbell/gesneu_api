'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { ColumnDef } from '@tanstack/react-table';
import { DataTable } from '@/components/ui/data-table';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { formatCurrency } from '@/lib/utils/format';
import { ArrowLeft, Loader2, TrendingDown, TrendingUp, AlertCircle } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';

interface PerformanceItem {
    id: string;
    serie: string;
    marca: string;
    modelo: string;
    medida: string;
    vehiculo: string;
    tipo_vehiculo: string;
    estado: string;
    costo_total: number;
    km_actual: number;
    cpk_actual: number;
    prof_actual_mm: number;
    vida_estimada_km: number;
    cpk_proyectado: number;
}

interface PerformanceResponse {
    summary: {
        total_neumaticos: number;
        costo_flota_total: number;
        km_rodados_total: number;
        cpk_flota_promedio: number;
    };
    data: PerformanceItem[];
}

const columns: ColumnDef<PerformanceItem>[] = [
    {
        accessorKey: "serie",
        header: "Serie",
    },
    {
        accessorKey: "marca",
        header: "Marca",
    },
    {
        accessorKey: "modelo",
        header: "Modelo",
        cell: ({ row }) => (
            <div className="flex flex-col">
                <span>{row.original.modelo}</span>
                <span className="text-xs text-muted-foreground">{row.original.medida}</span>
            </div>
        )
    },
    {
        accessorKey: "vehiculo",
        header: "Vehículo",
    },
    {
        accessorKey: "km_actual",
        header: "Km Actual",
        cell: ({ getValue }) => Number(getValue()).toLocaleString(),
    },
    {
        accessorKey: "costo_total",
        header: "Costo Total",
        cell: ({ getValue }) => formatCurrency(Number(getValue())),
    },
    {
        accessorKey: "cpk_actual",
        header: "CPK Actual",
        cell: ({ getValue }) => {
            const val = Number(getValue());
            return (
                <div className={`font-medium ${val > 0.005 ? 'text-red-500' : 'text-green-600'}`}>
                    ${val.toFixed(5)}
                </div>
            )
        },
    },
    {
        accessorKey: "vida_estimada_km",
        header: "Vida Est. (Km)",
        cell: ({ getValue }) => Number(getValue()).toLocaleString(),
    },
    {
        accessorKey: "cpk_proyectado",
        header: "CPK Proy.",
        cell: ({ getValue }) => {
            const val = Number(getValue());
            return <span className="text-muted-foreground">${val.toFixed(5)}</span>;
        }
    },
]

export default function RendimientoPage() {
    const { data, isLoading, error } = useQuery<PerformanceResponse>({
        queryKey: ['reporte-rendimiento'],
        queryFn: () => apiClient<PerformanceResponse>('/reportes/rendimiento'),
    });

    if (error) return <div className="p-8 text-center text-red-500">Error cargando reporte</div>;
    if (isLoading) return <div className="p-8 flex justify-center"><Loader2 className="animate-spin h-8 w-8" /></div>;

    const summary = data?.summary;

    return (
        <div className="space-y-6 container mx-auto py-6">
            <div className="flex items-center gap-4">
                <Link href="/dashboard/reportes">
                    <Button variant="ghost" size="icon">
                        <ArrowLeft className="h-4 w-4" />
                    </Button>
                </Link>
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Rendimiento de Flota (DET_REND)</h1>
                    <p className="text-muted-foreground">Análisis financiero detallado Costo-Kilómetro y Proyecciones.</p>
                </div>
            </div>

            {/* KPIs */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-muted-foreground">CPK Promedio Flota</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-blue-600">${summary?.cpk_flota_promedio.toFixed(5)} / km</div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-muted-foreground">Costo Inventario + Mant.</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{formatCurrency(summary?.costo_flota_total || 0)}</div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-muted-foreground">Km Rodados Totales</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{(summary?.km_rodados_total || 0).toLocaleString()} km</div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-muted-foreground">Neumáticos Analizados</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{summary?.total_neumaticos}</div>
                    </CardContent>
                </Card>
            </div>

            {/* Tabla Detallada */}
            <Card>
                <CardHeader>
                    <CardTitle>Detalle por Neumático</CardTitle>
                    <CardDescription>
                        Listado completo ordenado por eficiencia (CPK). Los valores en rojo indican costos superiores al promedio.
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <DataTable
                        columns={columns}
                        data={data?.data || []}
                        searchKey="serie"
                    />
                </CardContent>
            </Card>
        </div>
    );
}
