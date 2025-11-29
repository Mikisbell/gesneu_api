'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { almacenesApi } from '@/lib/api/almacenes'
import { DataTable } from '@/components/ui/data-table'
import { getColumns } from './columns'
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
import { AlmacenForm } from '@/components/forms/almacen-form'

export default function AlmacenesPage() {
    const [open, setOpen] = useState(false)
    const [editingAlmacen, setEditingAlmacen] = useState<any>(null)

    const { data: almacenes, isLoading, isError } = useQuery({
        queryKey: ['almacenes'],
        queryFn: almacenesApi.getAll,
    })

    const handleEdit = (almacen: any) => {
        setEditingAlmacen(almacen)
        setOpen(true)
    }

    const handleClose = () => {
        setOpen(false)
        setEditingAlmacen(null)
    }

    const columns = getColumns({ onEdit: handleEdit })

    if (isError) {
        return (
            <div className="p-8 text-center text-red-500">
                Error al cargar los almacenes. Por favor intente nuevamente.
            </div>
        )
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold tracking-tight">Almacenes</h1>

                <Dialog open={open} onOpenChange={setOpen}>
                    <Button onClick={() => {
                        setEditingAlmacen(null)
                        setOpen(true)
                    }}>
                        <Plus className="mr-2 h-4 w-4" /> Nuevo Almacén
                    </Button>
                    <DialogContent className="sm:max-w-[600px]">
                        <DialogHeader>
                            <DialogTitle>{editingAlmacen ? 'Editar Almacén' : 'Registrar Almacén'}</DialogTitle>
                            <DialogDescription>
                                {editingAlmacen
                                    ? 'Modifique los datos del almacén seleccionado.'
                                    : 'Ingrese los datos del nuevo almacén para el inventario.'}
                            </DialogDescription>
                        </DialogHeader>
                        <AlmacenForm
                            initialData={editingAlmacen}
                            onSuccess={handleClose}
                        />
                    </DialogContent>
                </Dialog>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Listado de Almacenes</CardTitle>
                </CardHeader>
                <CardContent>
                    {isLoading ? (
                        <div className="flex justify-center py-8">
                            <Loader2 className="h-8 w-8 animate-spin text-primary" />
                        </div>
                    ) : (
                        <DataTable
                            columns={columns}
                            data={almacenes || []}
                            searchKey="nombre"
                        />
                    )}
                </CardContent>
            </Card>
        </div>
    )
}
