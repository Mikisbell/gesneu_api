'use client';

import React, { useEffect, useState } from 'react';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';

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

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const res = await fetch(`/api/v1/neumaticos/${neumaticoId}/historial-presion`);
                const json = await res.json();

                if (json.success) {
                    setData(json.data);
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

    if (loading) return <Skeleton className="h-[300px] w-full rounded-xl" />;
    if (error) return <div className="text-red-500 text-sm p-4 text-center">{error}</div>;
    if (data.length === 0) return (
        <Card>
            <CardContent className="h-[300px] flex items-center justify-center text-muted-foreground">
                No hay lecturas de presión registradas.
            </CardContent>
        </Card>
    );

    // Configuración del Chart
    const chartData = {
        labels: data.map(d => new Date(d.fecha).toLocaleDateString('es-PE', { day: '2-digit', month: 'short' })),
        datasets: [
            {
                label: 'Presión (PSI)',
                data: data.map(d => d.presion),
                borderColor: 'rgb(59, 130, 246)', // Blue-500
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                fill: true,
                tension: 0.3, // Curva suave
                pointRadius: 4,
                pointHoverRadius: 6,
            }
        ],
    };

    const options = {
        responsive: true,
        plugins: {
            legend: {
                position: 'top' as const,
            },
            tooltip: {
                callbacks: {
                    afterLabel: function (context: any) {
                        const index = context.dataIndex;
                        const lectura = data[index];
                        return `Insp: ${lectura.inspector}`;
                    }
                }
            }
        },
        scales: {
            y: {
                beginAtZero: false,
                title: { display: true, text: 'PSI' }
            }
        },
        maintainAspectRatio: false
    };

    return (
        <Card className="shadow-sm">
            <CardHeader className="pb-2">
                <CardTitle className="text-lg font-medium">Historial de Presión</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="h-[300px] w-full">
                    <Line options={options} data={chartData} />
                </div>
            </CardContent>
        </Card>
    );
};
