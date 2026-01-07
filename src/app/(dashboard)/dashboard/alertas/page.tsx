'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/components/ui/use-toast';
import { Bell, AlertTriangle, AlertCircle, Info, CheckCircle, Loader2, Eye, RefreshCw } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';

interface Alerta {
    id: string;
    tipo: string;
    severidad: 'INFO' | 'WARNING' | 'CRITICAL';
    mensaje: string;
    leida: boolean;
    resuelta: boolean;
    creado_en: string;
    neumatico?: {
        id: string;
        numero_serie: string;
    };
}

const SEVERIDAD_CONFIG = {
    CRITICAL: { icon: AlertCircle, color: 'text-red-500', bg: 'bg-red-50 border-red-200', badge: 'bg-red-500' },
    WARNING: { icon: AlertTriangle, color: 'text-amber-500', bg: 'bg-amber-50 border-amber-200', badge: 'bg-amber-500' },
    INFO: { icon: Info, color: 'text-blue-500', bg: 'bg-blue-50 border-blue-200', badge: 'bg-blue-500' },
};

const TIPO_LABELS: Record<string, string> = {
    PROFUNDIDAD_MINIMA: 'Profundidad Mínima',
    REENCAUCHE_MAXIMO: 'Límite Reencauches',
    DESGASTE_IRREGULAR: 'Desgaste Irregular',
    VENCIMIENTO_DOT: 'Vencimiento DOT',
    PRESION_BAJA: 'Presión Baja',
    PRESION_ALTA: 'Presión Alta',
};

