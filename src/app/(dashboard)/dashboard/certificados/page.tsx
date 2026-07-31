"use client"

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { certificadosApi } from '@/lib/api/certificados'
import { DataTable } from '@/components/ui/data-table'
import { columns } from './columns'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Loader2 } from 'lucide-react'
import { EstadoOperatividadEnum } from '@prisma/client'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { Input } from "@/components/ui/input"

export default function CertificadosPage() {
    const [page, setPage] = useState(1)
    const [search, setSearch] = useState("")
    const [estado, setEstado] = useState<EstadoOperatividadEnum | "TODOS">("TODOS")

    const { data: response, isLoading, isError } = useQuery({
        queryKey: ['certificados', page, search, estado],
        queryFn: () => certificadosApi.getAll({
            page,
            limit: 20,
            q: search !== "" ? search : undefined,
            estado: estado !== "TODOS" ? estado : undefined
        }),
    })

    if (isError) {
        return (
            <div className="p-8 text-center text-red-500">
                Error al cargar los certificados. Por favor intente nuevamente.
            </div>
        )
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold tracking-tight">Certificados de Operatividad</h1>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Listado de Certificados</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="flex flex-col sm:flex-row gap-4 mb-6">
                        <div className="w-full sm:w-1/3">
                            <Input
                                placeholder="Buscar por folio o placa..."
                                value={search}
                                onChange={(e) => {
                                    setSearch(e.target.value)
                                    setPage(1)
                                }}
                            />
                        </div>
                        <div className="w-full sm:w-1/4">
                            <Select
                                value={estado}
                                onValueChange={(value: EstadoOperatividadEnum | "TODOS") => {
                                    setEstado(value)
                                    setPage(1)
                                }}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder="Filtrar por estado" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="TODOS">Todos los estados</SelectItem>
                                    <SelectItem value="APTO">Apto</SelectItem>
                                    <SelectItem value="CONDICIONAL">Condicional</SelectItem>
                                    <SelectItem value="NO_APTO">No Apto</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                    </div>

                    {isLoading ? (
                        <div className="flex justify-center py-8">
                            <Loader2 className="h-8 w-8 animate-spin text-primary" />
                        </div>
                    ) : (
                        <DataTable
                            columns={columns}
                            data={response?.data || []}
                            searchKey="folio_numero"
                        />
                    )}
                </CardContent>
            </Card>
        </div>
    )
}
