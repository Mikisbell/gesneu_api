
"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import {
    Shield, Building2, Users, FileText, Webhook,
    BarChart3, Settings, ChevronLeft
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

const adminNavItems = [
    {
        title: "Centro de Comando",
        href: "/dashboard/admin",
        icon: Shield,
        exact: true
    },
    {
        title: "Empresas",
        href: "/dashboard/admin/tenants",
        icon: Building2
    },
    {
        title: "Usuarios",
        href: "/dashboard/admin/users",
        icon: Users
    },
    {
        title: "Audit Trail",
        href: "/dashboard/admin/audit",
        icon: FileText
    },
    {
        title: "Webhooks",
        href: "/dashboard/admin/webhooks",
        icon: Webhook
    }
]

export default function AdminLayout({
    children,
}: {
    children: React.ReactNode
}) {
    const pathname = usePathname()

    const isActive = (item: typeof adminNavItems[0]) => {
        if (item.exact) {
            return pathname === item.href
        }
        return pathname.startsWith(item.href)
    }

    return (
        <div className="flex min-h-screen">
            {/* Sidebar Navigation */}
            <aside className="hidden lg:flex lg:flex-col w-64 border-r bg-muted/30">
                <div className="p-4 border-b">
                    <Link href="/dashboard">
                        <Button variant="ghost" size="sm" className="w-full justify-start">
                            <ChevronLeft className="h-4 w-4 mr-2" />
                            Volver al Dashboard
                        </Button>
                    </Link>
                </div>
                <nav className="flex-1 p-4 space-y-1">
                    {adminNavItems.map((item) => {
                        const Icon = item.icon
                        const active = isActive(item)
                        return (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={cn(
                                    "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                                    active
                                        ? "bg-primary text-primary-foreground"
                                        : "text-muted-foreground hover:bg-muted hover:text-foreground"
                                )}
                            >
                                <Icon className="h-4 w-4" />
                                {item.title}
                            </Link>
                        )
                    })}
                </nav>
                <div className="p-4 border-t">
                    <div className="text-xs text-muted-foreground text-center">
                        Panel de Administración
                    </div>
                </div>
            </aside>

            {/* Mobile Header */}
            <div className="lg:hidden fixed top-0 left-0 right-0 z-50 bg-background border-b p-2">
                <div className="flex items-center gap-2 overflow-x-auto">
                    <Link href="/dashboard">
                        <Button variant="ghost" size="sm">
                            <ChevronLeft className="h-4 w-4" />
                        </Button>
                    </Link>
                    {adminNavItems.map((item) => {
                        const Icon = item.icon
                        const active = isActive(item)
                        return (
                            <Link key={item.href} href={item.href}>
                                <Button
                                    variant={active ? "default" : "ghost"}
                                    size="sm"
                                    className="whitespace-nowrap"
                                >
                                    <Icon className="h-4 w-4 mr-1.5" />
                                    {item.title}
                                </Button>
                            </Link>
                        )
                    })}
                </div>
            </div>

            {/* Main Content */}
            <main className="flex-1 lg:pt-0 pt-14">
                {children}
            </main>
        </div>
    )
}
