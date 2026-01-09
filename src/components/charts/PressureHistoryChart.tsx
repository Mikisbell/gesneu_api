'use client';

import React, { useEffect, useState, useRef } from 'react';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler,
    ScriptableContext,
    ChartData
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { ArrowDownRight, ArrowUpRight, Minus, AlertTriangle, CheckCircle2 } from 'lucide-react';

// Registrar componentes de Chart.js
ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
);

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
    const chartRef = useRef<any>(null);

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const res = await fetch(`/api/v1/neumaticos/${neumaticoId}/historial-presion`);
                const json = await res.json();

                if (json.success) {
                    setData(json.data);
                    // Leemos la presión recomendada de los metadatos de la respuesta
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
    if (error) return <div className="text-red-500 text-sm p-4 text-center border border-red-100 rounded-lg bg-red-50">{error}</div>;

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

    // --- LÓGICA DE UI PREMIUM ---

    // 1. Análisis de Tendencia Simple
    const analizarTendencia = () => {
        if (data.length < 2) return { text: 'Datos insuficientes', color: 'text-slate-500', bg: 'bg-slate-100', icon: <Minus className="h-4 w-4" /> };

        const recent = data.slice(-5);
        const first = recent[0].presion;
        const last = recent[recent.length - 1].presion;
        const diff = last - first;

        if (diff < -2) return { text: 'Pérdida Detectada', color: 'text-rose-600', bg: 'bg-rose-50', icon: <ArrowDownRight className="h-4 w-4" /> };
        if (diff > 2) return { text: 'Presión Subiendo', color: 'text-emerald-600', bg: 'bg-emerald-50', icon: <ArrowUpRight className="h-4 w-4" /> };
        return { text: 'Presión Estable', color: 'text-blue-600', bg: 'bg-blue-50', icon: <CheckCircle2 className="h-4 w-4" /> };
    };

    const trend = analizarTendencia();
    const lastReading = data[data.length - 1];
    const maxVal = Math.max(...data.map(d => d.presion));
    const minVal = Math.min(...data.map(d => d.presion));

    // 2. Configuración Chart.js con Gradiente e Industrial Look
    const safeMin = recomendada ? recomendada * 0.9 : 0; // -10% margin
    const safeMax = recomendada ? recomendada * 1.1 : 120; // +10% margin

    const chartData: ChartData<'line'> = {
        labels: data.map(d => new Date(d.fecha).toLocaleDateString('es-PE', { day: '2-digit', month: 'short' })),
        datasets: [
            // BANDA SEGURA (SAFE ZONE) - Fondo verde sutil
            ...(recomendada ? [{
                label: 'Zona Segura Max',
                data: data.map(() => safeMax),
                borderColor: 'transparent',
                backgroundColor: 'rgba(34, 197, 94, 0.1)', // green-500 very light
                fill: '+1', // Llenar hasta el siguiente dataset (Zona Segura Min)
                pointRadius: 0,
                tension: 0
            }, {
                label: 'Zona Segura Min',
                data: data.map(() => safeMin),
                borderColor: 'transparent',
                backgroundColor: 'transparent', // El color viene del fill del de arriba
                fill: false,
                pointRadius: 0,
                tension: 0
            }] : []) as any,

            // LÍNEA PRINCIPAL (DATOS)
            {
                label: 'Presión Medida',
                data: data.map(d => d.presion),
                borderColor: '#3b82f6', // blue-500 default
                borderWidth: 3,
                segment: {
                    borderColor: (ctx: any) => {
                        if (!recomendada) return '#3b82f6';
                        const val = ctx.p0.parsed.y;
                        if (val < safeMin || val > safeMax) return '#ef4444'; // Red if out of zone
                        return '#22c55e'; // Green if inside zone
                    }
                } as any, // Cast any to avoid weird type issues with segments in react-chartjs-2 wrapper
                backgroundColor: (context: ScriptableContext<'line'>) => {
                    const ctx = context.chart.ctx;
                    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
                    gradient.addColorStop(0, "rgba(59, 130, 246, 0.1)");
                    gradient.addColorStop(1, "rgba(59, 130, 246, 0.0)");
                    return gradient;
                },
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointBackgroundColor: '#ffffff',
                pointBorderColor: (ctx: any) => {
                    if (!recomendada) return '#3b82f6';
                    const val = ctx.raw as number;
                    if (val < safeMin || val > safeMax) return '#ef4444';
                    return '#22c55e';
                },
                pointBorderWidth: 2,
                pointHoverRadius: 6,
                pointHoverBackgroundColor: '#ffffff',
                pointHoverBorderColor: '#3b82f6',
            },

            // LÍNEA IDEAL (Punteada)
            ...(recomendada ? [{
                label: 'Presión Ideal',
                data: data.map(() => recomendada),
                borderColor: '#64748b', // slate-500
                borderWidth: 1,
                borderDash: [6, 6],
                pointRadius: 0,
                fill: false,
                tension: 0
            }] : []) as any
        ]
    };

    const options: any = {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            mode: 'index',
            intersect: false,
        },
        plugins: {
            legend: { display: false },
            tooltip: {
                enabled: true,
                backgroundColor: 'rgba(15, 23, 42, 0.95)',
                titleColor: '#f8fafc',
                bodyColor: '#e2e8f0',
                padding: 12,
                cornerRadius: 8,
                titleFont: { size: 13, weight: 600 },
                bodyFont: { size: 12 },
                displayColors: false, // Cleaner tooltip
                callbacks: {
                    label: function (context: any) {
                        if (['Zona Segura Max', 'Zona Segura Min'].includes(context.dataset.label)) return null;

                        let label = `${context.parsed.y} PSI`;
                        const val = context.parsed.y;

                        if (recomendada) {
                            if (val < safeMin) label += ' (⚠️ BAJA)';
                            else if (val > safeMax) label += ' (⚠️ ALTA)';
                            else label += ' (✅ OK)';
                        }
                        return label;
                    },
                    afterLabel: function (context: any) {
                        if (context.dataset.label !== 'Presión Medida') return '';
                        const index = context.dataIndex;
                        const lectura = data[index];
                        return `\n📅 ${new Date(lectura.fecha).toLocaleString('es-PE', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })}\n👤 ${lectura.inspector}`;
                    }
                }
            }
        },
        scales: {
            x: {
                grid: { display: false },
                ticks: {
                    font: { size: 10 },
                    color: '#94a3b8',
                    maxTicksLimit: 6
                }
            },
            y: {
                position: 'right',
                grid: {
                    color: '#f1f5f9',
                    borderDash: [2, 2]
                },
                border: { display: false },
                ticks: {
                    font: { size: 10 },
                    color: '#94a3b8',
                    callback: (value: number) => `${value}`
                },
                min: recomendada ? recomendada * 0.5 : 0,
                max: recomendada ? recomendada * 1.3 : 150
            }
        }
    };

    return (
        <Card className="shadow-sm border-slate-200 overflow-hidden">
            <CardHeader className="border-b border-slate-100 bg-slate-50/50 pb-4 pt-4">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <CardTitle className="text-base font-semibold text-slate-800 flex items-center gap-2">
                            Monitoreo de Presión
                        </CardTitle>
                        <p className="text-xs text-slate-500 mt-1">
                            {recomendada ? `Zona Segura: ${safeMin.toFixed(0)} - ${safeMax.toFixed(0)} PSI` : 'Sin presión recomendada configurada'}
                        </p>
                    </div>

                    {/* Stats Row */}
                    <div className="flex items-center gap-6 text-sm">
                        <div className="flex flex-col items-end">
                            <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Última Lectura</span>
                            <div className="flex items-baseline gap-1">
                                <span className={`text-xl font-bold ${lastReading.presion < (safeMin || 0) ? 'text-rose-600' : 'text-emerald-600'}`}>
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
            <CardContent className="p-0">
                <div className="h-[350px] w-full p-4 relative bg-gradient-to-b from-transparent to-slate-50/30">
                    <Line ref={chartRef} options={options} data={chartData} />
                </div>
            </CardContent>
        </Card>
    );
};
