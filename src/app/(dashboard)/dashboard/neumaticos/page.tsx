'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { neumaticosApi } from '@/lib/api/neumaticos'
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
import { NeumaticoForm } from '@/components/forms/neumatico-form'

export default function NeumaticosPage() {
    const [open, setOpen] = useState(false)
    const [editingNeumatico, setEditingNeumatico] = useState<any>(null)

    const { data: neumaticos, isLoading, isError } = useQuery({
        queryKey: ['neumaticos'],
        queryFn: neumaticosApi.getAll,
    })

    const handleEdit = (neumatico: any) => {
        setEditingNeumatico(neumatico)
        setOpen(true)
    }

    const handleClose = () => {
        setOpen(false)
        setEditingNeumatico(null)
    }

    const columns = getColumns({ onEdit: handleEdit })

    if (isError) {
        return (
            <div className="p-8 text-center text-red-500">
                Error al cargar los neumáticos. Por favor intente nuevamente.
            </div>
        )
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold tracking-tight">Neumáticos</h1>

                <Dialog open={open} onOpenChange={setOpen}>
                    <Button onClick={() => {
                        setEditingNeumatico(null)
                        setOpen(true)
                    }}>
                        <Plus className="mr-2 h-4 w-4" /> Nuevo Neumático
                    </Button>
                    <DialogContent className="sm:max-w-[600px]">
                        <DialogHeader>
                            <DialogTitle>{editingNeumatico ? 'Editar Neumático' : 'Registrar Neumático'}</DialogTitle>
                            <DialogDescription>
                                {editingNeumatico
                                    ? 'Modifique los datos del neumático seleccionado.'
                                    : 'Ingrese los datos del nuevo neumático para el inventario.'}
                            </DialogDescription>
                        </DialogHeader>
                        <NeumaticoForm
                            initialData={editingNeumatico}
                            onSuccess={handleClose}
                        />
                    </DialogContent>
                </Dialog>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Listado de Neumáticos</CardTitle>
                </CardHeader>
                <CardContent>
                    {isLoading ? (
                        <div className="flex justify-center py-8">
                            <Loader2 className="h-8 w-8 animate-spin text-primary" />
                        </div>
                    ) : (
                        <DataTable
                            columns={columns}
                            data={neumaticos || []}
                            searchKey="numero_serie"
                        />
                    )}
                </CardContent>
            </Card>
        </div>
    )
}
