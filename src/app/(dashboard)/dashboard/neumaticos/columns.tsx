"use client"

import { ColumnDef } from "@tanstack/react-table"
import { Action, NeumaticoResponse } from "@/types/domain/neumatico.types"
// import { NeumaticoWithRelations } from "@/lib/api/neumaticos"
import { MoreHorizontal, Pencil, Trash, Eye } from "lucide-react"
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
    onEdit: (neumatico: NeumaticoResponse) => void
    onDelete: (id: string) => void
}

console.log("COLUMNS DEFINITION RELOADED - V2");
export const getColumns = ({ onEdit, onDelete }: GetColumnsProps): ColumnDef<NeumaticoResponse>[] => [
    {
        accessorKey: "identificacion.serie",
        id: "serie",
        header: "Serie",
        cell: ({ row }) => <span className="font-medium">{row.original.identificacion.serie || 'S/N'}</span>,
    },
    {
        accessorKey: "identificacion.modelo",
        header: "Modelo",
        cell: ({ row }) => (
            <div className="flex flex-col">
                <span className="font-medium">{row.original.identificacion.modelo}</span>
                <span className="text-xs text-muted-foreground">{row.original.identificacion.medida}</span>
            </div>
        )
    },
    {
        accessorKey: "identificacion.dot",
        header: "DOT",
        cell: ({ row }) => <span>{row.original.identificacion.dot || '-'}</span>,
    },
    {
        accessorKey: "estado.estadoActual",
        header: "Estado",
        cell: ({ row }) => {
            const estado = row.original.estado.estadoActual
            if (!estado) return <Badge variant="secondary">UNKNOWN</Badge>

            return (
                <Badge variant={estado === "MONTADO" ? "default" : "secondary"}>
                    {estado.replace("_", " ")}
                </Badge>
            )
        },
    },
    {
        accessorKey: "estado.ubicacion",
        header: "Ubicación",
        cell: ({ row }) => {
            return <span className="text-sm truncate max-w-[200px]" title={row.original.estado.ubicacion}>
                {row.original.estado.ubicacion}
            </span>
        },
    },
    {
        id: "actions",
        cell: ({ row }) => {
            const neumatico = row.original

            return (
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <Button variant="ghost" className="h-8 w-8 p-0">
                            <span className="sr-only">Abrir menú</span>
                            <MoreHorizontal className="h-4 w-4" />
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                        <DropdownMenuLabel>Acciones</DropdownMenuLabel>
                        <DropdownMenuItem
                            onClick={() => navigator.clipboard.writeText(neumatico.id)}
                        >
                            Copiar ID
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem onClick={() => window.location.href = `/dashboard/neumaticos/${neumatico.id}`}>
                            <Eye className="mr-2 h-4 w-4" /> Ver Historial
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => onEdit(neumatico)}>
                            <Pencil className="mr-2 h-4 w-4" /> Editar
                        </DropdownMenuItem>
                        <DropdownMenuItem
                            className="text-red-600 cursor-pointer"
                            onClick={() => onDelete(neumatico.id)}
                        >
                            <Trash className="mr-2 h-4 w-4" /> Eliminar
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            )
        },
    },
]
