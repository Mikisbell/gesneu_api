"use client"

import { ColumnDef } from "@tanstack/react-table"
import { Proveedor } from "@prisma/client"
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

export const columns: ColumnDef<Proveedor>[] = [
    {
        accessorKey: "nombre",
        header: "Nombre",
    },
    {
        accessorKey: "ruc",
        header: "RUC",
    },
    {
        accessorKey: "email",
        header: "Email",
    },
    {
        accessorKey: "telefono",
        header: "Teléfono",
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
            const proveedor = row.original

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
                            onClick={() => navigator.clipboard.writeText(proveedor.id)}
                        >
                            Copiar ID
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
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
