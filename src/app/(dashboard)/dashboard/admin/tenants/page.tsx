
"use client"

import { useState } from "react"
import { DataTable } from "@/components/ui/data-table"
import { columns, Tenant } from "./columns"
import { TenantDialog } from "./TenantDialog"
import { useQuery } from "@tanstack/react-query"
import {
    Building2, Users, Truck, CircleDot, RefreshCw,
    ArrowLeft, CheckCircle2, XCircle
} from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Badge } from "@/components/ui/badge"
import { useRouter } from "next/navigation"

export default function AdminTenantsPage() {
    const router = useRouter()
    const [refreshing, setRefreshing] = useState(false)

    const { data: response, isLoading, error, refetch } = useQuery<{ success: boolean; data: Tenant[] }>({
        queryKey: ["tenants"],
        queryFn: async () => {
            const res = await fetch("/api/v1/admin/tenants")
            if (!res.ok) throw new Error("Error fetching tenants")
            return res.json()
        }
    })

    const tenants = response?.data || []

    // Calculate summary stats
    const totalTenants = tenants.length
    const activeTenants = tenants.filter(t => t.activo).length
    const totalUsers = tenants.reduce((sum, t) => sum + (t._count?.usuarios || 0), 0)
    const totalVehiculos = tenants.reduce((sum, t) => sum + (t._count?.vehiculos || 0), 0)
    const totalNeumaticos = tenants.reduce((sum, t) => sum + (t._count?.neumaticos || 0), 0)

    const handleRefresh = async () => {
        setRefreshing(true)
        await refetch()
        setRefreshing(false)
    }

    if (isLoading) {
        return (
            <div className="flex-1 space-y-6 p-6">
                <div className="flex items-center gap-4">
                    <Skeleton className="h-10 w-10" />
                    <Skeleton className="h-10 w-64" />
                </div>
                <div className="grid gap-4 md:grid-cols-4">
                    {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-24" />)}
                </div>
                <Skeleton className="h-96" />
            </div>
        )
    }

    if (error) {
        return (
            <div className="flex h-full flex-col items-center justify-center text-destructive p-6">
                <XCircle className="h-12 w-12 mb-4" />
                <p className="text-lg font-semibold">Error al cargar empresas</p>
                <p className="text-sm text-muted-foreground mt-2">{error.message}</p>
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
                            <Building2 className="h-6 w-6 text-primary" />
                            Gestión de Empresas
                        </h1>
                        <p className="text-muted-foreground text-sm mt-0.5">
                            Administra los tenants registrados en la plataforma
                        </p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={handleRefresh}
                        disabled={refreshing}
                    >
                        <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                        Actualizar
                    </Button>
                    <TenantDialog />
                </div>
            </div>

            {/* Stats Summary */}
            <div className="grid gap-4 md:grid-cols-5">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Empresas</CardTitle>
                        <Building2 className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{totalTenants}</div>
                        <div className="flex items-center gap-2 mt-1">
                            <Badge variant="secondary" className="text-xs">
                                <CheckCircle2 className="h-3 w-3 mr-1" />
                                {activeTenants} activas
                            </Badge>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Usuarios</CardTitle>
                        <Users className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{totalUsers.toLocaleString()}</div>
                        <p className="text-xs text-muted-foreground">En todas las empresas</p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Vehículos</CardTitle>
                        <Truck className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{totalVehiculos.toLocaleString()}</div>
                        <p className="text-xs text-muted-foreground">Registrados</p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Neumáticos</CardTitle>
                        <CircleDot className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{totalNeumaticos.toLocaleString()}</div>
                        <p className="text-xs text-muted-foreground">En gestión</p>
                    </CardContent>
                </Card>

                <Card className="bg-gradient-to-br from-primary/10 to-primary/5 border-primary/20">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Promedio/Empresa</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-1 text-sm">
                            <div className="flex justify-between">
                                <span className="text-muted-foreground">Usuarios:</span>
                                <span className="font-medium">{totalTenants > 0 ? Math.round(totalUsers / totalTenants) : 0}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-muted-foreground">Vehículos:</span>
                                <span className="font-medium">{totalTenants > 0 ? Math.round(totalVehiculos / totalTenants) : 0}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-muted-foreground">Neumáticos:</span>
                                <span className="font-medium">{totalTenants > 0 ? Math.round(totalNeumaticos / totalTenants) : 0}</span>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Data Table */}
            <Card>
                <CardContent className="pt-6">
                    <DataTable
                        data={tenants}
                        columns={columns}
                        searchKey="nombre"
                    />
                </CardContent>
            </Card>
        </div>
    )
}
