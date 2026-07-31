"use client"

import { ColumnDef } from "@tanstack/react-table"
import { MoreHorizontal, Pencil, Trash, Warehouse, Disc } from "lucide-react"
import Link from "next/link"
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

interface GetColumnsProps {
    onEdit: (almacen: any) => void
    onDelete: (id: string) => void
}

export const getColumns = ({ onEdit, onDelete }: GetColumnsProps): ColumnDef<any>[] => [
    {
        accessorKey: "codigo",
        header: "Código",
        cell: ({ row }) => (
            <Badge variant="outline" className="font-mono text-xs bg-slate-50 dark:bg-slate-800">
                {row.getValue("codigo")}
            </Badge>
        )
    },
    {
        accessorKey: "nombre",
        header: "Nombre del Almacén",
        cell: ({ row }) => (
            <div className="flex items-center gap-2">
                <Warehouse className="h-4 w-4 text-primary" />
                <span className="font-semibold text-sm">{row.getValue("nombre")}</span>
            </div>
        )
    },
    {
        accessorKey: "direccion",
        header: "Ubicación / Dirección",
        cell: ({ row }) => (
            <span className="text-xs text-muted-foreground">
                {row.getValue("direccion") || 'Sin dirección registrada'}
            </span>
        )
    },
    {
        id: "totalNeumaticos",
        header: "Neumáticos en Stock",
        cell: ({ row }) => {
            const almacen = row.original
            const count = almacen.totalNeumaticos ?? almacen._count?.neumaticos ?? 0
            if (count === 0) {
                return <span className="text-xs text-muted-foreground italic">0 neumáticos</span>
            }
            return (
                <Link href={`/dashboard/neumaticos`}>
                    <Badge variant="secondary" className="font-mono text-xs cursor-pointer hover:bg-primary/20 hover:text-primary transition-colors gap-1">
                        <Disc className="h-3 w-3 text-primary" />
                        {count} {count === 1 ? 'neumático' : 'neumáticos'}
                    </Badge>
                </Link>
            )
        }
    },
    {
        accessorKey: "activo",
        header: "Estado",
        cell: ({ row }) => {
            const activo = row.getValue("activo")
            return (
                <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    activo 
                        ? "bg-emerald-50 text-emerald-700 border border-emerald-200" 
                        : "bg-slate-100 text-slate-600 border border-slate-200"
                }`}>
                    <span className={`h-1.5 w-1.5 rounded-full ${activo ? "bg-emerald-500" : "bg-slate-400"}`} />
                    {activo ? "Activo" : "Inactivo"}
                </span>
            )
        },
    },
    {
        id: "actions",
        cell: ({ row }) => {
            const almacen = row.original

            return (
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <Button variant="ghost" className="h-8 w-8 p-0 hover:bg-muted">
                            <span className="sr-only">Abrir menú</span>
                            <MoreHorizontal className="h-4 w-4" />
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                        <DropdownMenuLabel>Acciones</DropdownMenuLabel>
                        <DropdownMenuItem asChild>
                            <Link href={`/dashboard/neumaticos`}>
                                <Disc className="mr-2 h-4 w-4" /> Ver Stock en este Almacén
                            </Link>
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem onClick={() => onEdit(almacen)}>
                            <Pencil className="mr-2 h-4 w-4" /> Editar Almacén
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem
                            className="text-red-600 cursor-pointer focus:text-red-600 focus:bg-red-50"
                            onClick={() => onDelete(almacen.id)}
                        >
                            <Trash className="mr-2 h-4 w-4" /> Eliminar
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            )
        },
    },
]
