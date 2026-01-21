'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import {
    LayoutDashboard,
    Users,
    Package,
    Truck,
    Settings,
    LogOut,
    Disc,
    Wrench,
    Warehouse,
    UserCog,
    ClipboardCheck,
    RotateCw,
    Trash2,
    Bell,
    FileText,
    Shield,
    Share2,
    Building
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { signOut, useSession } from 'next-auth/react'
import { PERMISSIONS } from '@/lib/auth/permissions'
import { usePermission } from '@/hooks/use-permission'

const catalogosItems = [
    {
        title: 'Dashboard',
        href: '/dashboard',
        icon: LayoutDashboard,
        permission: PERMISSIONS.REPORTES_DASHBOARD // Accesible para todos los roles definidos
    },
    {
        title: 'Neumáticos',
        href: '/dashboard/neumaticos',
        icon: Disc,
        permission: PERMISSIONS.NEUMATICOS_READ
    },
    {
        title: 'Vehículos',
        href: '/dashboard/vehiculos',
        icon: Truck,
        permission: PERMISSIONS.VEHICULOS_READ
    },
    {
        title: 'Almacenes',
        href: '/dashboard/almacenes',
        icon: Warehouse,
        permission: PERMISSIONS.CATALOGOS_ALMACENES_READ
    },
    {
        title: 'Proveedores',
        href: '/dashboard/proveedores',
        icon: UserCog,
        permission: PERMISSIONS.CATALOGOS_PROVEEDORES_READ
    },
]

const operacionesItems = [
    {
        title: 'Montaje',
        href: '/dashboard/operaciones/montaje',
        icon: Wrench,
        permission: PERMISSIONS.NEUMATICOS_EVENTO_INSTALACION
    },
    {
        title: 'Rotación',
        href: '/dashboard/operaciones/rotacion',
        icon: RotateCw,
        permission: PERMISSIONS.NEUMATICOS_EVENTO_ROTACION
    },
    {
        title: 'Inspección',
        href: '/dashboard/operaciones/inspeccion',
        icon: ClipboardCheck,
        permission: PERMISSIONS.NEUMATICOS_EVENTO_INSPECCION
    },
    {
        title: 'Desecho',
        href: '/dashboard/operaciones/desecho',
        icon: Trash2,
        permission: PERMISSIONS.NEUMATICOS_EVENTO_DESECHO
    },
]

const sistemaItems = [
    {
        title: 'Alertas',
        href: '/dashboard/alertas',
        icon: Bell,
        // Las alertas suelen ser para todos, pero podemos restringir a reportes o dashboard
        permission: PERMISSIONS.REPORTES_DASHBOARD
    },
    {
        title: 'Reportes',
        href: '/dashboard/reportes',
        icon: FileText,
        permission: PERMISSIONS.REPORTES_DASHBOARD
    },
    {
        title: 'Usuarios',
        href: '/dashboard/usuarios',
        icon: Shield,
        permission: PERMISSIONS.SISTEMA_USUARIOS_READ
    },
    {
        title: 'Integraciones',
        href: '/dashboard/ajustes/integraciones',
        icon: Share2, // Icono para webhooks/conexiones
        permission: PERMISSIONS.SISTEMA_AJUSTES_READ
    },
]

