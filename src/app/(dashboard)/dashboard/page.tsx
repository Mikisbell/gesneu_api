import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Disc, Truck, AlertTriangle, CheckCircle } from 'lucide-react'
import { DashboardService } from '@/lib/services/dashboard.service'
import { StatusPieChart } from '@/components/dashboard/charts/StatusPieChart'

export const dynamic = 'force-dynamic' // Asegurar datos frescos en cada carga

export default async function DashboardPage() {
    const dashboardService = new DashboardService()
    // Parallel data fetching
    const [stats, inventario] = await Promise.all([
        dashboardService.getGeneralStats(),
        dashboardService.getReporteInventario()
    ])

    return (
        <div className="space-y-6">
            <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">
                            Total Neumáticos
                        </CardTitle>
                        <Disc className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.totalNeumaticos}</div>
                        <p className="text-xs text-muted-foreground">
                            En inventario o instalados
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">
                            Vehículos Activos
                        </CardTitle>
                        <Truck className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.vehiculosActivos}</div>
                        <p className="text-xs text-muted-foreground">
                            Operativos actualmente
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">
                            Alertas Pendientes
                        </CardTitle>
                        <AlertTriangle className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.alertasPendientes}</div>
                        <p className="text-xs text-muted-foreground">
                            Requieren atención
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">
                            Operaciones Hoy
                        </CardTitle>
                        <CheckCircle className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.operacionesHoy}</div>
                        <p className="text-xs text-muted-foreground">
                            Eventos registrados
                        </p>
                    </CardContent>
                </Card>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
                <Card className="col-span-4">
                    <CardHeader>
                        <CardTitle>Resumen Reciente</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-sm text-muted-foreground h-[300px] flex items-center justify-center bg-muted/20 rounded-lg">
                            Gráfico de actividad en desarrollo...
                        </p>
                    </CardContent>
                </Card>

                {/* Status Chart Component */}
                <StatusPieChart data={inventario.por_estado} />
            </div>
        </div>
    )
}
