"use client"

import { ColumnDef } from "@tanstack/react-table"
import { CertificadoListado } from "@/lib/api/certificados"
import { format } from "date-fns"
import { es } from "date-fns/locale"
import { Badge } from "@/components/ui/badge"
import { EstadoOperatividadEnum } from "@prisma/client"
import { Button } from "@/components/ui/button"
import { FileText } from "lucide-react"

export const columns: ColumnDef<CertificadoListado>[] = [
    {
        accessorKey: "folio_numero",
        header: "Folio",
        cell: ({ row }) => {
            const folio = row.getValue("folio_numero") as number
            return <div className="font-medium">#{folio.toString().padStart(6, '0')}</div>
        }
    },
    {
        accessorKey: "fecha_emision",
        header: "Fecha de Emisión",
        cell: ({ row }) => {
            const date = new Date(row.getValue("fecha_emision"))
            return format(date, "dd/MM/yyyy HH:mm", { locale: es })
        }
    },
    {
        accessorKey: "vehiculo.placa",
        header: "Placa",
    },
    {
        accessorKey: "estado_operatividad",
        header: "Estado",
        cell: ({ row }) => {
            const estado = row.getValue("estado_operatividad") as EstadoOperatividadEnum
            
            const variantMap: Record<EstadoOperatividadEnum, "default" | "secondary" | "destructive"> = {
                APTO: "default",
                CONDICIONAL: "secondary",
                NO_APTO: "destructive"
            }
            
            const textMap: Record<EstadoOperatividadEnum, string> = {
                APTO: "Apto",
                CONDICIONAL: "Condicional",
                NO_APTO: "No Apto"
            }
            
            return (
                <Badge variant={variantMap[estado]}>
                    {textMap[estado]}
                </Badge>
            )
        }
    },
    {
        accessorKey: "emisor.nombre_completo",
        header: "Emitido Por",
    },
    {
        id: "actions",
        cell: ({ row }) => {
            const certificado = row.original

            return (
                <Button 
                    variant="ghost" 
                    size="sm"
                    className="flex items-center"
                    onClick={() => {
                        // TODO: Implement view certificate details / PDF download
                        console.log("View certificate", certificado.id)
                    }}
                >
                    <FileText className="h-4 w-4 mr-2" />
                    Detalle
                </Button>
            )
        },
    },
]
