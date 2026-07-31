'use client';

import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ChartContainer } from '@/components/ui/chart-container';

interface InventoryPieChartProps {
    data: {
        marca: string;
        cantidad: number;
    }[];
}

const COLORS = ['#2563eb', '#16a34a', '#eab308', '#dc2626', '#9333ea', '#0891b2'];

export function InventoryPieChart({ data }: InventoryPieChartProps) {
    if (!data || data.length === 0) {
        return (
            <Card className="col-span-1">
                <CardHeader>
                    <CardTitle>Inventario por Marca</CardTitle>
                </CardHeader>
                <CardContent className="h-[300px] flex items-center justify-center text-muted-foreground">
                    Sin datos disponibles
                </CardContent>
            </Card>
        );
    }

    return (
        <Card className="col-span-1">
            <CardHeader>
                <CardTitle>Inventario por Marca</CardTitle>
            </CardHeader>
            <CardContent>
                <ChartContainer className="h-[300px] w-full">
                    <ResponsiveContainer width="100%" height="100%" initialDimension={{ width: 400, height: 300 }}>
                        <PieChart>
                            <Pie
                                data={data}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={80}
                                fill="#8884d8"
                                paddingAngle={5}
                                dataKey="cantidad"
                                nameKey="marca"
                            >
                                {data.map((entry, index) => (
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
    );
}
