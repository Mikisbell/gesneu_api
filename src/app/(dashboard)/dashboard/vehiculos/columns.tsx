"use client"

import { ColumnDef } from "@tanstack/react-table"
import { VehiculoWithRelations } from "@/lib/api/vehiculos"
import { MoreHorizontal, Pencil, Trash } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

interface GetColumnsProps {
    onEdit: (vehiculo: VehiculoWithRelations) => void
}

export const getColumns = ({ onEdit }: GetColumnsProps): ColumnDef<VehiculoWithRelations>[] => [
    {
        accessorKey: "placa",
        header: "Placa",
    },
    {
        accessorKey: "tipo_vehiculo.nombre",
        header: "Tipo",
    },
    {
        accessorKey: "marca",
        header: "Marca",
    },
    {
        accessorKey: "modelo",
        header: "Modelo",
    },
    {
        accessorKey: "kilometraje_actual",
        header: "Kilometraje",
        cell: ({ row }) => {
            const km = row.getValue("kilometraje_actual") as number
            return km ? `${km.toLocaleString()} km` : "-"
        }
    },
    {
        accessorKey: "activo",
        header: "Estado",
        cell: ({ row }) => (
            <div className={row.getValue("activo") ? "text-green-600" : "text-red-600"}>
                {row.getValue("activo") ? "Activo" : "Inactivo"}
            </div>
        ),
    },
    {
        id: "actions",
        cell: ({ row }) => {
            const vehiculo = row.original

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
                            onClick={() => navigator.clipboard.writeText(vehiculo.id)}
                        >
                            Copiar ID
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem onClick={() => onEdit(vehiculo)}>
                            <Pencil className="mr-2 h-4 w-4" /> Editar
                        </DropdownMenuItem>
                        <DropdownMenuItem className="text-red-600">
                            <Trash className="mr-2 h-4 w-4" /> Eliminar
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            )
        },
    },
]
