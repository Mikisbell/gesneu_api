import { prisma } from '@/lib/prisma';
import Link from 'next/link';

export const dynamic = 'force-dynamic';

async function getStatistics() {
    const [
        totalNeumaticos,
        neumaticosInstalados,
        neumaticosEnStock,
        totalVehiculos,
        eventosHoy,
        neumaticosEnReparacion
    ] = await Promise.all([
        prisma.neumatico.count({ where: { activo: true } }),
        prisma.neumatico.count({ where: { estado_actual: 'INSTALADO', activo: true } }),
        prisma.neumatico.count({ where: { estado_actual: 'EN_STOCK', activo: true } }),
        prisma.vehiculo.count({ where: { activo: true } }),
        prisma.eventoNeumatico.count({
            where: {
                fecha_evento: { gte: new Date(new Date().setHours(0, 0, 0, 0)) }
            }
        }),
        prisma.neumatico.count({ where: { estado_actual: 'EN_REPARACION', activo: true } })
    ]);

    return {
        totalNeumaticos,
        neumaticosInstalados,
        neumaticosEnStock,
        totalVehiculos,
        eventosHoy,
        neumaticosEnReparacion
    };
}

export default async function DashboardPage() {
    const stats = await getStatistics();

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header simple y limpio */}
            <div className="bg-white border-b border-gray-200">
                <div className="max-w-7xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-xl font-semibold text-gray-900">GesNeu</h1>
                            <p className="text-sm text-gray-500">Sistema de Gestión de Neumáticos</p>
                        </div>
                        <div className="text-right">
                            <p className="text-sm text-gray-500">{new Date().toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}</p>
                        </div>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-6 py-6">
                {/* Métricas compactas */}
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-6">
                    <MetricCard title="Total Neumáticos" value={stats.totalNeumaticos} />
                    <MetricCard title="Instalados" value={stats.neumaticosInstalados} />
                    <MetricCard title="En Stock" value={stats.neumaticosEnStock} />
                    <MetricCard title="Vehículos" value={stats.totalVehiculos} />
                    <MetricCard title="Eventos Hoy" value={stats.eventosHoy} />
                    <MetricCard title="En Reparación" value={stats.neumaticosEnReparacion} />
                </div>

                {/* Acciones */}
                <div className="bg-white rounded border border-gray-200 p-5 mb-6">
                    <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">Acciones</h2>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                        <ActionButton href="/api/v1/neumaticos" label="Neumáticos" />
                        <ActionButton href="/api/v1/vehiculos" label="Vehículos" />
                        <ActionButton href="/api/v1/operaciones/montaje" label="Montaje" />
                        <ActionButton href="/api/v1/operaciones/rotacion" label="Rotación" />
                    </div>
                </div>

                {/* API Endpoints */}
                <div className="bg-white rounded border border-gray-200 p-5">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">API Endpoints</h2>
                        <span className="text-xs text-gray-500">7 disponibles</span>
                    </div>
                    <div className="space-y-1.5">
                        <ApiEndpoint method="GET" path="/api/v1/neumaticos" />
                        <ApiEndpoint method="POST" path="/api/v1/neumaticos" />
                        <ApiEndpoint method="GET" path="/api/v1/vehiculos" />
                        <ApiEndpoint method="POST" path="/api/v1/vehiculos" />
                        <ApiEndpoint method="POST" path="/api/v1/operaciones/montaje" />
                        <ApiEndpoint method="POST" path="/api/v1/operaciones/desmontaje" />
                        <ApiEndpoint method="POST" path="/api/v1/operaciones/rotacion" />
                    </div>
                </div>
            </div>
        </div>
    );
}

function MetricCard({ title, value }: { title: string; value: number }) {
    return (
        <div className="bg-white rounded border border-gray-200 p-4 hover:border-gray-300 transition-colors">
            <p className="text-xs text-gray-500 mb-1">{title}</p>
            <p className="text-2xl font-semibold text-gray-900">{value}</p>
        </div>
    );
}

function ActionButton({ href, label }: { href: string; label: string }) {
    return (
        <Link
            href={href}
            target="_blank"
            className="block px-4 py-2.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded hover:bg-gray-50 hover:border-gray-400 transition-colors text-center"
        >
            {label}
        </Link>
    );
}

function ApiEndpoint({ method, path }: { method: string; path: string }) {
    const methodColors: Record<string, string> = {
        GET: 'bg-blue-50 text-blue-700 border-blue-200',
        POST: 'bg-green-50 text-green-700 border-green-200',
        PUT: 'bg-amber-50 text-amber-700 border-amber-200',
        DELETE: 'bg-red-50 text-red-700 border-red-200'
    };

    return (
        <div className="flex items-center gap-3 py-2 px-3 rounded hover:bg-gray-50">
            <span className={`px-2.5 py-0.5 text-xs font-medium rounded border ${methodColors[method]}`}>
                {method}
            </span>
            <code className="text-sm text-gray-600 font-mono">{path}</code>
        </div>
    );
}
