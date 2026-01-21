
"use client"

import { ColumnDef } from "@tanstack/react-table"
import { MoreHorizontal, Users, Truck, CircleDot, Eye, Settings, Power } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Badge } from "@/components/ui/badge"

// This type defines the shape of tenant data
export type Tenant = {
    id: string
    nombre: string
    ruc: string
    direccion: string | null
    activo: boolean
    creado_en: Date
    _count?: {
        usuarios: number
        vehiculos: number
        neumaticos: number
    }
}

export const columns: ColumnDef<Tenant>[] = [
    {
        accessorKey: "nombre",
        header: "Empresa",
        cell: ({ row }) => {
            return (
                <div className="flex flex-col min-w-[180px]">
                    <span className="font-medium">{row.getValue("nombre")}</span>
                    <span className="text-xs text-muted-foreground truncate max-w-[200px]">
                        {row.original.direccion || 'Sin dirección'}
                    </span>
                </div>
            )
        }
    },
    {
        accessorKey: "ruc",
        header: "RUC / NIT",
        cell: ({ row }) => (
            <code className="bg-muted px-2 py-1 rounded text-sm font-mono">
                {row.getValue("ruc")}
            </code>
        )
    },
    {
        id: "recursos",
        header: "Recursos",
        cell: ({ row }) => {
            const usuarios = row.original._count?.usuarios || 0
            const vehiculos = row.original._count?.vehiculos || 0
            const neumaticos = row.original._count?.neumaticos || 0

            return (
                <div className="flex items-center gap-3 text-sm">
                    <div className="flex items-center gap-1" title="Usuarios">
                        <Users className="h-3.5 w-3.5 text-blue-500" />
                        <span className="font-medium">{usuarios}</span>
                    </div>
                    <div className="flex items-center gap-1" title="Vehículos">
                        <Truck className="h-3.5 w-3.5 text-orange-500" />
                        <span className="font-medium">{vehiculos}</span>
                    </div>
                    <div className="flex items-center gap-1" title="Neumáticos">
                        <CircleDot className="h-3.5 w-3.5 text-violet-500" />
                        <span className="font-medium">{neumaticos}</span>
                    </div>
                </div>
            )
        }
    },
    {
        accessorKey: "activo",
        header: "Estado",
        cell: ({ row }) => {
            const activo = row.getValue("activo")
            return (
                <Badge
                    variant={activo ? "default" : "destructive"}
                    className={activo ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400" : ""}
                >
                    {activo ? "Activo" : "Suspendido"}
                </Badge>
            )
        },
    },
    {
        accessorKey: "creado_en",
        header: "Registro",
        cell: ({ row }) => {
            const date = new Date(row.original.creado_en)
            return (
                <div className="text-sm text-muted-foreground">
                    {date.toLocaleDateString('es-PE', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric'
                    })}
                </div>
            )
        }
    },
    {
        id: "actions",
        cell: ({ row }) => {
            const tenant = row.original

            return (
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <Button variant="ghost" className="h-8 w-8 p-0">
                            <span className="sr-only">Abrir menú</span>
                            <MoreHorizontal className="h-4 w-4" />
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="w-48">
                        <DropdownMenuLabel>Acciones</DropdownMenuLabel>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem
                            onClick={() => navigator.clipboard.writeText(tenant.id)}
                        >
                            <Eye className="h-4 w-4 mr-2" />
                            Ver Detalles
                        </DropdownMenuItem>
                        <DropdownMenuItem>
                            <Users className="h-4 w-4 mr-2" />
                            Gestionar Usuarios
                        </DropdownMenuItem>
                        <DropdownMenuItem>
                            <Settings className="h-4 w-4 mr-2" />
                            Configuración
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem
                            className={tenant.activo ? "text-amber-600" : "text-emerald-600"}
                        >
                            <Power className="h-4 w-4 mr-2" />
                            {tenant.activo ? "Suspender" : "Reactivar"}
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            )
        },
    },
]
