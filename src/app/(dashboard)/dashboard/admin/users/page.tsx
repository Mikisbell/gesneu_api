
"use client"

import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import {
    Users, RefreshCw, ArrowLeft, Search,
    CheckCircle2, XCircle, Building2, Shield
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

interface User {
    id: string
    username: string
    email: string
    nombre_completo: string
    rol: string
    activo: boolean
    creado_en: string
    empresa: { id: string; nombre: string } | null
}

interface UsersResponse {
    success: boolean
    data: {
        users: User[]
        pagination: {
            total: number
            limit: number
            offset: number
            hasMore: boolean
        }
    }
}

const roleColors: Record<string, string> = {
    SUPERADMIN: "bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400",
    ADMIN: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400",
    GESTOR: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400",
    OPERADOR: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300",
}

export default function AdminUsersPage() {
    const router = useRouter()
    const [search, setSearch] = useState("")
    const [rolFilter, setRolFilter] = useState<string>("")
    const [activoFilter, setActivoFilter] = useState<string>("")
    const [refreshing, setRefreshing] = useState(false)

    const buildUrl = () => {
        const params = new URLSearchParams()
        if (search) params.set('search', search)
        if (rolFilter && rolFilter !== 'all') params.set('rol', rolFilter)
        if (activoFilter && activoFilter !== 'all') params.set('activo', activoFilter)
        return `/api/v1/admin/users?${params.toString()}`
    }

    const { data: response, isLoading, error, refetch } = useQuery<UsersResponse>({
        queryKey: ["admin-users", search, rolFilter, activoFilter],
        queryFn: async () => {
            const res = await fetch(buildUrl())
            if (!res.ok) throw new Error("Error fetching users")
            return res.json()
        }
    })

    const users = response?.data?.users || []
    const pagination = response?.data?.pagination

    const handleRefresh = async () => {
        setRefreshing(true)
        await refetch()
        setRefreshing(false)
    }

    // Stats
    const totalUsers = pagination?.total || 0
    const activeUsers = users.filter(u => u.activo).length
    const adminCount = users.filter(u => ['ADMIN', 'SUPERADMIN'].includes(u.rol)).length

    if (isLoading) {
        return (
            <div className="flex-1 space-y-6 p-6">
                <div className="flex items-center gap-4">
                    <Skeleton className="h-10 w-10" />
                    <Skeleton className="h-10 w-64" />
                </div>
                <div className="grid gap-4 md:grid-cols-3">
                    {[1, 2, 3].map(i => <Skeleton key={i} className="h-24" />)}
                </div>
                <Skeleton className="h-96" />
            </div>
        )
    }

    if (error) {
        return (
            <div className="flex h-full flex-col items-center justify-center text-destructive p-6">
                <XCircle className="h-12 w-12 mb-4" />
                <p className="text-lg font-semibold">Error al cargar usuarios</p>
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
                            <Users className="h-6 w-6 text-primary" />
                            Directorio de Usuarios
                        </h1>
                        <p className="text-muted-foreground text-sm mt-0.5">
                            Vista global de usuarios en todas las empresas
                        </p>
                    </div>
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
            <div className="grid gap-4 md:grid-cols-3">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Usuarios</CardTitle>
                        <Users className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{totalUsers}</div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Activos</CardTitle>
                        <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-emerald-600">{activeUsers}</div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Administradores</CardTitle>
                        <Shield className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{adminCount}</div>
                    </CardContent>
                </Card>
            </div>

            {/* Filters */}
            <Card>
                <CardContent className="pt-6">
                    <div className="flex flex-col sm:flex-row gap-4 mb-6">
                        <div className="relative flex-1">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                            <Input
                                placeholder="Buscar por nombre, email o username..."
                                value={search}
                                onChange={(e) => setSearch(e.target.value)}
                                className="pl-9"
                            />
                        </div>
                        <Select value={rolFilter} onValueChange={setRolFilter}>
                            <SelectTrigger className="w-[160px]">
                                <SelectValue placeholder="Todos los roles" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">Todos los roles</SelectItem>
                                <SelectItem value="SUPERADMIN">SuperAdmin</SelectItem>
                                <SelectItem value="ADMIN">Admin</SelectItem>
                                <SelectItem value="GESTOR">Gestor</SelectItem>
                                <SelectItem value="OPERADOR">Operador</SelectItem>
                            </SelectContent>
                        </Select>
                        <Select value={activoFilter} onValueChange={setActivoFilter}>
                            <SelectTrigger className="w-[140px]">
                                <SelectValue placeholder="Estado" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">Todos</SelectItem>
                                <SelectItem value="true">Activos</SelectItem>
                                <SelectItem value="false">Inactivos</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>

                    {/* Table */}
                    <div className="rounded-md border">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Usuario</TableHead>
                                    <TableHead>Empresa</TableHead>
                                    <TableHead>Rol</TableHead>
                                    <TableHead>Estado</TableHead>
                                    <TableHead>Registro</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {users.length === 0 ? (
                                    <TableRow>
                                        <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                                            No se encontraron usuarios
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
                                                {user.empresa ? (
                                                    <div className="flex items-center gap-1.5">
                                                        <Building2 className="h-3.5 w-3.5 text-muted-foreground" />
                                                        <span className="text-sm">{user.empresa.nombre}</span>
                                                    </div>
                                                ) : (
                                                    <span className="text-muted-foreground text-sm">Sin empresa</span>
                                                )}
                                            </TableCell>
                                            <TableCell>
                                                <Badge className={roleColors[user.rol] || ""}>
                                                    {user.rol}
                                                </Badge>
                                            </TableCell>
                                            <TableCell>
                                                <Badge variant={user.activo ? "default" : "destructive"}>
                                                    {user.activo ? "Activo" : "Inactivo"}
                                                </Badge>
                                            </TableCell>
                                            <TableCell className="text-sm text-muted-foreground">
                                                {new Date(user.creado_en).toLocaleDateString('es-PE')}
                                            </TableCell>
                                        </TableRow>
                                    ))
                                )}
                            </TableBody>
                        </Table>
                    </div>

                    {/* Pagination info */}
                    {pagination && (
                        <div className="flex items-center justify-between mt-4 text-sm text-muted-foreground">
                            <span>
                                Mostrando {users.length} de {pagination.total} usuarios
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
