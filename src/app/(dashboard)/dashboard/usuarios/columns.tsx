'use client'

import { ColumnDef } from '@tanstack/react-table'
import { MoreHorizontal, Shield, Edit, Trash2, Power } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Badge } from '@/components/ui/badge'
import { useState } from 'react'

// Definir tipo User para la UI
export type UsuarioColumn = {
    id: string
    nombre_completo: string
    email: string
    username: string
    rol: string
    activo: boolean
    creado_en: Date
}

export const columns = (
    onEdit: (user: UsuarioColumn) => void,
    onToggle: (id: string, current: boolean) => void,
    onDelete: (id: string) => void
): ColumnDef<UsuarioColumn>[] => [
        {
            accessorKey: 'nombre_completo',
            header: 'Nombre',
            cell: ({ row }) => (
                <div className="flex flex-col">
                    <span className="font-medium">{row.original.nombre_completo}</span>
                    <span className="text-xs text-muted-foreground">{row.original.username}</span>
                </div>
            )
        },
        {
            accessorKey: 'email',
            header: 'Email',
        },
        {
            accessorKey: 'rol',
            header: 'Rol',
            cell: ({ row }) => {
                const role = row.original.rol
                let variant: "default" | "secondary" | "destructive" | "outline" = "outline"

                if (role === 'ADMIN') variant = "destructive"
                if (role === 'GESTOR') variant = "default"
                if (role === 'OPERADOR') variant = "secondary"

                return (
                    <Badge variant={variant} className="gap-1">
                        <Shield className="h-3 w-3" />
                        {role}
                    </Badge>
                )
            }
        },
        {
            accessorKey: 'activo',
            header: 'Estado',
            cell: ({ row }) => {
                const activo = row.original.activo
                return (
                    <Badge variant={activo ? "success" : "secondary"}>
                        {activo ? 'Activo' : 'Inactivo'}
                    </Badge>
                )
            }
        },
        {
            id: 'actions',
            cell: ({ row }) => {
                const user = row.original

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
                            <DropdownMenuItem onClick={() => onEdit(user)}>
                                <Edit className="mr-2 h-4 w-4" />
                                Editar
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => onToggle(user.id, user.activo)}>
                                <Power className="mr-2 h-4 w-4" />
                                {user.activo ? 'Desactivar' : 'Activar'}
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem
                                className="text-destructive focus:text-destructive"
                                onClick={() => onDelete(user.id)}
                            >
                                <Trash2 className="mr-2 h-4 w-4" />
                                Eliminar
                            </DropdownMenuItem>
                        </DropdownMenuContent>
                    </DropdownMenu>
                )
            },
        },
    ]
