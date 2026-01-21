
"use client"

import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import {
    Webhook, RefreshCw, CheckCircle2, XCircle,
    Clock, ExternalLink, RotateCcw, AlertTriangle
} from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"

interface WebhookData {
    id: string
    nombre: string
    url: string
    activo: boolean
    empresa: { nombre: string } | null
    _count: { logs: number }
}

interface WebhookLog {
    id: string
    exitoso: boolean
    status_code: number | null
    duracion_ms: number | null
    error_mensaje: string | null
    creado_en: string
    webhook: {
        nombre: string
        url: string
        empresa: { nombre: string } | null
    }
}

interface WebhookResponse {
    success: boolean
    data: {
        webhooks: WebhookData[]
        logs: WebhookLog[]
        stats: {
            total24h: number
            success24h: number
            failed24h: number
            successRate: number
        }
    }
}

export default function WebhookConsolePage() {
    const [statusFilter, setStatusFilter] = useState<string>("")
    const [refreshing, setRefreshing] = useState(false)

    const buildUrl = () => {
        const params = new URLSearchParams()
        if (statusFilter && statusFilter !== 'all') params.set('exitoso', statusFilter)
        return `/api/v1/admin/webhooks?${params.toString()}`
    }

    const { data: response, isLoading, error, refetch } = useQuery<WebhookResponse>({
        queryKey: ["webhook-console", statusFilter],
        queryFn: async () => {
            const res = await fetch(buildUrl())
            if (!res.ok) throw new Error("Error fetching webhooks")
            return res.json()
        }
    })

    const handleRefresh = async () => {
        setRefreshing(true)
        await refetch()
        setRefreshing(false)
    }

    const data = response?.data
    const webhooks = data?.webhooks || []
    const logs = data?.logs || []
    const stats = data?.stats || { total24h: 0, success24h: 0, failed24h: 0, successRate: 100 }

    if (isLoading) {
        return (
            <div className="flex-1 space-y-6 p-6">
                <Skeleton className="h-10 w-64" />
                <div className="grid gap-4 md:grid-cols-4">
                    {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-24" />)}
                </div>
                <Skeleton className="h-64" />
            </div>
        )
    }

    if (error) {
        return (
            <div className="flex h-full flex-col items-center justify-center text-destructive p-6">
                <XCircle className="h-12 w-12 mb-4" />
                <p className="text-lg font-semibold">Error al cargar webhooks</p>
                <Button onClick={() => refetch()} className="mt-4">
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Reintentar
                </Button>
            </div>
        )
    }

    return (
        <div className="flex-1 space-y-6 p-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
                        <Webhook className="h-6 w-6 text-primary" />
                        Webhook Console
                    </h1>
                    <p className="text-muted-foreground text-sm mt-0.5">
                        Monitoreo de integraciones y logs de ejecución
                    </p>
                </div>
                <Button
                    variant="outline"
                    size="sm"
                    onClick={handleRefresh}
                    disabled={refreshing}
                >
                    <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                    Actualizar
                </Button>
            </div>

            {/* Stats */}
            <div className="grid gap-4 md:grid-cols-4">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Webhooks Activos</CardTitle>
                        <Webhook className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{webhooks.filter(w => w.activo).length}</div>
                        <p className="text-xs text-muted-foreground">de {webhooks.length} total</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Ejecuciones (24h)</CardTitle>
                        <Clock className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.total24h}</div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Exitosos</CardTitle>
                        <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-emerald-600">{stats.success24h}</div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Fallidos</CardTitle>
                        <XCircle className="h-4 w-4 text-red-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-red-600">{stats.failed24h}</div>
                    </CardContent>
                </Card>
            </div>

            {/* Success Rate */}
            <Card>
                <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium flex items-center justify-between">
                        <span>Tasa de Éxito (24h)</span>
                        <span className={`text-lg font-bold ${stats.successRate >= 95 ? 'text-emerald-600' : stats.successRate >= 80 ? 'text-amber-600' : 'text-red-600'}`}>
                            {stats.successRate}%
                        </span>
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <Progress value={stats.successRate} className="h-2" />
                </CardContent>
            </Card>

            {/* Logs Table */}
            <Card>
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <div>
                            <CardTitle>Logs de Ejecución</CardTitle>
                            <CardDescription>Últimas 50 ejecuciones de webhooks</CardDescription>
                        </div>
                        <Select value={statusFilter} onValueChange={setStatusFilter}>
                            <SelectTrigger className="w-[140px]">
                                <SelectValue placeholder="Estado" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">Todos</SelectItem>
                                <SelectItem value="true">Exitosos</SelectItem>
                                <SelectItem value="false">Fallidos</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Webhook</TableHead>
                                <TableHead>Empresa</TableHead>
                                <TableHead>Estado</TableHead>
                                <TableHead>Código</TableHead>
                                <TableHead>Duración</TableHead>
                                <TableHead>Fecha</TableHead>
                                <TableHead className="w-[80px]">Acción</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {logs.length === 0 ? (
                                <TableRow>
                                    <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                                        No hay logs de ejecución
                                    </TableCell>
                                </TableRow>
                            ) : (
                                logs.map((log) => (
                                    <TableRow key={log.id}>
                                        <TableCell>
                                            <div className="flex flex-col">
                                                <span className="font-medium">{log.webhook?.nombre || 'Desconocido'}</span>
                                                <span className="text-xs text-muted-foreground truncate max-w-[200px]">
                                                    {log.webhook?.url}
                                                </span>
                                            </div>
                                        </TableCell>
                                        <TableCell className="text-sm">
                                            {log.webhook?.empresa?.nombre || '-'}
                                        </TableCell>
                                        <TableCell>
                                            {log.exitoso ? (
                                                <Badge className="bg-emerald-100 text-emerald-800">
                                                    <CheckCircle2 className="h-3 w-3 mr-1" />
                                                    OK
                                                </Badge>
                                            ) : (
                                                <Badge variant="destructive">
                                                    <XCircle className="h-3 w-3 mr-1" />
                                                    Error
                                                </Badge>
                                            )}
                                        </TableCell>
                                        <TableCell>
                                            <code className="bg-muted px-1.5 py-0.5 rounded text-xs">
                                                {log.status_code || '-'}
                                            </code>
                                        </TableCell>
                                        <TableCell className="text-sm text-muted-foreground">
                                            {log.duracion_ms ? `${log.duracion_ms}ms` : '-'}
                                        </TableCell>
                                        <TableCell className="text-sm text-muted-foreground">
                                            {new Date(log.creado_en).toLocaleString('es-PE')}
                                        </TableCell>
                                        <TableCell>
                                            {!log.exitoso && (
                                                <Button variant="ghost" size="sm" title="Reintentar">
                                                    <RotateCcw className="h-4 w-4" />
                                                </Button>
                                            )}
                                        </TableCell>
                                    </TableRow>
                                ))
                            )}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>
        </div>
    )
}
