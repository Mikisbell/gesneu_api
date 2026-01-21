
"use client"

import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import {
    FileText, RefreshCw, ArrowLeft, Search,
    Plus, XCircle, Clock, Download, Filter
} from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { useRouter } from "next/navigation"
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
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"

interface AuditLog {
    id: string
    timestamp_log: string
    operacion: string
    nombre_tabla: string
    entidad_id: string | null
    usuario_app: string | null
    ip_direccion: string | null
    datos_antiguos: any
    datos_nuevos: any
    cambios: any
    usuario: { username: string; email?: string } | null
    empresa: { nombre: string } | null
}

interface AuditResponse {
    success: boolean
    data: {
        logs: AuditLog[]
        filters: { tables: string[] }
        pagination: {
            total: number
            limit: number
            offset: number
            hasMore: boolean
        }
    }
}

const operationConfig: Record<string, { color: string; bg: string }> = {
    INSERT: { color: 'text-emerald-700', bg: 'bg-emerald-100 dark:bg-emerald-900/30' },
    UPDATE: { color: 'text-blue-700', bg: 'bg-blue-100 dark:bg-blue-900/30' },
    DELETE: { color: 'text-red-700', bg: 'bg-red-100 dark:bg-red-900/30' },
}

export default function AdminAuditPage() {
    const router = useRouter()
    const [search, setSearch] = useState("")
    const [operacionFilter, setOperacionFilter] = useState<string>("")
    const [tablaFilter, setTablaFilter] = useState<string>("")
    const [refreshing, setRefreshing] = useState(false)
    const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null)

    const buildUrl = () => {
        const params = new URLSearchParams()
        if (search) params.set('search', search)
        if (operacionFilter && operacionFilter !== 'all') params.set('operacion', operacionFilter)
        if (tablaFilter && tablaFilter !== 'all') params.set('tabla', tablaFilter)
        return `/api/v1/admin/audit?${params.toString()}`
    }

    const { data: response, isLoading, error, refetch } = useQuery<AuditResponse>({
        queryKey: ["admin-audit", search, operacionFilter, tablaFilter],
        queryFn: async () => {
            const res = await fetch(buildUrl())
            if (!res.ok) throw new Error("Error fetching audit logs")
            return res.json()
        }
    })

    const logs = response?.data?.logs || []
    const tables = response?.data?.filters?.tables || []
    const pagination = response?.data?.pagination

    const handleRefresh = async () => {
        setRefreshing(true)
        await refetch()
        setRefreshing(false)
    }

    const formatTimeAgo = (date: string) => {
        const seconds = Math.floor((Date.now() - new Date(date).getTime()) / 1000)
        if (seconds < 60) return 'hace unos segundos'
        const minutes = Math.floor(seconds / 60)
        if (minutes < 60) return `hace ${minutes}m`
        const hours = Math.floor(minutes / 60)
        if (hours < 24) return `hace ${hours}h`
        const days = Math.floor(hours / 24)
        return `hace ${days}d`
    }

    if (isLoading) {
        return (
            <div className="flex-1 space-y-6 p-6">
                <div className="flex items-center gap-4">
                    <Skeleton className="h-10 w-10" />
                    <Skeleton className="h-10 w-64" />
                </div>
                <Skeleton className="h-96" />
            </div>
        )
    }

    if (error) {
        return (
            <div className="flex h-full flex-col items-center justify-center text-destructive p-6">
                <XCircle className="h-12 w-12 mb-4" />
                <p className="text-lg font-semibold">Error al cargar audit trail</p>
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
                <div className="flex items-center gap-4">
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => router.push('/dashboard/admin')}
                    >
                        <ArrowLeft className="h-5 w-5" />
                    </Button>
                    <div>
                        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
                            <FileText className="h-6 w-6 text-primary" />
                            Audit Trail
                        </h1>
                        <p className="text-muted-foreground text-sm mt-0.5">
                            Historial completo de operaciones en la plataforma
                        </p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm">
                        <Download className="h-4 w-4 mr-2" />
                        Exportar CSV
                    </Button>
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
            </div>

            {/* Stats */}
            <div className="grid gap-4 md:grid-cols-4">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Registros</CardTitle>
                        <FileText className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{pagination?.total?.toLocaleString() || 0}</div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Inserciones</CardTitle>
                        <Plus className="h-4 w-4 text-emerald-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-emerald-600">
                            {logs.filter(l => l.operacion === 'INSERT').length}
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Actualizaciones</CardTitle>
                        <RefreshCw className="h-4 w-4 text-blue-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-blue-600">
                            {logs.filter(l => l.operacion === 'UPDATE').length}
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Eliminaciones</CardTitle>
                        <XCircle className="h-4 w-4 text-red-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-red-600">
                            {logs.filter(l => l.operacion === 'DELETE').length}
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Filters & Table */}
            <Card>
                <CardContent className="pt-6">
                    <div className="flex flex-col sm:flex-row gap-4 mb-6">
                        <div className="relative flex-1">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                            <Input
                                placeholder="Buscar por tabla, usuario o ID..."
                                value={search}
                                onChange={(e) => setSearch(e.target.value)}
                                className="pl-9"
                            />
                        </div>
                        <Select value={operacionFilter} onValueChange={setOperacionFilter}>
                            <SelectTrigger className="w-[160px]">
                                <SelectValue placeholder="Operación" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">Todas</SelectItem>
                                <SelectItem value="INSERT">INSERT</SelectItem>
                                <SelectItem value="UPDATE">UPDATE</SelectItem>
                                <SelectItem value="DELETE">DELETE</SelectItem>
                            </SelectContent>
                        </Select>
                        <Select value={tablaFilter} onValueChange={setTablaFilter}>
                            <SelectTrigger className="w-[180px]">
                                <SelectValue placeholder="Tabla" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">Todas las tablas</SelectItem>
                                {tables.map(table => (
                                    <SelectItem key={table} value={table}>{table}</SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>

                    {/* Table */}
                    <div className="rounded-md border">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead className="w-[140px]">Fecha/Hora</TableHead>
                                    <TableHead className="w-[100px]">Operación</TableHead>
                                    <TableHead>Tabla</TableHead>
                                    <TableHead>Usuario</TableHead>
                                    <TableHead>Empresa</TableHead>
                                    <TableHead className="w-[80px]">Detalles</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {logs.length === 0 ? (
                                    <TableRow>
                                        <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">
                                            No se encontraron registros
                                        </TableCell>
                                    </TableRow>
                                ) : (
                                    logs.map((log) => {
                                        const config = operationConfig[log.operacion] || operationConfig.UPDATE
                                        return (
                                            <TableRow key={log.id}>
                                                <TableCell>
                                                    <div className="flex flex-col">
                                                        <span className="text-sm font-medium">
                                                            {new Date(log.timestamp_log).toLocaleTimeString('es-PE')}
                                                        </span>
                                                        <span className="text-xs text-muted-foreground">
                                                            {new Date(log.timestamp_log).toLocaleDateString('es-PE')}
                                                        </span>
                                                    </div>
                                                </TableCell>
                                                <TableCell>
                                                    <Badge className={`${config.bg} ${config.color}`}>
                                                        {log.operacion}
                                                    </Badge>
                                                </TableCell>
                                                <TableCell>
                                                    <code className="bg-muted px-1.5 py-0.5 rounded text-xs">
                                                        {log.nombre_tabla}
                                                    </code>
                                                </TableCell>
                                                <TableCell className="text-sm">
                                                    {log.usuario?.username || log.usuario_app || 'Sistema'}
                                                </TableCell>
                                                <TableCell className="text-sm text-muted-foreground">
                                                    {log.empresa?.nombre || '-'}
                                                </TableCell>
                                                <TableCell>
                                                    <Dialog>
                                                        <DialogTrigger asChild>
                                                            <Button
                                                                variant="ghost"
                                                                size="sm"
                                                                onClick={() => setSelectedLog(log)}
                                                            >
                                                                <Filter className="h-4 w-4" />
                                                            </Button>
                                                        </DialogTrigger>
                                                        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
                                                            <DialogHeader>
                                                                <DialogTitle>Detalles del Registro</DialogTitle>
                                                            </DialogHeader>
                                                            <div className="space-y-4">
                                                                <div className="grid grid-cols-2 gap-4 text-sm">
                                                                    <div>
                                                                        <span className="font-medium">ID:</span> {log.id}
                                                                    </div>
                                                                    <div>
                                                                        <span className="font-medium">Entidad ID:</span> {log.entidad_id || '-'}
                                                                    </div>
                                                                    <div>
                                                                        <span className="font-medium">IP:</span> {log.ip_direccion || '-'}
                                                                    </div>
                                                                </div>
                                                                {log.cambios && (
                                                                    <div>
                                                                        <span className="font-medium text-sm">Cambios:</span>
                                                                        <pre className="mt-2 p-3 bg-muted rounded-lg text-xs overflow-x-auto">
                                                                            {JSON.stringify(log.cambios, null, 2)}
                                                                        </pre>
                                                                    </div>
                                                                )}
                                                            </div>
                                                        </DialogContent>
                                                    </Dialog>
                                                </TableCell>
                                            </TableRow>
                                        )
                                    })
                                )}
                            </TableBody>
                        </Table>
                    </div>

                    {/* Pagination */}
                    {pagination && (
                        <div className="flex items-center justify-between mt-4 text-sm text-muted-foreground">
                            <span>
                                Mostrando {logs.length} de {pagination.total.toLocaleString()} registros
                            </span>
                            {pagination.hasMore && (
                                <Button variant="outline" size="sm">
                                    Cargar más
                                </Button>
                            )}
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    )
}
