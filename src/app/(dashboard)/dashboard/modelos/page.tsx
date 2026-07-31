"use client"

import { useState, Suspense } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useSearchParams, useRouter } from 'next/navigation'
import { useToast } from '@/components/ui/use-toast'
import { modelosNeumaticoApi } from '@/lib/api/modelos-neumatico'
import { DataTable } from '@/components/ui/data-table'
import { getColumns } from './columns'
import { Button } from '@/components/ui/button'
import { Plus, Loader2, Filter, X } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog"
import { ModeloNeumaticoForm } from '@/components/forms/modelo-neumatico-form'

function ModelosContent() {
    const [open, setOpen] = useState(false)
    const [editingModelo, setEditingModelo] = useState<any>(null)
    const queryClient = useQueryClient()
    const { toast } = useToast()
    const searchParams = useSearchParams()
    const router = useRouter()

    const fabricanteId = searchParams.get('fabricanteId')

    const { data: modelos, isLoading, isError } = useQuery({
        queryKey: ['modelos-neumatico'],
        queryFn: modelosNeumaticoApi.getAll,
    })

    const handleEdit = (modelo: any) => {
        setEditingModelo(modelo)
        setOpen(true)
    }

    const handleClose = () => {
        setOpen(false)
        setEditingModelo(null)
    }

    const deleteMutation = useMutation({
        mutationFn: modelosNeumaticoApi.delete,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['modelos-neumatico'] })
            toast({
                title: "Modelo eliminado",
                description: "El modelo de neumático fue eliminado correctamente."
            })
        },
        onError: (error: Error) => {
            toast({
                variant: "destructive",
                title: "Error al eliminar",
                description: error.message || "No se pudo eliminar el modelo."
            })
        }
    })

    const handleDelete = (id: string, nombre: string) => {
        if (window.confirm(`¿Está seguro de eliminar el modelo "${nombre}"? Esta acción no se puede deshacer.`)) {
            deleteMutation.mutate(id)
        }
    }

    const columns = getColumns({
        onEdit: handleEdit,
        onDelete: handleDelete
    })

    const modelosFiltrados = (modelos && fabricanteId)
        ? modelos.filter((m: any) => (m.fabricante?.id || m.fabricante_id) === fabricanteId)
        : (modelos || [])

    const fabricanteNombre = (modelosFiltrados.length > 0 && fabricanteId)
        ? ((modelosFiltrados[0] as any).fabricante?.nombre || (modelosFiltrados[0] as any).fabricante_nombre || 'Seleccionado')
        : null

    if (isError) {
        return (
            <div className="p-8 text-center text-red-500">
                Error al cargar los modelos de neumáticos. Por favor intente nuevamente.
            </div>
        )
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Modelos de Neumáticos</h1>
                    <p className="text-sm text-muted-foreground mt-1">
                        Gestión de catálogo de marcas, medidas y especificaciones técnicas.
                    </p>
                </div>

                <Dialog open={open} onOpenChange={setOpen}>
                    <Button onClick={() => {
                        setEditingModelo(null)
                        setOpen(true)
                    }}>
                        <Plus className="mr-2 h-4 w-4" /> Nuevo Modelo
                    </Button>
                    <DialogContent className="sm:max-w-[550px]">
                        <DialogHeader>
                            <DialogTitle>{editingModelo ? 'Editar Modelo' : 'Registrar Modelo'}</DialogTitle>
                            <DialogDescription>
                                {editingModelo
                                    ? 'Modifique las especificaciones técnicas del modelo seleccionado.'
                                    : 'Ingrese las especificaciones del nuevo modelo de neumático.'}
                            </DialogDescription>
                        </DialogHeader>
                        <ModeloNeumaticoForm
                            initialData={editingModelo}
                            onSuccess={handleClose}
                        />
                    </DialogContent>
                </Dialog>
            </div>

            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
                    <CardTitle className="text-base font-semibold">Catálogo de Modelos</CardTitle>
                    {fabricanteId && (
                        <div className="flex items-center gap-2">
                            <Badge variant="outline" className="bg-primary/10 text-primary border-primary/20 gap-1.5 py-1 px-3">
                                <Filter className="h-3.5 w-3.5" />
                                <span>Filtrado por: <strong>{fabricanteNombre || 'Fabricante'}</strong></span>
                            </Badge>
                            <Button
                                variant="ghost"
                                size="sm"
                                className="h-7 px-2 text-xs text-muted-foreground hover:text-foreground"
                                onClick={() => router.push('/dashboard/modelos')}
                            >
                                <X className="h-3.5 w-3.5 mr-1" /> Limpiar filtro
                            </Button>
                        </div>
                    )}
                </CardHeader>
                <CardContent>
                    {isLoading ? (
                        <div className="flex justify-center py-8">
                            <Loader2 className="h-8 w-8 animate-spin text-primary" />
                        </div>
                    ) : (
                        <DataTable
                            columns={columns}
                            data={modelosFiltrados}
                            searchKey="nombre"
                        />
                    )}
                </CardContent>
            </Card>
        </div>
    )
}

export default function ModelosNeumaticoPage() {
    return (
        <Suspense fallback={
            <div className="flex justify-center py-8">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
        }>
            <ModelosContent />
        </Suspense>
    )
}
