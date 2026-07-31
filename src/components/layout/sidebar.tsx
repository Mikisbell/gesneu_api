'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import {
    LayoutDashboard,
    Truck,
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
    Building,
    ChevronDown,
    ChevronRight,
    Package
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { signOut, useSession } from 'next-auth/react'
import { PERMISSIONS } from '@/lib/auth/permissions'
import { usePermission } from '@/hooks/use-permission'
import { MULTI_TENANT_ENABLED } from '@/lib/features'

interface NavSubItem {
    title: string
    href: string
    permission?: string
}

interface NavItemData {
    title: string
    href: string
    icon: any
    permission?: string
    children?: NavSubItem[]
}

const catalogosItems: NavItemData[] = [
    {
        title: 'Dashboard',
        href: '/dashboard',
        icon: LayoutDashboard,
        permission: PERMISSIONS.REPORTES_DASHBOARD
    },
    {
        title: 'Neumáticos',
        href: '/dashboard/neumaticos',
        icon: Disc,
        permission: PERMISSIONS.NEUMATICOS_READ,
        children: [
            {
                title: 'Inventario',
                href: '/dashboard/neumaticos',
                permission: PERMISSIONS.NEUMATICOS_READ
            },
            {
                title: 'Modelos de Neumático',
                href: '/dashboard/modelos',
                permission: PERMISSIONS.NEUMATICOS_READ
            },
            {
                title: 'Fabricantes',
                href: '/dashboard/fabricantes',
                permission: PERMISSIONS.NEUMATICOS_READ
            }
        ]
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

const operacionesItems: NavItemData[] = [
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

const sistemaItems: NavItemData[] = [
    {
        title: 'Alertas',
        href: '/dashboard/alertas',
        icon: Bell,
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
        icon: Share2,
        permission: PERMISSIONS.SISTEMA_AJUSTES_READ
    },
]

function SidebarNavItem({ item, onNavigate }: { item: NavItemData; onNavigate?: () => void }) {
    const pathname = usePathname()
    const { hasPermission } = usePermission()
    const Icon = item.icon

    const hasChildren = item.children && item.children.length > 0
    const isChildActive = hasChildren && item.children?.some(child => pathname === child.href)
    const isParentActive = pathname === item.href || isChildActive

    const [isOpen, setIsOpen] = useState(isParentActive)

    if (hasChildren) {
        const filteredChildren = item.children?.filter(child => !child.permission || hasPermission(child.permission as any)) || []

        return (
            <div>
                <button
                    type="button"
                    onClick={() => setIsOpen(!isOpen)}
                    className={cn(
                        "w-full flex items-center justify-between px-3 py-2 rounded-md text-sm font-medium transition-colors",
                        isParentActive
                            ? "bg-slate-100 dark:bg-slate-800 text-foreground font-semibold"
                            : "text-muted-foreground hover:bg-muted hover:text-foreground"
                    )}
                >
                    <div className="flex items-center gap-3">
                        <Icon className="h-4 w-4" />
                        <span>{item.title}</span>
                    </div>
                    {isOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                </button>

                {isOpen && (
                    <div className="ml-4 pl-3 border-l border-slate-200 dark:border-slate-800 my-1 space-y-1">
                        {filteredChildren.map(child => {
                            const isSubActive = pathname === child.href

                            return (
                                <Link
                                    key={child.href}
                                    href={child.href}
                                    onClick={onNavigate}
                                    className={cn(
                                        "block px-3 py-1.5 rounded-md text-xs font-medium transition-colors",
                                        isSubActive
                                            ? "bg-primary text-primary-foreground font-bold"
                                            : "text-muted-foreground hover:bg-muted hover:text-foreground"
                                    )}
                                >
                                    {child.title}
                                </Link>
                            )
                        })}
                    </div>
                )}
            </div>
        )
    }

    return (
        <Link
            href={item.href}
            onClick={onNavigate}
            className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                pathname === item.href
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
            )}
        >
            <Icon className="h-4 w-4" />
            {item.title}
        </Link>
    )
}

export function Sidebar({ onNavigate }: { onNavigate?: () => void }) {
    const pathname = usePathname()
    const { hasPermission, isLoading } = usePermission()
    const { data: session } = useSession()
    const userExtended = session?.user as { rol?: string; role?: string; roles?: string[] } | undefined;
    const isSuperAdmin = userExtended?.rol === 'SUPERADMIN' || userExtended?.role === 'SUPERADMIN' || userExtended?.roles?.includes('SUPERADMIN')

    if (isLoading) return <div className="w-64 bg-gray-100 dark:bg-gray-900 border-r" />

    const filterItems = (items: NavItemData[]) => {
        return items.filter(item => !item.permission || hasPermission(item.permission as any))
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
                {isSuperAdmin && MULTI_TENANT_ENABLED && (
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
                            {filteredCatalogos.map((item) => (
                                <SidebarNavItem key={item.title} item={item} onNavigate={onNavigate} />
                            ))}
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
                            {filteredOperaciones.map((item) => (
                                <SidebarNavItem key={item.title} item={item} onNavigate={onNavigate} />
                            ))}
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
                            {filteredSistema.map((item) => (
                                <SidebarNavItem key={item.title} item={item} onNavigate={onNavigate} />
                            ))}
                        </div>
                    </div>
                )}
            </div>

            <div className="p-4 border-t">
                <Button
                    variant="ghost"
                    data-testid="logout-button"
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
