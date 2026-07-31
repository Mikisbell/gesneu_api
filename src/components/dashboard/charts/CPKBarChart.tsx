'use client';

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { ChartContainer } from '@/components/ui/chart-container';

interface CPKBarChartProps {
    data: {
        fabricante_nombre: string;
        cpk_promedio: number;
        cpk_minimo: number;
        cpk_maximo: number;
    }[];
}

export function CPKBarChart({ data }: CPKBarChartProps) {
    if (!data || data.length === 0) {
        return (
            <Card className="col-span-1 md:col-span-2">
                <CardHeader>
                    <CardTitle>Costo por Kilómetro (CPK)</CardTitle>
                </CardHeader>
                <CardContent className="h-[300px] flex items-center justify-center text-muted-foreground">
                    Sin datos de kilometraje suficiente
                </CardContent>
            </Card>
        )
    }

    return (
        <Card className="col-span-1 md:col-span-2">
            <CardHeader>
                <CardTitle>Comparativo CPK por Marca</CardTitle>
                <CardDescription>Costo promedio por kilómetro (Menor es mejor)</CardDescription>
            </CardHeader>
            <CardContent>
                <ChartContainer className="h-[300px] w-full">
                    <ResponsiveContainer width="100%" height="100%" initialDimension={{ width: 400, height: 300 }}>
                        <BarChart
                            data={data}
                            layout="vertical"
                            margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
                        >
                            <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                            <XAxis type="number" tickFormatter={(value) => `$${value}`} />
                            <YAxis dataKey="fabricante_nombre" type="category" width={100} />
                            <Tooltip
                                formatter={(value) => [`$${(value as number)?.toFixed(4) ?? '0'}`, 'CPK Promedio']}
                                labelStyle={{ color: 'black' }}
                            />
                            <Legend />
                            <Bar
                                dataKey="cpk_promedio"
                                name="CPK Promedio ($)"
                                fill="#0f172a"
                                radius={[0, 4, 4, 0]}
                                barSize={40}
                            />
                        </BarChart>
                    </ResponsiveContainer>
                </ChartContainer>
            </CardContent>
        </Card>
    );
}
