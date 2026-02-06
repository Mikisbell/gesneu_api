/**
 * 🏠 Dashboard Page - Server Component (2026)
 * Hybrid rendering: Static shell + Streaming data
 */

import { Suspense } from 'react'
import { Disc, Truck, AlertTriangle, CheckCircle } from 'lucide-react'
import { DashboardService } from '@/lib/services/dashboard.service'
import { StatusPieChart } from '@/components/dashboard/charts/StatusPieChart'
import { PageHeader, SkeletonTable } from '@/components/ui/animated'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { requireAuth } from '@/lib/auth/authorization'
import { StatCard } from '@/components/dashboard/stat-card'

// ✅ 2026: Force dynamic para datos frescos
export const dynamic = 'force-dynamic'

// ============================================
// MAIN PAGE (Server Component)
// ============================================

export default async function DashboardPage() {
    const session = await requireAuth()
    const empresaId = session.user.empresa_id!

    return (
        <div className="space-y-6">
            {/* ✅ Header es estático - renderiza instant */}
            <PageHeader
                title="Dashboard"
                description="Vista general del sistema de gestión de neumáticos"
            />

            {/* ✅ Stats cards con Suspense - streams incrementalmente */}
            <Suspense fallback={<StatsCardsSkeleton />}>
                <StatsCards empresaId={empresaId} />
            </Suspense>

            {/* ✅ Charts con Suspense independiente */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
                <Suspense fallback={<ChartSkeleton className="col-span-4" />}>
                    <RecentActivityChart empresaId={empresaId} />
                </Suspense>

                <Suspense fallback={<ChartSkeleton className="col-span-3" />}>
                    <StatusChart empresaId={empresaId} />
                </Suspense>
            </div>
        </div>
    )
}

// ============================================
// STATS CARDS (Server Component)
// ============================================

async function StatsCards({ empresaId }: { empresaId: string }) {
    const dashboardService = new DashboardService()
    const stats = await dashboardService.getGeneralStats(empresaId)

    return (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <StatCard
                title="Total Neumáticos"
                value={stats.totalNeumaticos}
                description="En inventario o instalados"
                icon={<Disc className="h-4 w-4 text-muted-foreground" />}
                delay={0}
            />
            <StatCard
                title="Vehículos Activos"
                value={stats.vehiculosActivos}
                description="Operativos actualmente"
                icon={<Truck className="h-4 w-4 text-muted-foreground" />}
                delay={0.1}
            />
            <StatCard
                title="Alertas Pendientes"
                value={stats.alertasPendientes}
                description="Requieren atención"
                icon={<AlertTriangle className="h-4 w-4 text-muted-foreground" />}
                delay={0.2}
            />
            <StatCard
                title="Operaciones Hoy"
                value={stats.operacionesHoy}
                description="Eventos registrados"
                icon={<CheckCircle className="h-4 w-4 text-muted-foreground" />}
                delay={0.3}
            />
        </div>
    )
}

// ============================================
// STAT CARD (Now imported from client component)
// ============================================
// import { StatCard } from '@/components/dashboard/stat-card'
// ============================================
// STATUS CHART (Server Component)
// ============================================

async function StatusChart({ empresaId }: { empresaId: string }) {
    const dashboardService = new DashboardService()
    const inventario = await dashboardService.getReporteInventario(empresaId)

    return <StatusPieChart data={inventario.por_estado} />
}

// ============================================
// RECENT ACTIVITY (Server Component)
// ============================================

async function RecentActivityChart({ empresaId }: { empresaId: string }) {
    // TODO: Implementar servicio de actividad reciente

    return (
        <Card className="col-span-4">
            <CardHeader>
                <CardTitle>Actividad Reciente</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="h-[300px] flex items-center justify-center bg-muted/20 rounded-lg">
                    <p className="text-sm text-muted-foreground">
                        Gráfico de actividad en desarrollo...
                    </p>
                </div>
            </CardContent>
        </Card>
    )
}

// ============================================
// LOADING SKELETONS
// ============================================

function StatsCardsSkeleton() {
    return (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {[...Array(4)].map((_, i) => (
                <Card key={i}>
                    <CardHeader className="space-y-0 pb-2">
                        <div className="h-4 w-24 bg-muted animate-pulse rounded" />
                    </CardHeader>
                    <CardContent>
                        <div className="h-8 w-16 bg-muted animate-pulse rounded mb-1" />
                        <div className="h-3 w-32 bg-muted animate-pulse rounded" />
                    </CardContent>
                </Card>
            ))}
        </div>
    )
}

function ChartSkeleton({ className }: { className?: string }) {
    return (
        <Card className={className}>
            <CardHeader>
                <div className="h-6 w-32 bg-muted animate-pulse rounded" />
            </CardHeader>
            <CardContent>
                <div className="h-[300px] bg-muted/20 animate-pulse rounded" />
            </CardContent>
        </Card>
    )
}
