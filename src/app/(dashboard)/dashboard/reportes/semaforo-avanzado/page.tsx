'use client';

import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { apiClient } from '@/lib/api/client';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Loader2, ArrowLeft, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell, Legend } from 'recharts';
import { ChartContainer } from '@/components/ui/chart-container';

interface SemaforoData {
    filtro_aplicado: string | null;
    medidas_disponibles: string[];
    resumen: {
        total: number;
        verde: number;
        amarillo: number;
        rojo: number;
        porcentaje_critico: number;
    };
    distribucion_por_eje: Array<{
        eje: string;
        verde: number;
        amarillo: number;
        rojo: number;
        total: number;
        porcentaje_rojo: number;
    }>;
    detalle: Array<{
        serie: string;
        medida: string;
        marca: string;
        placa: string;
        posicion: string;
        eje: string;
        remanente_mm: number;
        estado_semaforo: 'VERDE' | 'AMARILLO' | 'ROJO';
    }>;
}

const SEMAFORO_COLORS = {
    VERDE: '#10B981',
    AMARILLO: '#F59E0B',
    ROJO: '#EF4444'
};

export default function SemaforoAvanzadoPage() {
    const [medidaFilter, setMedidaFilter] = useState<string>('');

    const { data, isLoading, error } = useQuery<SemaforoData>({
        queryKey: ['semaforo-medida', medidaFilter],
        queryFn: () => apiClient<SemaforoData>(`/reportes/semaforo-medida${medidaFilter ? `?medida=${medidaFilter}` : ''}`),
        refetchInterval: 60000
    });

    if (error) return <div className="p-8 text-center text-red-500">Error cargando datos de semáforo</div>;
    if (isLoading) return <div className="p-8 flex justify-center"><Loader2 className="animate-spin h-8 w-8" /></div>;

    const { resumen, distribucion_por_eje, detalle, medidas_disponibles } = data!;

    // Preparar datos para gráfico stacked
    const chartData = distribucion_por_eje.map(d => ({
        name: d.eje,
        Verde: d.verde,
        Amarillo: d.amarillo,
        Rojo: d.rojo
    }));

    return (
        <div className="space-y-6 container mx-auto py-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <Link href="/dashboard/reportes">
                        <Button variant="ghost" size="icon">
                            <ArrowLeft className="h-4 w-4" />
                        </Button>
                    </Link>
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight">Semáforo por Medida</h1>
                        <p className="text-muted-foreground">Distribución de remanente por eje y dimensión</p>
                    </div>
                </div>

                {/* Filtro por Medida */}
                <Select value={medidaFilter} onValueChange={setMedidaFilter}>
                    <SelectTrigger className="w-[200px]">
                        <SelectValue placeholder="Todas las medidas" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="">Todas las medidas</SelectItem>
                        {medidas_disponibles.map(m => (
                            <SelectItem key={m} value={m}>{m}</SelectItem>
                        ))}
                    </SelectContent>
                </Select>
            </div>

            {/* Resumen Global */}
            <div className="grid gap-4 md:grid-cols-4">
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium">Total Neumáticos</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{resumen.total}</div>
                    </CardContent>
                </Card>

                <Card className="border-green-200 bg-green-50/50 dark:bg-green-950/20">
                    <CardHeader className="pb-2 flex flex-row items-center justify-between">
                        <CardTitle className="text-sm font-medium">Estado Óptimo</CardTitle>
                        <CheckCircle className="h-4 w-4 text-green-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-green-600">{resumen.verde}</div>
                        <p className="text-xs text-muted-foreground">&gt;5mm remanente</p>
                    </CardContent>
                </Card>

                <Card className="border-yellow-200 bg-yellow-50/50 dark:bg-yellow-950/20">
                    <CardHeader className="pb-2 flex flex-row items-center justify-between">
                        <CardTitle className="text-sm font-medium">Precaución</CardTitle>
                        <AlertTriangle className="h-4 w-4 text-yellow-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-yellow-600">{resumen.amarillo}</div>
                        <p className="text-xs text-muted-foreground">3-5mm remanente</p>
                    </CardContent>
                </Card>

                <Card className="border-red-200 bg-red-50/50 dark:bg-red-950/20">
                    <CardHeader className="pb-2 flex flex-row items-center justify-between">
                        <CardTitle className="text-sm font-medium">Crítico</CardTitle>
                        <XCircle className="h-4 w-4 text-red-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-red-600">{resumen.rojo}</div>
                        <p className="text-xs text-muted-foreground">&lt;3mm remanente ({resumen.porcentaje_critico}%)</p>
                    </CardContent>
                </Card>
            </div>

            {/* Gráfico de Distribución por Eje */}
            <Card>
                <CardHeader>
                    <CardTitle>Distribución por Tipo de Eje</CardTitle>
                    <CardDescription>Direccional vs Tracción vs Repuesto</CardDescription>
                </CardHeader>
                <CardContent className="h-[300px]">
                    <ChartContainer className="h-full">
                    <ResponsiveContainer width="100%" height="100%" minHeight={300}>
                        <BarChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Bar dataKey="Verde" stackId="a" fill={SEMAFORO_COLORS.VERDE} />
                            <Bar dataKey="Amarillo" stackId="a" fill={SEMAFORO_COLORS.AMARILLO} />
                            <Bar dataKey="Rojo" stackId="a" fill={SEMAFORO_COLORS.ROJO} />
                        </BarChart>
                    </ResponsiveContainer>
                    </ChartContainer>
                </CardContent>
            </Card>

            {/* Tabla de Detalle - Neumáticos Críticos Primero */}
            <Card>
                <CardHeader>
                    <CardTitle>Detalle de Neumáticos</CardTitle>
                    <CardDescription>Ordenado por criticidad (menor remanente primero)</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="overflow-auto max-h-[400px]">
                        <table className="w-full text-sm">
                            <thead className="sticky top-0 bg-background">
                                <tr className="border-b">
                                    <th className="text-left p-2">Serie</th>
                                    <th className="text-left p-2">Medida</th>
                                    <th className="text-left p-2">Marca</th>
                                    <th className="text-left p-2">Placa</th>
                                    <th className="text-left p-2">Posición</th>
                                    <th className="text-left p-2">Eje</th>
                                    <th className="text-right p-2">Remanente</th>
                                    <th className="text-center p-2">Estado</th>
                                </tr>
                            </thead>
                            <tbody>
                                {detalle.map((n, i) => (
                                    <tr key={i} className="border-b hover:bg-muted/50">
                                        <td className="p-2 font-mono">{n.serie}</td>
                                        <td className="p-2">{n.medida}</td>
                                        <td className="p-2">{n.marca}</td>
                                        <td className="p-2 font-medium">{n.placa}</td>
                                        <td className="p-2">{n.posicion}</td>
                                        <td className="p-2">{n.eje}</td>
                                        <td className="text-right p-2 font-semibold">{n.remanente_mm.toFixed(1)}mm</td>
                                        <td className="text-center p-2">
                                            <Badge
                                                variant="outline"
                                                style={{
                                                    backgroundColor: `${SEMAFORO_COLORS[n.estado_semaforo]}20`,
                                                    borderColor: SEMAFORO_COLORS[n.estado_semaforo],
                                                    color: SEMAFORO_COLORS[n.estado_semaforo]
                                                }}
                                            >
                                                {n.estado_semaforo}
                                            </Badge>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
