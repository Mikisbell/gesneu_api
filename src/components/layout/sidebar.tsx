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
    Disc
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { signOut } from 'next-auth/react'

const sidebarItems = [
    {
        title: 'Dashboard',
        href: '/dashboard',
        icon: LayoutDashboard,
    },
    {
        title: 'Neumáticos',
        href: '/dashboard/neumaticos',
        icon: Disc,
    },
    {
        title: 'Vehículos',
        href: '/dashboard/vehiculos',
        icon: Truck,
    },
    {
        title: 'Inventario',
        href: '/dashboard/inventario',
        icon: Package,
    },
    {
        title: 'Usuarios',
        href: '/dashboard/usuarios',
        icon: Users,
    },
    {
        title: 'Configuración',
        href: '/dashboard/configuracion',
        icon: Settings,
    },
]

export function Sidebar() {
    const pathname = usePathname()

    return (
        <div className="flex flex-col h-full bg-white dark:bg-gray-900 border-r">
            <div className="p-6">
                <h1 className="text-2xl font-bold text-primary">GesNeu</h1>
            </div>

            <div className="flex-1 px-4 space-y-2">
                {sidebarItems.map((item) => {
                    const Icon = item.icon
                    const isActive = pathname === item.href

                    return (
                        <Link
                            key={item.href}
                            href={item.href}
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
