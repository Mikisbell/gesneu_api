"use client"

import { ColumnDef } from "@tanstack/react-table"
import { MoreHorizontal, Pencil, Trash, Disc } from "lucide-react"
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
    onEdit: (modelo: any) => void
    onDelete: (id: string, nombre: string) => void
}

export const getColumns = ({ onEdit, onDelete }: GetColumnsProps): ColumnDef<any>[] => [
    {
        accessorKey: "fabricante.nombre",
        header: "Fabricante",
        cell: ({ row }) => {
            const m = row.original
            const nombreFab = m.fabricante?.nombre || m.fabricante_nombre || "Sin Fabricante"
            return (
                <span className="font-semibold text-sm text-foreground">
                    {nombreFab}
                </span>
            )
        }
    },
    {
        id: "nombre",
        accessorFn: (row) => row.nombre || row.nombre_modelo || "",
        header: "Modelo",
        cell: ({ row }) => {
            const m = row.original
            const nombreModelo = m.nombre || m.nombre_modelo || "-"
            const patron = m.patron_dibujo || m.patronDibujo || m.tipo_servicio
            return (
                <div className="flex flex-col">
                    <span className="font-semibold text-sm text-primary">{nombreModelo}</span>
                    {patron && (
                        <span className="text-[11px] text-muted-foreground uppercase font-mono">
                            {patron}
                        </span>
                    )}
                </div>
            )
        }
    },
    {
        accessorKey: "medida",
        header: "Medida",
        cell: ({ row }) => {
            const m = row.original
            return (
                <Badge variant="outline" className="font-mono text-xs bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-700">
                    {m.medida}
                </Badge>
            )
        }
    },
    {
        id: "profundidadOriginal",
        header: "Prof. Original",
        cell: ({ row }) => {
            const m = row.original
            const val = m.profundidadOriginal ?? m.profundidad_original_mm
            if (val === undefined || val === null) return <span className="text-xs text-muted-foreground italic">-</span>
            return <span className="font-medium text-xs">{val} mm</span>
        }
    },
    {
        id: "presionRecomendada",
        header: "PSI Rec.",
        cell: ({ row }) => {
            const m = row.original
            const val = m.presionRecomendada ?? m.presion_recomendada_psi
            if (val === undefined || val === null) return <span className="text-xs text-muted-foreground italic">-</span>
            return <span className="font-medium text-xs">{val} PSI</span>
        }
    },
    {
        id: "reencauches",
        header: "Reencauches",
        cell: ({ row }) => {
            const m = row.original
            const permite = m.reencauche?.permitido ?? m.permite_reencauche ?? false
            const max = m.reencauche?.maximos ?? m.reencauches_maximos ?? 0
            if (permite) {
                return (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800">
                        Sí (Máx {max})
                    </span>
                )
            }
            return (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700">
                    No permite
                </span>
            )
        }
    },
    {
        id: "actions",
        cell: ({ row }) => {
            const modelo = row.original
            const nombreDisplay = `${modelo.fabricante?.nombre || ''} ${modelo.nombre || modelo.nombre_modelo || ''}`

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
                        <DropdownMenuItem onClick={() => onEdit(modelo)}>
                            <Pencil className="mr-2 h-4 w-4" /> Editar Modelo
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem
                            className="text-red-600 cursor-pointer focus:text-red-600 focus:bg-red-50"
                            onClick={() => onDelete(modelo.id, nombreDisplay)}
                        >
                            <Trash className="mr-2 h-4 w-4" /> Eliminar
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            )
        },
    },
]
