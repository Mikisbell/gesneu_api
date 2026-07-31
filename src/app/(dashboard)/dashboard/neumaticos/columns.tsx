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
            const dot = row.original.dot || (row.original as any).dot;
            return (
                <div className="flex items-center gap-2">
                    <span className="font-mono text-xs border px-1.5 py-0.5 rounded bg-slate-50 border-slate-200">
                        {dot || 'S/DOT'}
                    </span>
                </div>
            )
        }
    },
    {
        accessorKey: "estado",
        header: "Estado",
        cell: ({ row }) => {
            const item = row.original as any;
            const estado = item.estado || item.estado_actual || 'DISPONIBLE';

            const variantMap: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
                DISPONIBLE: "outline",
                EN_STOCK: "outline",
                INSTALADO: "default",
                EN_USO: "default",
                EN_REPARACION: "secondary",
                PARA_REENCAUCHE: "secondary",
                DESECHO: "destructive",
                DESECHADO: "destructive",
            };

            const labelMap: Record<string, string> = {
                DISPONIBLE: "En Almacén",
                EN_STOCK: "En Almacén",
                INSTALADO: "En Uso (Rodando)",
                EN_USO: "En Uso (Rodando)",
                EN_REPARACION: "En Reparación",
                PARA_REENCAUCHE: "En Reencauche",
                DESECHO: "Desechado",
                DESECHADO: "Desechado"
            };

            return (
                <Badge variant={variantMap[estado] || "secondary"} className="capitalize">
                    {labelMap[estado] || estado.replace("_", " ")}
                </Badge>
            )
        },
    },
    {
        id: "ubicacion",
        header: "Ubicación Actual",
        cell: ({ row }) => {
            const item = row.original as any;
            const u = item.ubicacion;
            const estado = item.estado || item.estado_actual;

            // Vehículo asignado (Response mapeada o entidad Prisma directa)
            const vehiculoPlaca = u?.vehiculo?.placa || item.ubicacion_vehiculo?.placa || item.vehiculo?.placa;
            const vehiculoId = item.ubicacion_vehiculo_id || item.ubicacion_vehiculo?.id || u?.vehiculo?.id;
            const posicionCodigo = u?.posicion?.codigo || item.ubicacion_posicion?.codigo_posicion || item.posicion?.codigo;

            if (vehiculoPlaca) {
                return (
                    <div className="flex flex-col">
                        <span className="font-semibold text-sm flex items-center gap-1 text-slate-800">
                            🚛 Placa: {vehiculoPlaca}
                        </span>
                        <span className="text-xs text-muted-foreground">
                            Posición: {posicionCodigo || 'Instalado'}
                        </span>
                    </div>
                )
            }

            if (u?.tipo === 'VEHICULO' || estado === 'INSTALADO' || estado === 'EN_USO') {
                return (
                    <div className="flex flex-col">
                        <span className="font-medium text-xs flex items-center gap-1 text-amber-700 bg-amber-50 px-2 py-1 rounded border border-amber-200">
                            ⚠️ {vehiculoId ? `Vehículo ID: ${vehiculoId.slice(0, 8)}...` : 'En uso (Pendiente asignación)'}
                        </span>
                        <span className="text-[10px] text-muted-foreground mt-0.5">
                            {posicionCodigo ? `Posición: ${posicionCodigo}` : 'Sin posición registrada'}
                        </span>
                    </div>
                )
            }

            // Almacén asignado
            const almacenNombre = u?.almacen?.nombre || item.ubicacion_almacen?.nombre || item.almacen?.nombre;
            if (almacenNombre || u?.tipo === 'ALMACEN' || estado === 'EN_STOCK' || estado === 'DISPONIBLE') {
                return (
                    <div className="flex flex-col">
                        <span className="font-medium text-sm flex items-center gap-1">
                            🏭 {almacenNombre || 'Almacén Principal'}
                        </span>
                        <span className="text-xs text-muted-foreground">En Stock</span>
                    </div>
                )
            }

            // Desecho
            const motivoDesecho = item.motivo_desecho?.nombre || item.motivo_desecho_id;
            if (u?.tipo === 'DESECHO' || estado === 'DESECHO' || estado === 'DESECHADO') {
                return (
                    <div className="flex flex-col">
                        <span className="font-medium text-sm flex items-center gap-1 text-red-600">
                            🗑️ Desechado
                        </span>
                        {motivoDesecho && (
                            <span className="text-xs text-muted-foreground">{motivoDesecho}</span>
                        )}
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