export function Sidebar({ onNavigate }: { onNavigate?: () => void }) {
    const pathname = usePathname()
    const { hasPermission, isLoading } = usePermission()
    const { data: session } = useSession() // Get session for role check
    const userExtended = session?.user as { rol?: string; role?: string; roles?: string[] } | undefined;
    const isSuperAdmin = userExtended?.rol === 'SUPERADMIN' || userExtended?.role === 'SUPERADMIN' || userExtended?.roles?.includes('SUPERADMIN')

    // Si está cargando auth, mostramos esqueleto o nada
    if (isLoading) return <div className="w-64 bg-gray-100 dark:bg-gray-900 border-r" />

    const filterItems = (items: any[]) => {
        return items.filter(item => !item.permission || hasPermission(item.permission))
    }

    const filteredCatalogos = filterItems(catalogosItems)
    const filteredOperaciones = filterItems(operacionesItems)
    const filteredSistema = filterItems(sistemaItems)

    return (
        <div className="flex flex-col h-full bg-white dark:bg-gray-900 border-r">
            <div className="p-6">
                <h1 className="text-2xl font-bold text-primary">GesNeu</h1>
            </div>

            <div className="flex-1 px-4 space-y-4 overflow-y-auto">
                {/* Admin Section */}
                {isSuperAdmin && (
                    <div>
                        <div className="px-3 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                            Administración
                        </div>
                        <div className="space-y-1">
                            <Link
                                href="/dashboard/admin/tenants"
                                onClick={onNavigate}
                                className={cn(
                                    "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                                    pathname.startsWith('/dashboard/admin')
                                        ? "bg-primary text-primary-foreground"
                                        : "text-muted-foreground hover:bg-muted hover:text-foreground"
                                )}
                            >
                                <Building className="h-4 w-4" />
                                Empresas
                            </Link>
                        </div>
                    </div>
                )}

                {/* Catálogos Section */}
                {filteredCatalogos.length > 0 && (
                    <div>
                        <div className="px-3 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                            Catálogos
                        </div>
                        <div className="space-y-1">
                            {filteredCatalogos.map((item) => {
                                const Icon = item.icon
                                const isActive = pathname === item.href

                                return (
                                    <Link
                                        key={item.href}
                                        href={item.href}
                                        onClick={onNavigate}
                                        className={cn(
                                            "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                                            isActive
                                                ? "bg-primary text-primary-foreground"
                                                : "text-muted-foreground hover:bg-muted hover:text-foreground"
                                        )}
                                    >
                                        <Icon className="h-4 w-4" />
                                        {item.title}
                                    </Link>
                                )
                            })}
                        </div>
                    </div>
                )}

                {/* Operaciones Section */}
                {filteredOperaciones.length > 0 && (
                    <div>
                        <div className="px-3 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                            Operaciones
                        </div>
                        <div className="space-y-1">
                            {filteredOperaciones.map((item) => {
                                const Icon = item.icon
                                const isActive = pathname === item.href || pathname.startsWith(item.href)

                                return (
                                    <Link
                                        key={item.href}
                                        href={item.href}
                                        onClick={onNavigate}
                                        className={cn(
                                            "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                                            isActive
                                                ? "bg-primary text-primary-foreground"
                                                : "text-muted-foreground hover:bg-muted hover:text-foreground"
                                        )}
                                    >
                                        <Icon className="h-4 w-4" />
                                        {item.title}
                                    </Link>
                                )
                            })}
                        </div>
                    </div>
                )}

                {/* Sistema Section */}
                {filteredSistema.length > 0 && (
                    <div>
                        <div className="px-3 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                            Sistema
                        </div>
                        <div className="space-y-1">
                            {filteredSistema.map((item) => {
                                const Icon = item.icon
                                const isActive = pathname === item.href || pathname.startsWith(item.href)

                                return (
                                    <Link
                                        key={item.href}
                                        href={item.href}
                                        onClick={onNavigate}
                                        className={cn(
                                            "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                                            isActive
                                                ? "bg-primary text-primary-foreground"
                                                : "text-muted-foreground hover:bg-muted hover:text-foreground"
                                        )}
                                    >
                                        <Icon className="h-4 w-4" />
                                        {item.title}
                                    </Link>
                                )
                            })}
                        </div>
                    </div>
                )}

                {/* Admin/Tenants Section (SUPERADMIN ONLY) */}
                {/* We use a direct role check here or assume specific permission if we added it */}
                {/* For now, let's assume we want to show this if the user has the 'SUPERADMIN' role context */}
                {/* Note: usePermission hook might not expose role directly, so we might need useSession if strictly role based */}

                <div>
                    {/* Placeholder for dynamic role check if needed, or we rely on having the permission */}
                </div>
            </div>

            <div className="p-4 border-t">
                <Button
                    variant="ghost"
                    className="w-full justify-start gap-3 text-muted-foreground hover:text-destructive"
                    onClick={() => signOut({ callbackUrl: '/login' })}
                >
                    <LogOut className="h-4 w-4" />
                    Cerrar Sesión
                </Button>
            </div>
        </div>
    )
}
