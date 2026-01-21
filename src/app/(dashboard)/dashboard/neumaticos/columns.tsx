"use client"

import { ColumnDef } from "@tanstack/react-table"
import { NeumaticoWithRelations } from "@/lib/api/neumaticos"
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
    onEdit: (neumatico: NeumaticoWithRelations) => void
    onDelete: (id: string) => void
}

export const getColumns = ({ onEdit, onDelete }: GetColumnsProps): ColumnDef<NeumaticoWithRelations>[] => [
    {
        accessorKey: "numero_serie",
        id: "serie",
        header: "Serie",
        cell: ({ row }) => <span className="font-medium">{row.original.numero_serie || 'S/N'}</span>,
    },
    {
        accessorKey: "modelo.nombre",
        header: "Modelo",
        cell: ({ row }) => (
            <div className="flex flex-col">
                <span className="font-medium">{row.original.modelo?.nombre_modelo || '-'}</span>
                <span className="text-xs text-muted-foreground">{row.original.modelo?.medida || '-'}</span>
            </div>
        )
    },
    {
        accessorKey: "dot",
        header: "DOT",
        cell: ({ row }) => <span>{row.original.dot || '-'}</span>,
    },
    {
        accessorKey: "estado_actual",
        header: "Estado",
        cell: ({ row }) => {
            const estado = row.original.estado_actual
            if (!estado) return <Badge variant="secondary">UNKNOWN</Badge>

            return (
                <Badge variant={estado === "INSTALADO" ? "default" : "secondary"}>
                    {estado.replace("_", " ")}
                </Badge>
            )
        },
    },
    {
        id: "ubicacion",
        header: "Ubicación",
        cell: ({ row }) => {
            const neumatico = row.original
            if (neumatico.ubicacion_vehiculo) {
                return <span className="text-sm">Vehículo: {neumatico.ubicacion_vehiculo.placa}</span>
            }
            if (neumatico.ubicacion_almacen) {
                return <span className="text-sm">Almacén: {neumatico.ubicacion_almacen.nombre}</span>
            }
            return <span className="text-sm text-muted-foreground">Sin ubicación</span>
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
