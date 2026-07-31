'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Loader2, ArrowLeft, RefreshCcw, Trash2, Activity, TrendingUp } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import { ChartContainer } from '@/components/ui/chart-container';

// Definición de tipos actualizada para Fase 6A
interface ManagementKPIs {
    kpis: {
        indice_reencauche_porcentaje: number;
        indice_vidas_promedio: number;
        total_activos: number;
        total_desechados: number;
        tasa_scrap_global: number;
    };
    distribucion_vidas: { '0': number; '1': number; '2': number; '3+': number };
    kpis_por_tipo_vehiculo: { tipo: string; total: number; reencauchados: number; participacion: number; indice_vidas: number }[];
    charts: {
        scrap_pareto: { name: string; value: number }[];
        scrap_pareto_categoria: { name: string; value: number }[];
    };
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];
const CATEGORY_COLORS: Record<string, string> = {
    'FATIGA': '#10B981',    // Verde
    'MECANICA': '#F59E0B',  // Amarillo
    'OPERACION': '#EF4444', // Rojo
    'SIN_CLASIFICAR': '#6B7280' // Gris
};

export default function GestionPage() {
    const { data, isLoading, error } = useQuery<ManagementKPIs>({
        queryKey: ['reportes-gestion'],
        queryFn: () => apiClient<ManagementKPIs>('/reportes/gestion'),
        refetchInterval: 30000 // Refrescar cada 30s
    });

    if (error) return <div className="p-8 text-center text-red-500">Error cargando KPIs de Gestión</div>;
    if (isLoading) return <div className="p-8 flex justify-center"><Loader2 className="animate-spin h-8 w-8" /></div>;

    const { kpis, charts, distribucion_vidas, kpis_por_tipo_vehiculo } = data!;

    // Preparar datos de distribución de vidas para gráfico
    const vidasData = [
        { name: 'Original (0)', value: distribucion_vidas['0'], fill: '#10B981' },
        { name: '1er Reencauche', value: distribucion_vidas['1'], fill: '#3B82F6' },
        { name: '2do Reencauche', value: distribucion_vidas['2'], fill: '#F59E0B' },
        { name: '3+ Reencauches', value: distribucion_vidas['3+'], fill: '#8B5CF6' },
    ];

    return (
        <div className="space-y-8 container mx-auto py-6">
            <div className="flex items-center gap-4">
                <Link href="/dashboard/reportes">
                    <Button variant="ghost" size="icon">
                        <ArrowLeft className="h-4 w-4" />
                    </Button>
                </Link>
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Gestión Estratégica de Flota</h1>
                    <p className="text-muted-foreground">KPIs de Ciclo de Vida y Análisis de Desechos.</p>
                </div>
            </div>

            {/* KPI Cards */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Índice Reencauchabilidad</CardTitle>
                        <RefreshCcw className="h-4 w-4 text-green-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{kpis.indice_reencauche_porcentaje}%</div>
                        <p className="text-xs text-muted-foreground">
                            Flota rodando con casco reutilizado
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Índice de Vidas</CardTitle>
                        <Activity className="h-4 w-4 text-blue-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{kpis.indice_vidas_promedio}x</div>
                        <p className="text-xs text-muted-foreground">
                            Promedio vidas por carcasa (Obj: {'>'} 2.5)
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Desechos</CardTitle>
                        <Trash2 className="h-4 w-4 text-gray-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{kpis.total_desechados}</div>
                        <p className="text-xs text-muted-foreground">
                            Neumáticos dados de baja histórica
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Tasa de Scrap</CardTitle>
                        <TrendingUp className="h-4 w-4 text-red-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{kpis.tasa_scrap_global}%</div>
                        <p className="text-xs text-muted-foreground">
                            % Inversión perdida en desecho
                        </p>
                    </CardContent>
                </Card>
            </div>

            {/* Charts Row 1: Pareto por Categoría + Distribución Vidas */}
            <div className="grid gap-4 md:grid-cols-2">
                {/* Pareto por Categoría de Falla - NUEVO */}
                <Card>
                    <CardHeader>
                        <CardTitle>Análisis por Tipo de Falla</CardTitle>
                        <CardDescription>Categorización: Fatiga | Mecánica | Operación</CardDescription>
                    </CardHeader>
                    <CardContent className="h-[300px]">
                        <ChartContainer className="h-full">
                        <ResponsiveContainer width="100%" height="100%" minHeight={300}>
                            <BarChart data={charts.scrap_pareto_categoria} layout="vertical">
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis type="number" />
                                <YAxis dataKey="name" type="category" width={100} />
                                <Tooltip />
                                <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                                    {charts.scrap_pareto_categoria.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={CATEGORY_COLORS[entry.name] || COLORS[index]} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                        </ChartContainer>
                    </CardContent>
                </Card>

                {/* Distribución de Vidas - NUEVO */}
                <Card>
                    <CardHeader>
                        <CardTitle>Distribución por N° de Vidas</CardTitle>
                        <CardDescription>Original vs Reencauchados (0, 1, 2, 3+)</CardDescription>
                    </CardHeader>
                    <CardContent className="h-[300px]">
                        <ChartContainer className="h-full">
                        <ResponsiveContainer width="100%" height="100%" minHeight={300}>
                            <BarChart data={vidasData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="name" />
                                <YAxis />
                                <Tooltip />
                                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                                    {vidasData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.fill} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                        </ChartContainer>
                    </CardContent>
                </Card>
            </div>

            {/* Charts Row 2: Pareto Detallado + KPIs por Tipo Vehículo */}
            <div className="grid gap-4 md:grid-cols-2">
                {/* Scrap Pareto por Motivo */}
                <Card>
                    <CardHeader>
                        <CardTitle>Pareto de Causas de Desecho</CardTitle>
                        <CardDescription>Distribución de motivos de baja (Top Impacto)</CardDescription>
                    </CardHeader>
                    <CardContent className="h-[300px]">
                        <ChartContainer className="h-full">
                        <ResponsiveContainer width="100%" height="100%" minHeight={300}>
                            <PieChart>
                                <Pie
                                    data={charts.scrap_pareto}
                                    cx="50%"
                                    cy="50%"
                                    labelLine={false}
                                    outerRadius={80}
                                    fill="#8884d8"
                                    dataKey="value"
                                    label={({ name, percent }) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}
                                >
                                    {charts.scrap_pareto.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip />
                                <Legend />
                            </PieChart>
                        </ResponsiveContainer>
                        </ChartContainer>
                    </CardContent>
                </Card>

                {/* KPIs por Tipo de Vehículo - NUEVO */}
                <Card>
                    <CardHeader>
                        <CardTitle>KPIs por Tipo de Vehículo</CardTitle>
                        <CardDescription>Reencauchabilidad segmentada (Tracto, Semirremolque, etc.)</CardDescription>
                    </CardHeader>
                    <CardContent className="h-[300px] overflow-auto">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="border-b">
                                    <th className="text-left p-2">Tipo</th>
                                    <th className="text-right p-2">Total</th>
                                    <th className="text-right p-2">Reenc.</th>
                                    <th className="text-right p-2">%</th>
                                    <th className="text-right p-2">Idx Vidas</th>
                                </tr>
                            </thead>
                            <tbody>
                                {kpis_por_tipo_vehiculo.map((row, i) => (
                                    <tr key={i} className="border-b hover:bg-muted/50">
                                        <td className="p-2 font-medium">{row.tipo}</td>
                                        <td className="text-right p-2">{row.total}</td>
                                        <td className="text-right p-2">{row.reencauchados}</td>
                                        <td className="text-right p-2">{row.participacion}%</td>
                                        <td className="text-right p-2 font-semibold">{row.indice_vidas}x</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
