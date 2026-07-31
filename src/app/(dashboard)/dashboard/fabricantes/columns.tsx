"use client"

import { ColumnDef } from "@tanstack/react-table"
import { MoreHorizontal, Pencil, Trash, ExternalLink, Globe, Disc } from "lucide-react"
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

export function getCountryIsoCode(pais?: string | null): string | null {
    if (!pais) return null
    const clean = pais.trim().toLowerCase()

    if (clean.includes('francia') || clean.includes('france')) return 'fr'
    if (clean.includes('ee.uu') || clean.includes('usa') || clean.includes('estados unidos') || clean.includes('united states')) return 'us'
    if (clean.includes('japon') || clean.includes('japón') || clean.includes('japan')) return 'jp'
    if (clean.includes('alemania') || clean.includes('germany')) return 'de'
    if (clean.includes('italia') || clean.includes('italy')) return 'it'
    if (clean.includes('corea') || clean.includes('korea')) return 'kr'
    if (clean.includes('reino unido') || clean.includes('uk') || clean.includes('england')) return 'gb'
    if (clean.includes('china')) return 'cn'
    if (clean.includes('singapur') || clean.includes('singapore')) return 'sg'
    if (clean.includes('india')) return 'in'
    if (clean.includes('taiwan') || clean.includes('taiwán')) return 'tw'
    if (clean.includes('peru') || clean.includes('perú')) return 'pe'
    if (clean.includes('brasil') || clean.includes('brazil')) return 'br'
    if (clean.includes('mexico') || clean.includes('méxico')) return 'mx'
    if (clean.includes('espana') || clean.includes('españa') || clean.includes('spain')) return 'es'

    return null
}

export function FlagIcon({ pais, className = "h-3.5 w-5" }: { pais?: string | null; className?: string }) {
    const code = getCountryIsoCode(pais)
    if (!code) {
        return <Globe className="h-4 w-4 text-muted-foreground" />
    }
    return (
        <img
            src={`https://flagcdn.com/w40/${code}.png`}
            alt={pais || 'País'}
            className={`${className} object-cover rounded-[2px] shadow-sm border border-slate-200 dark:border-slate-700`}
            loading="lazy"
        />
    )
}

interface GetColumnsProps {
    onEdit: (fabricante: any) => void
    onDelete: (id: string, nombre: string) => void
}

export const getColumns = ({ onEdit, onDelete }: GetColumnsProps): ColumnDef<any>[] => [
    {
        accessorKey: "nombre",
        header: "Fabricante",
        cell: ({ row }) => {
            const nombre = row.getValue("nombre") as string
            return (
                <span className="font-semibold text-sm text-foreground tracking-tight py-1 block">
                    {nombre}
                </span>
            )
        }
    },
    {
        accessorKey: "codigoAbreviado",
        header: "Sigla",
        cell: ({ row }) => {
            const codigo = row.original.codigoAbreviado || row.original.codigo_abreviado
            if (!codigo) return <span className="text-xs text-muted-foreground italic">-</span>
            return (
                <Badge variant="outline" className="font-mono text-xs bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-700 font-semibold">
                    {codigo}
                </Badge>
            )
        }
    },
    {
        accessorKey: "paisOrigen",
        header: "País de Origen",
        cell: ({ row }) => {
            const pais = row.original.paisOrigen || row.original.pais_origen

            if (!pais) {
                return <span className="text-xs text-muted-foreground italic">No especificado</span>
            }

            return (
                <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full text-xs font-medium bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                    <FlagIcon pais={pais} />
                    <span>{pais}</span>
                </div>
            )
        }
    },
    {
        id: "totalModelos",
        header: "Modelos",
        cell: ({ row }) => {
            const fabricante = row.original
            const count = fabricante.totalModelos ?? fabricante._count?.modelos ?? 0
            if (count === 0) {
                return <span className="text-xs text-muted-foreground italic">0 modelos</span>
            }
            return (
                <Link href={`/dashboard/modelos?fabricanteId=${fabricante.id}`}>
                    <Badge variant="secondary" className="font-mono text-xs cursor-pointer hover:bg-primary/20 hover:text-primary transition-colors gap-1">
                        <Disc className="h-3 w-3 text-primary" />
                        {count} {count === 1 ? 'modelo' : 'modelos'}
                    </Badge>
                </Link>
            )
        }
    },
    {
        accessorKey: "sitioWeb",
        header: "Sitio Web",
        cell: ({ row }) => {
            const web = row.original.sitioWeb || row.original.sitio_web
            if (!web) return <span className="text-xs text-muted-foreground italic">-</span>
            const cleanUrl = web.replace(/^https?:\/\//, "").replace(/\/$/, "")
            return (
                <a
                    href={web.startsWith("http") ? web : `https://${web}`}
                    target="_blank"
                    rel="noreferrer"
                    className="text-xs font-medium text-slate-700 dark:text-slate-300 hover:text-primary transition-colors inline-flex items-center gap-1.5"
                >
                    <Globe className="h-3.5 w-3.5 text-muted-foreground" />
                    <span>{cleanUrl}</span>
                    <ExternalLink className="h-3 w-3 text-muted-foreground" />
                </a>
            )
        }
    },
    {
        accessorKey: "activo",
        header: "Estado",
        cell: ({ row }) => {
            const activo = row.original.activo ?? true
            if (activo) {
                return (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800">
                        <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                        Activo
                    </span>
                )
            }
            return (
                <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700">
                    <span className="h-1.5 w-1.5 rounded-full bg-slate-400" />
                    Inactivo
                </span>
            )
        }
    },
    {
        id: "actions",
        cell: ({ row }) => {
            const fabricante = row.original

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
                            <Link href={`/dashboard/modelos?fabricanteId=${fabricante.id}`}>
                                <Disc className="mr-2 h-4 w-4" /> Ver Modelos de esta Marca
                            </Link>
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem onClick={() => onEdit(fabricante)}>
                            <Pencil className="mr-2 h-4 w-4" /> Editar Fabricante
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem
                            className="text-red-600 cursor-pointer focus:text-red-600 focus:bg-red-50"
                            onClick={() => onDelete(fabricante.id, fabricante.nombre)}
                        >
                            <Trash className="mr-2 h-4 w-4" /> Eliminar
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            )
        },
    },
]