export default function AlertasPage() {
    const { toast } = useToast();
    const queryClient = useQueryClient();
    const [severidadFilter, setSeveridadFilter] = useState<string>('all');
    const [estadoFilter, setEstadoFilter] = useState<string>('pendientes');

    // Fetch alertas
    const { data: alertas, isLoading, refetch } = useQuery({
        queryKey: ['alertas', severidadFilter, estadoFilter],
        queryFn: async () => {
            let url = '/api/v1/alertas?limit=100';
            if (severidadFilter !== 'all') url += `&severidad=${severidadFilter}`;
            if (estadoFilter === 'pendientes') url += '&resuelta=false';
            if (estadoFilter === 'resueltas') url += '&resuelta=true';
            if (estadoFilter === 'no_leidas') url += '&leida=false';
            const res = await apiClient<Alerta[]>(url);
            return res;
        },
    });

    // Mark as read mutation
    const markAsReadMutation = useMutation({
        mutationFn: (id: string) =>
            apiClient(`/api/v1/alertas/${id}/leer`, { method: 'POST' }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['alertas'] });
            toast({ title: '✅ Alerta marcada como leída' });
        },
    });

    // Resolve mutation
    const resolveMutation = useMutation({
        mutationFn: (id: string) =>
            apiClient(`/api/v1/alertas/${id}/resolver`, { method: 'POST' }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['alertas'] });
            toast({ title: '✅ Alerta resuelta' });
        },
    });

    // Stats
    const stats = {
        total: alertas?.length || 0,
        critical: alertas?.filter(a => a.severidad === 'CRITICAL' && !a.resuelta).length || 0,
        warning: alertas?.filter(a => a.severidad === 'WARNING' && !a.resuelta).length || 0,
        unread: alertas?.filter(a => !a.leida).length || 0,
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
                        <Bell className="h-8 w-8" /> Alertas
                    </h1>
                    <p className="text-muted-foreground">Centro de notificaciones y alertas del sistema</p>
                </div>
                <Button variant="outline" onClick={() => refetch()}>
                    <RefreshCw className="h-4 w-4 mr-2" /> Actualizar
                </Button>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-muted-foreground">Total Alertas</p>
                                <p className="text-3xl font-bold">{stats.total}</p>
                            </div>
                            <Bell className="h-8 w-8 text-muted-foreground" />
                        </div>
                    </CardContent>
                </Card>
                <Card className="border-red-200 bg-red-50">
                    <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-red-600">Críticas</p>
                                <p className="text-3xl font-bold text-red-700">{stats.critical}</p>
                            </div>
                            <AlertCircle className="h-8 w-8 text-red-500" />
                        </div>
                    </CardContent>
                </Card>
                <Card className="border-amber-200 bg-amber-50">
                    <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-amber-600">Advertencias</p>
                                <p className="text-3xl font-bold text-amber-700">{stats.warning}</p>
                            </div>
                            <AlertTriangle className="h-8 w-8 text-amber-500" />
                        </div>
                    </CardContent>
                </Card>
                <Card className="border-blue-200 bg-blue-50">
                    <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-blue-600">Sin Leer</p>
                                <p className="text-3xl font-bold text-blue-700">{stats.unread}</p>
                            </div>
                            <Eye className="h-8 w-8 text-blue-500" />
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Filters */}
            <Card>
                <CardContent className="pt-6">
                    <div className="flex gap-4">
                        <div className="w-48">
                            <Select value={severidadFilter} onValueChange={setSeveridadFilter}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Severidad" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="all">Todas</SelectItem>
                                    <SelectItem value="CRITICAL">🔴 Críticas</SelectItem>
                                    <SelectItem value="WARNING">🟡 Advertencias</SelectItem>
                                    <SelectItem value="INFO">🔵 Información</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="w-48">
                            <Select value={estadoFilter} onValueChange={setEstadoFilter}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Estado" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="all">Todas</SelectItem>
                                    <SelectItem value="pendientes">Pendientes</SelectItem>
                                    <SelectItem value="no_leidas">Sin leer</SelectItem>
                                    <SelectItem value="resueltas">Resueltas</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Alerts List */}
            <Card>
                <CardHeader>
                    <CardTitle>Listado de Alertas</CardTitle>
                    <CardDescription>
                        {estadoFilter === 'pendientes' ? 'Alertas que requieren atención' : 'Historial de alertas'}
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    {isLoading ? (
                        <div className="flex justify-center py-8">
                            <Loader2 className="h-8 w-8 animate-spin text-primary" />
                        </div>
                    ) : (alertas || []).length === 0 ? (
                        <div className="text-center py-12 text-muted-foreground">
                            <CheckCircle className="h-12 w-12 mx-auto mb-4 text-green-500" />
                            <p>No hay alertas pendientes</p>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {(alertas || []).map((alerta) => {
                                const config = SEVERIDAD_CONFIG[alerta.severidad];
                                const Icon = config.icon;
                                return (
                                    <div
                                        key={alerta.id}
                                        className={`p-4 rounded-lg border ${config.bg} ${!alerta.leida ? 'ring-2 ring-offset-2 ring-primary/20' : ''}`}
                                    >
                                        <div className="flex items-start justify-between gap-4">
                                            <div className="flex items-start gap-3">
                                                <Icon className={`h-5 w-5 mt-0.5 ${config.color}`} />
                                                <div>
                                                    <div className="flex items-center gap-2 mb-1">
                                                        <Badge className={`${config.badge} text-white text-xs`}>
                                                            {alerta.severidad}
                                                        </Badge>
                                                        <Badge variant="outline" className="text-xs">
                                                            {TIPO_LABELS[alerta.tipo] || alerta.tipo}
                                                        </Badge>
                                                        {!alerta.leida && (
                                                            <Badge variant="secondary" className="text-xs">Nueva</Badge>
                                                        )}
                                                    </div>
                                                    <p className="font-medium">{alerta.mensaje}</p>
                                                    {alerta.neumatico && (
                                                        <p className="text-sm text-muted-foreground mt-1">
                                                            Neumático: {alerta.neumatico.numero_serie}
                                                        </p>
                                                    )}
                                                    <p className="text-xs text-muted-foreground mt-2">
                                                        {formatDistanceToNow(new Date(alerta.creado_en), { addSuffix: true, locale: es })}
                                                    </p>
                                                </div>
                                            </div>
                                            <div className="flex gap-2">
                                                {!alerta.leida && (
                                                    <Button
                                                        size="sm"
                                                        variant="ghost"
                                                        onClick={() => markAsReadMutation.mutate(alerta.id)}
                                                        disabled={markAsReadMutation.isPending}
                                                    >
                                                        <Eye className="h-4 w-4" />
                                                    </Button>
                                                )}
                                                {!alerta.resuelta && (
                                                    <Button
                                                        size="sm"
                                                        variant="outline"
                                                        onClick={() => resolveMutation.mutate(alerta.id)}
                                                        disabled={resolveMutation.isPending}
                                                    >
                                                        <CheckCircle className="h-4 w-4 mr-1" /> Resolver
                                                    </Button>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
