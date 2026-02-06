"use client"

import { ColumnDef } from "@tanstack/react-table"
import { NeumaticoResponse } from "@/lib/api/neumaticos"
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
    onDelete: (id: string, numeroSerie: string) => void
}

export const getColumns = ({ onEdit, onDelete }: GetColumnsProps): ColumnDef<NeumaticoResponse>[] => [
    {
        accessorKey: "numeroSerie",
        header: "Serie / ID",
        cell: ({ row }) => (
            <div className="flex flex-col">
                <span className="font-mono font-bold text-gray-900 dark:text-gray-100">
                    {row.original.numeroSerie || 'S/N'}
                </span>
                <span className="text-[10px] text-muted-foreground">ID: {row.original.id.slice(0, 8)}...</span>
            </div>
        ),
    },
    {
        accessorKey: "modelo.nombre",
        header: "Marca y Modelo",
        cell: ({ row }) => {
            const m = row.original.modelo;
            return (
                <div className="flex flex-col">
                    <span className="font-semibold text-sm">
                        {m?.fabricante?.nombre} {m?.nombre}
                    </span>
                    <Badge variant="outline" className="w-fit mt-1 text-[10px] font-normal">
                        {m?.medida}
                    </Badge>
                </div>
            )
        }
    },
    {
        accessorKey: "dot",
        header: "DOT / Antigüedad",
        cell: ({ row }) => {
            const dot = row.original.dot;
            return (
                <div className="flex items-center gap-2">
                    <span className="font-mono text-sm border px-1 rounded bg-muted">{dot || '----'}</span>
                </div>
            )
        }
    },
    {
        accessorKey: "estado",
        header: "Estado",
        cell: ({ row }) => {
            const estado = row.original.estado;

            const variantMap: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
                DISPONIBLE: "outline", // Greenish usually better, but shadcn default outline is clean
                INSTALADO: "default", // Black/Primary
                EN_REPARACION: "secondary", // Gray/Orange
                PARA_REENCAUCHE: "secondary",
                DESECHO: "destructive", // Red
            };

            const labelMap: Record<string, string> = {
                DISPONIBLE: "En Almacén",
                INSTALADO: "Rodando",
                EN_REPARACION: "Reparación",
                PARA_REENCAUCHE: "Reencauche",
                DESECHO: "Baja/Scrap"
            };

            return (
                <Badge variant={variantMap[estado] || "secondary"} className="capitalize">
                    {labelMap[estado] || estado?.replace("_", " ")}
                </Badge>
            )
        },
    },
    {
        id: "ubicacion",
        header: "Ubicación Actual",
        cell: ({ row }) => {
            const u = row.original.ubicacion;
            if (u.tipo === 'VEHICULO' && u.vehiculo) {
                return (
                    <div className="flex flex-col">
                        <span className="font-medium text-sm flex items-center gap-1">
                            🚛 {u.vehiculo.placa}
                        </span>
                        <span className="text-xs text-muted-foreground">
                            Pos: {u.posicion?.codigo || 'Indefinida'}
                        </span>
                    </div>
                )
            }
            if (u.tipo === 'ALMACEN' && u.almacen) {
                return (
                    <div className="flex flex-col">
                        <span className="font-medium text-sm flex items-center gap-1">
                            🏭 {u.almacen.nombre}
                        </span>
                        <span className="text-xs text-muted-foreground">Stock</span>
                    </div>
                )
            }
            return <span className="text-sm text-muted-foreground italic">Sin ubicación registrada</span>
        },
    },
    {
        id: "mediciones",
        header: "Condición",
        cell: ({ row }) => {
            const m = row.original.mediciones;
            return (
                <div className="flex flex-col gap-1 text-xs">
                    <div className="flex justify-between w-24">
                        <span className="text-muted-foreground">Prof:</span>
                        <span className="font-semibold">{m.profundidadActual} mm</span>
                    </div>
                </div>
            )
        }
    },
    {
        id: "actions",
        cell: ({ row }) => {
            const neumatico = row.original

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
                        <DropdownMenuItem
                            onClick={() => navigator.clipboard.writeText(neumatico.numeroSerie || '')}
                        >
                            Copiar Serie
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem onClick={() => window.location.href = `/dashboard/neumaticos/${neumatico.id}`}>
                            <Eye className="mr-2 h-4 w-4" /> Ver Historial
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => onEdit(neumatico)}>
                            <Pencil className="mr-2 h-4 w-4" /> Editar Ficha
                        </DropdownMenuItem>
                        <DropdownMenuItem
                            className="text-red-600 cursor-pointer focus:text-red-600 focus:bg-red-50"
                            onClick={() => onDelete(neumatico.id, neumatico.numeroSerie || '')}
                        >
                            <Trash className="mr-2 h-4 w-4" /> Dar de Baja
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            )
        },
    },
]
