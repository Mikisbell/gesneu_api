'use client';

import { useEffect, useState } from 'react';
import { BarChart, DoughnutChart, KpiCard, chartColors } from '@/components/charts/Charts';

interface DashboardData {
    inventario: {
        total_neumaticos: number;
        por_estado: { estado: string; cantidad: number }[];
        por_almacen: { almacen: string; cantidad: number }[];
    } | null;
    rendimiento: {
        top_mejores: { numero_serie: string; cpk: number; modelo: string }[];
        top_peores: { numero_serie: string; cpk: number; modelo: string }[];
        promedio_cpk: number;
    } | null;
    alertas: {
        total: number;
        critical: number;
        warning: number;
    };
    loading: boolean;
    error: string | null;
}

export default function DashboardPage() {
    const [data, setData] = useState<DashboardData>({
        inventario: null,
        rendimiento: null,
        alertas: { total: 0, critical: 0, warning: 0 },
        loading: true,
        error: null,
    });

    useEffect(() => {
        fetchDashboardData();
    }, []);

    async function fetchDashboardData() {
        try {
            // Fetch all dashboard data in parallel
            const [invRes, rendRes, alertRes] = await Promise.all([
                fetch('/api/v1/dashboard/inventario'),
                fetch('/api/v1/dashboard/rendimiento?limit=5'),
                fetch('/api/v1/alertas?resuelta=false'),
            ]);

            const invData = invRes.ok ? (await invRes.json()).data : null;
            const rendData = rendRes.ok ? (await rendRes.json()).data : null;
            const alertData = alertRes.ok ? (await alertRes.json()).data : [];

            // Count alerts by severity
            const critical = Array.isArray(alertData) ? alertData.filter((a: any) => a.severidad === 'CRITICAL').length : 0;
            const warning = Array.isArray(alertData) ? alertData.filter((a: any) => a.severidad === 'WARNING').length : 0;

            setData({
                inventario: invData,
                rendimiento: rendData,
                alertas: { total: critical + warning, critical, warning },
                loading: false,
                error: null,
            });
        } catch (err) {
            setData(prev => ({ ...prev, loading: false, error: 'Error cargando datos' }));
        }
    }

    if (data.loading) {
        return (
            <div className="min-h-screen bg-gray-100 flex items-center justify-center">
                <div className="text-xl text-gray-600">Cargando dashboard...</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-100 p-6">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">Dashboard GesNeu</h1>
                    <p className="text-gray-600">Sistema de Gestión de Neumáticos</p>
                </div>

                {/* KPI Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                    <KpiCard
                        title="Total Neumáticos"
                        value={data.inventario?.total_neumaticos || 0}
                        subtitle="En el sistema"
                        color="blue"
                    />
                    <KpiCard
                        title="CPK Promedio"
                        value={`$${data.rendimiento?.promedio_cpk?.toFixed(4) || '0.0000'}`}
                        subtitle="Costo por kilómetro"
                        color="green"
                    />
                    <KpiCard
                        title="Alertas Críticas"
                        value={data.alertas.critical}
                        subtitle="Requieren atención"
                        color="red"
                    />
                    <KpiCard
                        title="Alertas Warning"
                        value={data.alertas.warning}
                        subtitle="Monitorear"
                        color="yellow"
                    />
                </div>

                {/* Charts Row 1 */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                    {/* Inventario por Estado */}
                    <div className="bg-white p-6 rounded-xl shadow-sm">
                        {data.inventario?.por_estado && (
                            <DoughnutChart
                                labels={data.inventario.por_estado.map(e => e.estado)}
                                data={data.inventario.por_estado.map(e => e.cantidad)}
                                title="Inventario por Estado"
                            />
                        )}
                    </div>

                    {/* Inventario por Almacén */}
                    <div className="bg-white p-6 rounded-xl shadow-sm">
                        {data.inventario?.por_almacen && data.inventario.por_almacen.length > 0 ? (
                            <BarChart
                                labels={data.inventario.por_almacen.map(a => a.almacen)}
                                data={data.inventario.por_almacen.map(a => a.cantidad)}
                                title="Stock por Almacén"
                                color={chartColors.secondary}
                            />
                        ) : (
                            <div className="h-64 flex items-center justify-center text-gray-400">
                                Sin datos de almacenes
                            </div>
                        )}
                    </div>
                </div>

                {/* Top/Bottom CPK */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                    {/* Top Mejores */}
                    <div className="bg-white p-6 rounded-xl shadow-sm">
                        <h3 className="text-lg font-semibold mb-4 text-green-700">🏆 Top 5 Mejor CPK</h3>
                        <div className="space-y-3">
                            {data.rendimiento?.top_mejores?.slice(0, 5).map((n, i) => (
                                <div key={n.numero_serie} className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                                    <div>
                                        <span className="font-mono text-sm">{n.numero_serie}</span>
                                        <span className="text-xs text-gray-500 ml-2">{n.modelo}</span>
                                    </div>
                                    <span className="font-bold text-green-700">${n.cpk.toFixed(4)}</span>
                                </div>
                            ))}
                            {(!data.rendimiento?.top_mejores || data.rendimiento.top_mejores.length === 0) && (
                                <p className="text-gray-400">Sin datos de rendimiento</p>
                            )}
                        </div>
                    </div>

                    {/* Top Peores */}
                    <div className="bg-white p-6 rounded-xl shadow-sm">
                        <h3 className="text-lg font-semibold mb-4 text-red-700">⚠️ Top 5 Peor CPK</h3>
                        <div className="space-y-3">
                            {data.rendimiento?.top_peores?.slice(0, 5).map((n, i) => (
                                <div key={n.numero_serie} className="flex justify-between items-center p-3 bg-red-50 rounded-lg">
                                    <div>
                                        <span className="font-mono text-sm">{n.numero_serie}</span>
                                        <span className="text-xs text-gray-500 ml-2">{n.modelo}</span>
                                    </div>
                                    <span className="font-bold text-red-700">${n.cpk.toFixed(4)}</span>
                                </div>
                            ))}
                            {(!data.rendimiento?.top_peores || data.rendimiento.top_peores.length === 0) && (
                                <p className="text-gray-400">Sin datos de rendimiento</p>
                            )}
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="text-center text-gray-400 text-sm">
                    GesNeu API v1.0 | Dashboard actualizado en tiempo real
                </div>
            </div>
        </div>
    );
}
