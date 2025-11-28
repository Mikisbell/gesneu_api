'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { vehiculosApi } from '@/lib/api/vehiculos'
import { DataTable } from '@/components/ui/data-table'
import { columns } from './columns'
import { Button } from '@/components/ui/button'
import { Plus, Loader2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"
import { VehiculoForm } from '@/components/forms/vehiculo-form'

export default function VehiculosPage() {
    const [open, setOpen] = useState(false)

    const { data: vehiculos, isLoading, isError } = useQuery({
        queryKey: ['vehiculos'],
        queryFn: vehiculosApi.getAll,
    })

    if (isError) {
        return (
            <div className="p-8 text-center text-red-500">
                Error al cargar los vehículos. Por favor intente nuevamente.
            </div>
        )
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold tracking-tight">Vehículos</h1>

                <Dialog open={open} onOpenChange={setOpen}>
                    <Button onClick={() => setOpen(true)}>
                        <Plus className="mr-2 h-4 w-4" /> Nuevo Vehículo
                    </Button>
                    <DialogContent className="sm:max-w-[600px]">
                        <DialogHeader>
                            <DialogTitle>Registrar Vehículo</DialogTitle>
                            <DialogDescription>
                                Ingrese los datos del nuevo vehículo para la flota.
                            </DialogDescription>
                        </DialogHeader>
                        <VehiculoForm onSuccess={() => setOpen(false)} />
                    </DialogContent>
                </Dialog>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Listado de Vehículos</CardTitle>
                </CardHeader>
                <CardContent>
                    {isLoading ? (
                        <div className="flex justify-center py-8">
                            <Loader2 className="h-8 w-8 animate-spin text-primary" />
                        </div>
                    ) : (
                        <DataTable
                            columns={columns}
                            data={vehiculos || []}
                            searchKey="placa"
                        />
                    )}
                </CardContent>
            </Card>
        </div>
    )
}
