
"use client"

import { use } from "react"
import { useQuery } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import {
    Building2, Users, Truck, CircleDot, AlertTriangle,
    ArrowLeft, RefreshCw, Power, CheckCircle2, XCircle,
    Activity, Clock
} from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Badge } from "@/components/ui/badge"
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"

interface TenantDetailData {
    tenant: {
        id: string
        nombre: string
        ruc: string
        direccion: string | null
        activo: boolean
        creado_en: string
        _count: {
            usuarios: number
            vehiculos: number
            neumaticos: number
            alertas: number
        }
    }
    users: Array<{
        id: string
        username: string
        email: string
        nombre_completo: string
        rol: string
        activo: boolean
        creado_en: string
    }>
    recentAlerts: Array<{
        id: string
        tipo_alerta: string
        severidad: string
        mensaje: string
        leida: boolean
        creada_en: string
    }>
    recentActivity: Array<{
        id: string
        operacion: string
        nombre_tabla: string
        timestamp_log: string
        usuario: { username: string } | null
    }>
}

const roleColors: Record<string, string> = {
    SUPERADMIN: "bg-purple-100 text-purple-800",
    ADMIN: "bg-blue-100 text-blue-800",
    ADMINISTRADOR: "bg-blue-100 text-blue-800",
    GESTOR: "bg-emerald-100 text-emerald-800",
    OPERADOR: "bg-gray-100 text-gray-800",
}

const severityColors: Record<string, string> = {
    CRITICAL: "bg-red-100 text-red-800",
    WARNING: "bg-amber-100 text-amber-800",
    INFO: "bg-blue-100 text-blue-800",
}

export default function TenantDetailPage({ params }: { params: Promise<{ id: string }> }) {
    const { id } = use(params)
    const router = useRouter()

    const { data: response, isLoading, error, refetch } = useQuery<{ success: boolean; data: TenantDetailData }>({
        queryKey: ["tenant-detail", id],
        queryFn: async () => {
            const res = await fetch(`/api/v1/admin/tenants/${id}`)
            if (!res.ok) throw new Error("Error fetching tenant")
            return res.json()
        }
    })

    const data = response?.data

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

    if (error || !data) {
        return (
            <div className="flex h-full flex-col items-center justify-center text-destructive p-6">
                <XCircle className="h-12 w-12 mb-4" />
                <p className="text-lg font-semibold">Error al cargar empresa</p>
                <Button onClick={() => refetch()} className="mt-4">
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Reintentar
                </Button>
            </div>
        )
    }

    const { tenant, users, recentAlerts, recentActivity } = data

    return (
        <div className="flex-1 space-y-6 p-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => router.push('/dashboard/admin/tenants')}
                    >
                        <ArrowLeft className="h-5 w-5" />
                    </Button>
                    <div>
                        <div className="flex items-center gap-3">
                            <h1 className="text-2xl font-bold tracking-tight">
                                {tenant.nombre}
                            </h1>
                            <Badge variant={tenant.activo ? "default" : "destructive"}>
                                {tenant.activo ? "Activo" : "Suspendido"}
                            </Badge>
                        </div>
                        <p className="text-muted-foreground text-sm mt-0.5">
                            RUC: {tenant.ruc} • {tenant.direccion || 'Sin dirección'}
                        </p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" onClick={() => refetch()}>
                        <RefreshCw className="h-4 w-4 mr-2" />
                        Actualizar
                    </Button>
                    <Button
                        variant={tenant.activo ? "destructive" : "default"}
                        size="sm"
                    >
                        <Power className="h-4 w-4 mr-2" />
                        {tenant.activo ? "Suspender" : "Reactivar"}
                    </Button>
                </div>
            </div>

            {/* Stats */}
            <div className="grid gap-4 md:grid-cols-4">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Usuarios</CardTitle>
                        <Users className="h-4 w-4 text-blue-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{tenant._count.usuarios}</div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Vehículos</CardTitle>
                        <Truck className="h-4 w-4 text-orange-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{tenant._count.vehiculos}</div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Neumáticos</CardTitle>
                        <CircleDot className="h-4 w-4 text-violet-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{tenant._count.neumaticos}</div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Alertas</CardTitle>
                        <AlertTriangle className="h-4 w-4 text-amber-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{tenant._count.alertas}</div>
                    </CardContent>
                </Card>
            </div>

            {/* Users Table */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Users className="h-5 w-5" />
                        Usuarios de la Empresa
                    </CardTitle>
                    <CardDescription>Últimos 10 usuarios registrados</CardDescription>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Usuario</TableHead>
                                <TableHead>Rol</TableHead>
                                <TableHead>Estado</TableHead>
                                <TableHead>Registro</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {users.length === 0 ? (
                                <TableRow>
                                    <TableCell colSpan={4} className="text-center py-4 text-muted-foreground">
                                        No hay usuarios registrados
                                    </TableCell>
                                </TableRow>
                            ) : (
                                users.map((user) => (
                                    <TableRow key={user.id}>
                                        <TableCell>
                                            <div className="flex flex-col">
                                                <span className="font-medium">{user.nombre_completo}</span>
                                                <span className="text-xs text-muted-foreground">{user.email}</span>
                                            </div>
                                        </TableCell>
                                        <TableCell>
                                            <Badge className={roleColors[user.rol] || ""}>
                                                {user.rol}
                                            </Badge>
                                        </TableCell>
                                        <TableCell>
                                            {user.activo ? (
                                                <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                                            ) : (
                                                <XCircle className="h-4 w-4 text-red-500" />
                                            )}
                                        </TableCell>
                                        <TableCell className="text-sm text-muted-foreground">
                                            {new Date(user.creado_en).toLocaleDateString('es-PE')}
                                        </TableCell>
                                    </TableRow>
                                ))
                            )}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>

            {/* Two Column: Alerts + Activity */}
            <div className="grid gap-4 md:grid-cols-2">
                {/* Recent Alerts */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <AlertTriangle className="h-5 w-5" />
                            Alertas Recientes
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        {recentAlerts.length === 0 ? (
                            <p className="text-sm text-muted-foreground text-center py-4">
                                Sin alertas recientes
                            </p>
                        ) : (
                            <div className="space-y-3">
                                {recentAlerts.map((alert) => (
                                    <div key={alert.id} className="flex items-start gap-3 p-2 rounded-lg hover:bg-muted/50">
                                        <Badge className={severityColors[alert.severidad] || ""}>
                                            {alert.severidad}
                                        </Badge>
                                        <div className="flex-1 min-w-0">
                                            <p className="text-sm font-medium truncate">{alert.tipo_alerta}</p>
                                            <p className="text-xs text-muted-foreground truncate">{alert.mensaje}</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Recent Activity */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Activity className="h-5 w-5" />
                            Actividad Reciente
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        {recentActivity.length === 0 ? (
                            <p className="text-sm text-muted-foreground text-center py-4">
                                Sin actividad reciente
                            </p>
                        ) : (
                            <div className="space-y-3">
                                {recentActivity.map((log) => (
                                    <div key={log.id} className="flex items-center gap-3 text-sm">
                                        <Clock className="h-4 w-4 text-muted-foreground" />
                                        <span className="font-medium">{log.operacion}</span>
                                        <code className="bg-muted px-1.5 py-0.5 rounded text-xs">{log.nombre_tabla}</code>
                                        <span className="text-muted-foreground ml-auto">
                                            {log.usuario?.username || 'Sistema'}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    )
}
