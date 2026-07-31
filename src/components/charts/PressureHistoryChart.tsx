'use client';

import React, { useEffect, useState } from 'react';
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    ReferenceLine
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ChartContainer } from '@/components/ui/chart-container';
import { Skeleton } from '@/components/ui/skeleton';
import { Minus, ArrowDownRight, ArrowUpRight, CheckCircle2, AlertTriangle } from 'lucide-react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

interface LecturaHistorial {
    id: string;
    fecha: string;
    presion: number;
    temperatura?: number;
    inspector: string;
}

interface PressureHistoryChartProps {
    neumaticoId: string;
}

export const PressureHistoryChart = ({ neumaticoId }: PressureHistoryChartProps) => {
    const [data, setData] = useState<LecturaHistorial[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [recomendada, setRecomendada] = useState<number | undefined>(undefined);

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const res = await fetch(`/api/v1/neumaticos/${neumaticoId}/historial-presion`);
                const json = await res.json();

                if (json.success) {
                    // Sort by date just in case, though API should handle it
                    const sortedData = json.data.sort((a: any, b: any) => new Date(a.fecha).getTime() - new Date(b.fecha).getTime());
                    setData(sortedData);
                    if (json.meta?.recomendada) {
                        setRecomendada(json.meta.recomendada);
                    }
                } else {
                    setError('Error al cargar historial');
                }
            } catch (err) {
                setError('Error de conexión');
            } finally {
                setLoading(false);
            }
        };

        if (neumaticoId) {
            fetchHistory();
        }
    }, [neumaticoId]);

    if (loading) return <Skeleton className="h-[400px] w-full rounded-xl" />;

    if (error) return (
        <Card className="border-red-100 bg-red-50">
            <CardContent className="flex items-center justify-center h-[200px] text-red-600">
                <AlertTriangle className="mr-2 h-5 w-5" />
                {error}
            </CardContent>
        </Card>
    );

    if (data.length === 0) return (
        <Card className="shadow-sm border-slate-200">
            <CardHeader className="pb-2">
                <CardTitle className="text-lg font-semibold text-slate-800">Historial de Presión</CardTitle>
            </CardHeader>
            <CardContent className="h-[300px] flex items-center justify-center text-muted-foreground flex-col gap-3">
                <div className="bg-slate-100 p-4 rounded-full">
                    <Minus className="h-8 w-8 text-slate-400" />
                </div>
                <div className="text-center">
                    <p className="font-medium text-slate-900">Sin datos registrados</p>
                    <p className="text-sm text-slate-500 mt-1">Realiza una inspección para comenzar a ver el historial.</p>
                </div>
            </CardContent>
        </Card>
    );

    // --- KPI Analysis ---
    const lastReading = data[data.length - 1];
    const analyzeTrend = () => {
        if (data.length < 2) return { text: 'Datos insuficientes', color: 'text-slate-500', bg: 'bg-slate-100', icon: <Minus className="h-4 w-4" /> };

        const recent = data.slice(-5);
        const first = recent[0].presion;
        const last = recent[recent.length - 1].presion;
        const diff = last - first;

        if (diff < -2) return { text: 'Pérdida Detectada', color: 'text-rose-600', bg: 'bg-rose-50', icon: <ArrowDownRight className="h-4 w-4" /> };
        if (diff > 2) return { text: 'Presión Subiendo', color: 'text-emerald-600', bg: 'bg-emerald-50', icon: <ArrowUpRight className="h-4 w-4" /> };
        return { text: 'Presión Estable', color: 'text-blue-600', bg: 'bg-blue-50', icon: <CheckCircle2 className="h-4 w-4" /> };
    };

    const trend = analyzeTrend();

    // Bounds for chart scaling
    const dataMax = Math.max(...data.map(d => d.presion));
    const dataMin = Math.min(...data.map(d => d.presion));
    // Add buffer
    const domainMax = Math.max(dataMax, recomendada ? recomendada * 1.2 : 120);
    const domainMin = Math.max(0, Math.min(dataMin, recomendada ? recomendada * 0.8 : 0));

    // Colors
    const isLow = recomendada && lastReading.presion < (recomendada * 0.9);
    const chartColor = isLow ? '#f43f5e' : '#10b981'; // Rose or Emerald

    return (
        <Card className="shadow-sm border-slate-200 overflow-hidden">
            <CardHeader className="border-b border-slate-100 bg-slate-50/50 pb-4 pt-4">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <CardTitle className="text-base font-semibold text-slate-800 flex items-center gap-2">
                            Monitoreo de Presión
                        </CardTitle>
                        <p className="text-xs text-slate-500 mt-1">
                            {recomendada ? `Recomendada: ${recomendada} PSI` : 'Sin presión configurada'}
                        </p>
                    </div>

                    <div className="flex items-center gap-6 text-sm">
                        <div className="flex flex-col items-end">
                            <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Última Lectura</span>
                            <div className="flex items-baseline gap-1">
                                <span className={`text-xl font-bold ${isLow ? 'text-rose-600' : 'text-emerald-600'}`}>
                                    {lastReading.presion}
                                </span>
                                <span className="text-xs font-medium text-slate-400">PSI</span>
                            </div>
                        </div>

                        <div className={`flex items-center gap-2 px-3 py-1 rounded-full ${trend.bg} ${trend.color} border border-transparent/10`}>
                            {trend.icon}
                            <span className="font-semibold text-xs">{trend.text}</span>
                        </div>
                    </div>
                </div>
            </CardHeader>
            <CardContent className="p-1">
                <ChartContainer className="h-[350px] w-full mt-4">
                    <ResponsiveContainer width="100%" height="100%" minHeight={350}>
                        <AreaChart
                            data={data}
                            margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                        >
                            <defs>
                                <linearGradient id="colorPresion" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor={chartColor} stopOpacity={0.2} />
                                    <stop offset="95%" stopColor={chartColor} stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                            <XAxis
                                dataKey="fecha"
                                tickFormatter={(str) => format(new Date(str), 'd MMM', { locale: es })}
                                stroke="#94a3b8"
                                fontSize={12}
                                tickLine={false}
                                axisLine={false}
                            />
                            <YAxis
                                domain={[domainMin, domainMax]}
                                stroke="#94a3b8"
                                fontSize={12}
                                tickLine={false}
                                axisLine={false}
                                tickFormatter={(val) => `${Math.round(val)}`}
                            />
                            <Tooltip
                                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                labelFormatter={(label) => format(new Date(label), 'PPP p', { locale: es })}
                            />
                            {recomendada && (
                                <ReferenceLine
                                    y={recomendada}
                                    stroke="#64748b"
                                    strokeDasharray="3 3"
                                    label={{ value: 'Recomendada', position: 'insideRight', fill: '#64748b', fontSize: 10 }}
                                />
                            )}
                            <Area
                                type="monotone"
                                dataKey="presion"
                                stroke={chartColor}
                                strokeWidth={2}
                                fillOpacity={1}
                                fill="url(#colorPresion)"
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </ChartContainer>
            </CardContent>
        </Card>
    );
};
