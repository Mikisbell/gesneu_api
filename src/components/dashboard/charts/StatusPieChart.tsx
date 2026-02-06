'use client';

import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';

interface StatusPieChartProps {
    data: {
        estado: string;
        cantidad: number;
    }[];
}

const COLORS_MAP: Record<string, string> = {
    'EN_STOCK': '#16a34a', // Green
    'INSTALADO': '#2563eb', // Blue
    'EN_REPARACION': '#eab308', // Yellow
    'EN_REENCAUCHE': '#f97316', // Orange
    'DESECHADO': '#dc2626', // Red
    'PARA_DESECHO': '#9ca3af', // Gray
};

const DEFAULT_COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

export function StatusPieChart({ data }: StatusPieChartProps) {
    if (!data || data.length === 0) {
        return (
            <Card className="col-span-3">
                <CardHeader>
                    <CardTitle>Estado de Flota</CardTitle>
                </CardHeader>
                <CardContent className="h-[300px] flex items-center justify-center text-muted-foreground">
                    Sin datos
                </CardContent>
            </Card>
        );
    }

    const chartData = data.map(d => ({
        name: d.estado.replace('_', ' '),
        value: d.cantidad,
        color: COLORS_MAP[d.estado] || DEFAULT_COLORS[0]
    }));

    return (
        <Card className="col-span-3">
            <CardHeader>
                <CardTitle>Distribución por Estado</CardTitle>
                <CardDescription>Estado actual de los neumáticos</CardDescription>
            </CardHeader>
            <CardContent>
                <div className="h-[300px] w-full min-h-[300px]">
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={chartData}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={80}
                                paddingAngle={5}
                                dataKey="value"
                            >
                                {chartData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                            </Pie>
                            <Tooltip />
                            <Legend />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            </CardContent>
        </Card>
    );
}
