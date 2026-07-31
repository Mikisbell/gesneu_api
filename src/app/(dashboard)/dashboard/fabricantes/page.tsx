"use client"

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useToast } from '@/components/ui/use-toast'
import { fabricantesApi } from '@/lib/api/fabricantes'
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
} from "@/components/ui/dialog"
import { FabricanteForm } from '@/components/forms/fabricante-form'

export default function FabricantesPage() {
    const [open, setOpen] = useState(false)
    const [editingFabricante, setEditingFabricante] = useState<any>(null)
    const queryClient = useQueryClient()
    const { toast } = useToast()

    const { data: fabricantes, isLoading, isError } = useQuery({
        queryKey: ['fabricantes'],
        queryFn: fabricantesApi.getAll,
    })

    const handleEdit = (fabricante: any) => {
        setEditingFabricante(fabricante)
        setOpen(true)
    }

    const handleClose = () => {
        setOpen(false)
        setEditingFabricante(null)
    }

    const deleteMutation = useMutation({
        mutationFn: fabricantesApi.delete,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['fabricantes'] })
            toast({
                title: "Fabricante eliminado",
                description: "El registro ha sido eliminado correctamente."
            })
        },
        onError: (error: Error) => {
            toast({
                variant: "destructive",
                title: "Error al eliminar",
                description: error.message || "No se pudo eliminar el fabricante."
            })
        }
    })

    const handleDelete = (id: string, nombre: string) => {
        if (window.confirm(`¿Está seguro de eliminar el fabricante "${nombre}"? Esta acción no se puede deshacer.`)) {
            deleteMutation.mutate(id)
        }
    }

    const columns = getColumns({
        onEdit: handleEdit,
        onDelete: handleDelete
    })

    if (isError) {
        return (
            <div className="p-8 text-center text-red-500">
                Error al cargar los fabricantes. Por favor intente nuevamente.
            </div>
        )
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Fabricantes de Neumáticos</h1>
                    <p className="text-sm text-muted-foreground mt-1">
                        Catálogo de marcas e industrias fabricantes (Michelin, Bridgestone, Goodyear, etc.)
                    </p>
                </div>

                <Dialog open={open} onOpenChange={setOpen}>
                    <Button onClick={() => {
                        setEditingFabricante(null)
                        setOpen(true)
                    }}>
                        <Plus className="mr-2 h-4 w-4" /> Nuevo Fabricante
                    </Button>
                    <DialogContent className="sm:max-w-[500px]">
                        <DialogHeader>
                            <DialogTitle>{editingFabricante ? 'Editar Fabricante' : 'Registrar Fabricante'}</DialogTitle>
                            <DialogDescription>
                                {editingFabricante
                                    ? 'Modifique los datos del fabricante seleccionado.'
                                    : 'Ingrese la información de la marca o fabricante.'}
                            </DialogDescription>
                        </DialogHeader>
                        <FabricanteForm
                            initialData={editingFabricante}
                            onSuccess={handleClose}
                        />
                    </DialogContent>
                </Dialog>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Listado de Fabricantes</CardTitle>
                </CardHeader>
                <CardContent>
                    {isLoading ? (
                        <div className="flex justify-center py-8">
                            <Loader2 className="h-8 w-8 animate-spin text-primary" />
                        </div>
                    ) : (
                        <DataTable
                            columns={columns}
                            data={fabricantes || []}
                            searchKey="nombre"
                        />
                    )}
                </CardContent>
            </Card>
        </div>
    )
}
