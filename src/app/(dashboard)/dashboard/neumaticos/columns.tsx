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

export const columns: ColumnDef<NeumaticoWithRelations>[] = [
    {
        accessorKey: "numero_serie",
        header: "Serie",
        cell: ({ row }) => <span className="font-medium">{row.getValue("numero_serie")}</span>,
    },
    {
        accessorKey: "modelo.nombre",
        header: "Modelo",
    },
    {
        accessorKey: "dot",
        header: "DOT",
    },
    {
        accessorKey: "estado_actual",
        header: "Estado",
        cell: ({ row }) => {
            const estado = row.getValue("estado_actual") as string
            return (
                <Badge variant={estado === "EN_USO" ? "default" : "secondary"}>
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
                return <span>{neumatico.ubicacion_vehiculo.placa}</span>
            }
            if (neumatico.ubicacion_almacen) {
                return <span>{neumatico.ubicacion_almacen.nombre}</span>
            }
            return <span className="text-muted-foreground">-</span>
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
                        <DropdownMenuItem>
                            <Eye className="mr-2 h-4 w-4" /> Ver Historial
                        </DropdownMenuItem>
                        <DropdownMenuItem>
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
