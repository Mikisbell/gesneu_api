
"use client";

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import {
    Users, Building2, AlertTriangle, Activity, Shield,
    CheckCircle2, XCircle, TrendingUp, Gauge, Truck,
    CircleDot, Webhook, RefreshCw, Plus, FileBarChart,
    Clock, Zap
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';

// Types for API Response
interface DashboardStats {
    tenants: { value: number; trend: number; label: string };
    users: { value: number; todayNew: number; weekNew: number; label: string };
    neumaticos: { value: number; label: string };
    vehiculos: { value: number; label: string };
    operations: { value: number; label: string };
}

interface AlertsSummary {
    critical: number;
    warning: number;
    unresolved: number;
}

interface HealthStatus {
    status: 'OPTIMAL' | 'WARNING' | 'CRITICAL';
    webhookSuccessRate: number;
    webhooksTotal24h: number;
    webhooksFailed24h: number;
    activeSessions: number;
}

interface ActivityLog {
    id: string;
    operacion: string;
    nombre_tabla: string;
    timestamp_log: string;
    entidad_id?: string;
    usuario_app?: string;
    usuario?: { username: string; email?: string };
    empresa?: { nombre: string };
}

interface DashboardData {
    stats: DashboardStats;
    alerts: AlertsSummary;
    systemHealth: HealthStatus;
    recentActivity: ActivityLog[];
}

// Operation icons and colors
const operationConfig: Record<string, { icon: typeof Activity; color: string; bg: string }> = {
    INSERT: { icon: Plus, color: 'text-green-600', bg: 'bg-green-100 dark:bg-green-900/30' },
    UPDATE: { icon: RefreshCw, color: 'text-blue-600', bg: 'bg-blue-100 dark:bg-blue-900/30' },
    DELETE: { icon: XCircle, color: 'text-red-600', bg: 'bg-red-100 dark:bg-red-900/30' },
};

export default function AdminDashboardPage() {
    const [data, setData] = useState<DashboardData | null>(null);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const { toast } = useToast();
    const router = useRouter();

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async (isRefresh = false) => {
        if (isRefresh) setRefreshing(true);
        try {
            const res = await fetch('/api/v1/admin/dashboard');
            if (!res.ok) throw new Error('Failed to fetch admin stats');
            const json = await res.json();
            if (json.success) {
                setData(json.data);
            }
        } catch (error) {
            console.error(error);
            toast({
                title: "Error cargando métricas",
                description: "No se pudo conectar con el servidor de control.",
                variant: "destructive"
            });
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    const getHealthColor = (status: string) => {
        switch (status) {
            case 'OPTIMAL': return { text: 'text-emerald-500', bg: 'bg-emerald-500', badge: 'bg-emerald-100 text-emerald-800' };
            case 'WARNING': return { text: 'text-amber-500', bg: 'bg-amber-500', badge: 'bg-amber-100 text-amber-800' };
            case 'CRITICAL': return { text: 'text-red-500', bg: 'bg-red-500', badge: 'bg-red-100 text-red-800' };
            default: return { text: 'text-gray-500', bg: 'bg-gray-500', badge: 'bg-gray-100 text-gray-800' };
        }
    };

    const formatTimeAgo = (date: string) => {
        const seconds = Math.floor((Date.now() - new Date(date).getTime()) / 1000);
        if (seconds < 60) return 'hace unos segundos';
        const minutes = Math.floor(seconds / 60);
        if (minutes < 60) return `hace ${minutes} min`;
        const hours = Math.floor(minutes / 60);
        if (hours < 24) return `hace ${hours}h`;
        const days = Math.floor(hours / 24);
        return `hace ${days}d`;
    };

    if (loading) {
        return (
            <div className="flex-1 space-y-6 p-6">
                <div className="flex items-center justify-between">
                    <Skeleton className="h-10 w-64" />
                    <Skeleton className="h-10 w-32" />
                </div>
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
                    {[1, 2, 3, 4, 5].map(i => <Skeleton key={i} className="h-32" />)}
                </div>
                <div className="grid gap-4 md:grid-cols-2">
                    <Skeleton className="h-64" />
                    <Skeleton className="h-64" />
                </div>
            </div>
        );
    }

    if (!data) return null;

    const healthColors = getHealthColor(data.systemHealth.status);

    return (
        <div className="flex-1 space-y-6 p-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
                        <Shield className="h-8 w-8 text-primary" />
                        Centro de Comando
                    </h1>
                    <p className="text-muted-foreground mt-1">
                        Supervisión global de la plataforma GesNeu
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    <Badge className={healthColors.badge}>
                        {data.systemHealth.status}
                    </Badge>
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => fetchData(true)}
                        disabled={refreshing}
                    >
                        <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                        {refreshing ? 'Actualizando...' : 'Actualizar'}
                    </Button>
                </div>
            </div>

            {/* Primary Stats Row */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
                {/* Tenants */}
                <Card className="relative overflow-hidden">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Empresas</CardTitle>
                        <Building2 className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold">{data.stats.tenants.value}</div>
                        <div className="flex items-center gap-1 text-xs text-muted-foreground mt-1">
                            <TrendingUp className="h-3 w-3 text-emerald-500" />
                            <span className="text-emerald-600">+{data.stats.tenants.trend}</span>
                            <span>este mes</span>
                        </div>
                    </CardContent>
                    <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 to-blue-600" />
                </Card>

                {/* Users */}
                <Card className="relative overflow-hidden">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Usuarios</CardTitle>
                        <Users className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold">{data.stats.users.value}</div>
                        <div className="flex items-center gap-1 text-xs text-muted-foreground mt-1">
                            <span className="text-emerald-600">+{data.stats.users.todayNew}</span>
                            <span>hoy /</span>
                            <span className="text-blue-600">+{data.stats.users.weekNew}</span>
                            <span>semana</span>
                        </div>
                    </CardContent>
                    <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-emerald-500 to-emerald-600" />
                </Card>

                {/* Neumáticos */}
                <Card className="relative overflow-hidden">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Neumáticos</CardTitle>
                        <CircleDot className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold">{data.stats.neumaticos?.value.toLocaleString() || 0}</div>
                        <p className="text-xs text-muted-foreground mt-1">En todo el sistema</p>
                    </CardContent>
                    <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-violet-500 to-violet-600" />
                </Card>

                {/* Vehículos */}
                <Card className="relative overflow-hidden">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Vehículos</CardTitle>
                        <Truck className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold">{data.stats.vehiculos?.value.toLocaleString() || 0}</div>
                        <p className="text-xs text-muted-foreground mt-1">Registrados</p>
                    </CardContent>
                    <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-orange-500 to-orange-600" />
                </Card>

                {/* Operations */}
                <Card className="relative overflow-hidden">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Operaciones</CardTitle>
                        <Zap className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold">{data.stats.operations?.value || 0}</div>
                        <p className="text-xs text-muted-foreground mt-1">Últimos 7 días</p>
                    </CardContent>
                    <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-pink-500 to-pink-600" />
                </Card>
            </div>

            {/* Second Row: Health + Alerts + Quick Actions */}
            <div className="grid gap-4 md:grid-cols-3">
                {/* System Health */}
                <Card>
                    <CardHeader className="pb-3">
                        <CardTitle className="flex items-center gap-2">
                            <Gauge className="h-5 w-5" />
                            Estado del Sistema
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="flex items-center justify-between">
                            <span className="text-sm">Webhooks Success Rate</span>
                            <span className={`font-bold ${data.systemHealth.webhookSuccessRate >= 95 ? 'text-emerald-600' : data.systemHealth.webhookSuccessRate >= 80 ? 'text-amber-600' : 'text-red-600'}`}>
                                {data.systemHealth.webhookSuccessRate}%
                            </span>
                        </div>
                        <Progress value={data.systemHealth.webhookSuccessRate} className="h-2" />

                        <div className="grid grid-cols-2 gap-4 pt-2">
                            <div className="text-center p-3 bg-muted/50 rounded-lg">
                                <div className="text-2xl font-bold">{data.systemHealth.webhooksTotal24h}</div>
                                <div className="text-xs text-muted-foreground">Webhooks 24h</div>
                            </div>
                            <div className="text-center p-3 bg-muted/50 rounded-lg">
                                <div className="text-2xl font-bold flex items-center justify-center gap-1">
                                    <Activity className="h-4 w-4 text-emerald-500" />
                                    {data.systemHealth.activeSessions}
                                </div>
                                <div className="text-xs text-muted-foreground">Sesiones Activas</div>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Alerts Summary */}
                <Card>
                    <CardHeader className="pb-3">
                        <CardTitle className="flex items-center gap-2">
                            <AlertTriangle className="h-5 w-5" />
                            Alertas (24h)
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-3">
                            <div className="flex items-center justify-between p-3 bg-red-50 dark:bg-red-950/30 rounded-lg">
                                <div className="flex items-center gap-2">
                                    <XCircle className="h-5 w-5 text-red-600" />
                                    <span className="font-medium">Críticas</span>
                                </div>
                                <Badge variant="destructive">{data.alerts.critical}</Badge>
                            </div>
                            <div className="flex items-center justify-between p-3 bg-amber-50 dark:bg-amber-950/30 rounded-lg">
                                <div className="flex items-center gap-2">
                                    <AlertTriangle className="h-5 w-5 text-amber-600" />
                                    <span className="font-medium">Advertencias</span>
                                </div>
                                <Badge className="bg-amber-100 text-amber-800">{data.alerts.warning}</Badge>
                            </div>
                            <div className="flex items-center justify-between p-3 bg-blue-50 dark:bg-blue-950/30 rounded-lg">
                                <div className="flex items-center gap-2">
                                    <Clock className="h-5 w-5 text-blue-600" />
                                    <span className="font-medium">Sin Resolver</span>
                                </div>
                                <Badge variant="secondary">{data.alerts.unresolved}</Badge>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Quick Actions */}
                <Card>
                    <CardHeader className="pb-3">
                        <CardTitle className="flex items-center gap-2">
                            <Zap className="h-5 w-5" />
                            Acciones Rápidas
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                        <Button
                            variant="outline"
                            className="w-full justify-start"
                            onClick={() => router.push('/dashboard/admin/tenants')}
                        >
                            <Building2 className="h-4 w-4 mr-2" />
                            Gestionar Empresas
                        </Button>
                        <Button
                            variant="outline"
                            className="w-full justify-start"
                            onClick={() => router.push('/dashboard/alertas')}
                        >
                            <AlertTriangle className="h-4 w-4 mr-2" />
                            Ver Todas las Alertas
                        </Button>
                        <Button
                            variant="outline"
                            className="w-full justify-start"
                            onClick={() => router.push('/dashboard/reportes')}
                        >
                            <FileBarChart className="h-4 w-4 mr-2" />
                            Generar Reportes
                        </Button>
                        <Button
                            variant="outline"
                            className="w-full justify-start"
                            onClick={() => router.push('/dashboard/admin/webhooks')}
                        >
                            <Webhook className="h-4 w-4 mr-2" />
                            Console de Webhooks
                        </Button>
                    </CardContent>
                </Card>
            </div>

            {/* Activity Feed */}
            <Card>
                <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                        <CardTitle className="flex items-center gap-2">
                            <Activity className="h-5 w-5" />
                            Actividad Reciente
                        </CardTitle>
                        <Button variant="ghost" size="sm" onClick={() => router.push('/dashboard/admin/audit')}>
                            Ver Todo →
                        </Button>
                    </div>
                    <CardDescription>Últimas operaciones en la plataforma</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="space-y-3">
                        {data.recentActivity.length === 0 ? (
                            <p className="text-sm text-muted-foreground text-center py-8">
                                No hay actividad reciente registrada.
                            </p>
                        ) : (
                            data.recentActivity.map((log) => {
                                const config = operationConfig[log.operacion] || { icon: Activity, color: 'text-gray-600', bg: 'bg-gray-100' };
                                const Icon = config.icon;

                                return (
                                    <div
                                        key={log.id}
                                        className="flex items-center gap-4 p-3 rounded-lg hover:bg-muted/50 transition-colors"
                                    >
                                        <div className={`p-2 rounded-full ${config.bg}`}>
                                            <Icon className={`h-4 w-4 ${config.color}`} />
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center gap-2">
                                                <span className="font-medium text-sm">{log.operacion}</span>
                                                <span className="text-muted-foreground text-sm">en</span>
                                                <code className="bg-muted px-1.5 py-0.5 rounded text-xs">{log.nombre_tabla}</code>
                                            </div>
                                            <div className="text-xs text-muted-foreground mt-0.5">
                                                {log.usuario?.username || log.usuario_app || 'Sistema'}
                                                {log.empresa?.nombre && (
                                                    <> • <span className="text-blue-600">{log.empresa.nombre}</span></>
                                                )}
                                            </div>
                                        </div>
                                        <div className="text-xs text-muted-foreground whitespace-nowrap">
                                            {formatTimeAgo(log.timestamp_log)}
                                        </div>
                                    </div>
                                );
                            })
                        )}
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
