'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { neumaticosApi } from '@/lib/api/neumaticos'
import { DataTable } from '@/components/ui/data-table'
import { getColumns } from './columns'
import { Plus, Disc, AlertTriangle } from 'lucide-react'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
import { NeumaticoForm } from '@/components/forms/neumatico-form'
import { ConfirmDialog } from '@/components/ui/confirm-dialog'
import {
    PageHeader,
    EmptyState,
    SkeletonTable,
    LoadingButton
} from '@/components/ui/patterns'
import { Button } from '@/components/ui/button'
import { useToast } from '@/components/ui/use-toast'

export default function NeumaticosPage() {
    const [open, setOpen] = useState(false)
    const [editingNeumatico, setEditingNeumatico] = useState<any>(null)
    const [deleteDialog, setDeleteDialog] = useState<{ open: boolean; id: string; name: string }>({
        open: false,
        id: '',
        name: ''
    })

    const queryClient = useQueryClient()
    const { toast } = useToast()

    // ✅ Patrón homogéneo: useQuery
    const { data: neumaticos, isLoading, isError, refetch } = useQuery({
        queryKey: ['neumaticos'],
        queryFn: neumaticosApi.getAll,
    })

    // ✅ Patrón homogéneo: Optimistic delete
    const deleteMutation = useMutation({
        mutationFn: neumaticosApi.delete,
        onMutate: async (deletedId) => {
            await queryClient.cancelQueries({ queryKey: ['neumaticos'] })
            const previous = queryClient.getQueryData(['neumaticos'])
            queryClient.setQueryData(['neumaticos'], (old: any) =>
                old?.filter((n: any) => n.id !== deletedId)
            )
            return { previous }
        },
        onSuccess: () => {
            toast({
                title: "Neumático eliminado",
                description: "El registro ha sido eliminado correctamente."
            })
            setDeleteDialog({ open: false, id: '', name: '' })
        },
        onError: (error: Error, variables, context) => {
            queryClient.setQueryData(['neumaticos'], context?.previous)
            toast({
                variant: "destructive",
                title: "Error al eliminar",
                description: error.message || "No se pudo eliminar el registro."
            })
        }
    })

    const handleEdit = (neumatico: any) => {
        setEditingNeumatico(neumatico)
        setOpen(true)
    }

    const handleClose = () => {
        setOpen(false)
        setEditingNeumatico(null)
    }

    const handleDeleteClick = (id: string, numeroSerie: string) => {
        setDeleteDialog({ open: true, id, name: numeroSerie })
    }

    const columns = getColumns({
        onEdit: handleEdit,
        onDelete: handleDeleteClick
    })

    return (
        <div className="space-y-6">
            {/* ✅ Patrón homogéneo: PageHeader */}
            <PageHeader
                title="Neumáticos"
                description="Gestiona el inventario completo de neumáticos"
                action={
                    <Button onClick={() => setOpen(true)} data-testid="btn-new-neumatico">
                        <Plus className="mr-2 h-4 w-4" />
                        Nuevo Neumático
                    </Button>
                }
            />

            {/* ✅ Patrón homogéneo: Loading state */}
            {isLoading && <SkeletonTable rows={8} />}

            {/* ✅ Patrón homogéneo: Error state */}
            {isError && (
                <EmptyState
                    icon={<AlertTriangle className="h-8 w-8 text-muted-foreground" />}
                    title="Error al cargar datos"
                    description="No pudimos conectar con el servidor. Por favor intenta nuevamente."
                    action={
                        <Button onClick={() => refetch()} variant="outline">
                            Reintentar
                        </Button>
                    }
                />
            )}

            {/* ✅ Patrón homogéneo: Empty state */}
            {!isLoading && !isError && neumaticos?.length === 0 && (
                <EmptyState
                    icon={<Disc className="h-8 w-8 text-muted-foreground" />}
                    title="No hay neumáticos registrados"
                    description="Comienza agregando tu primer neumático al inventario."
                    action={
                        <Button onClick={() => setOpen(true)} data-testid="btn-new-neumatico-empty">
                            <Plus className="mr-2 h-4 w-4" />
                            Agregar Neumático
                        </Button>
                    }
                />
            )}

            {/* ✅ Data display */}
            {!isLoading && !isError && neumaticos && neumaticos.length > 0 && (
                <DataTable columns={columns} data={neumaticos} />
            )}

            {/* ✅ Formulario modal */}
            <Dialog open={open} onOpenChange={setOpen}>
                <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
                    <DialogHeader>
                        <DialogTitle>
                            {editingNeumatico ? 'Editar Neumático' : 'Nuevo Neumático'}
                        </DialogTitle>
                        <DialogDescription>
                            {editingNeumatico
                                ? 'Modifica los datos del neumático seleccionado.'
                                : 'Ingresa los datos para registrar un nuevo neumático en el inventario.'}
                        </DialogDescription>
                    </DialogHeader>
                    <NeumaticoForm
                        initialData={editingNeumatico}
                        onSuccess={handleClose}
                    />
                </DialogContent>
            </Dialog>

            {/* ✅ Patrón homogéneo: ConfirmDialog en vez de window.confirm */}
            <ConfirmDialog
                open={deleteDialog.open}
                onOpenChange={(open) => setDeleteDialog({ ...deleteDialog, open })}
                title="¿Eliminar neumático?"
                description={
                    <>
                        Esta acción eliminará permanentemente el neumático{' '}
                        <strong>{deleteDialog.name}</strong>. Esta acción no se puede deshacer.
                    </>
                }
                confirmText="Eliminar"
                cancelText="Cancelar"
                variant="destructive"
                onConfirm={() => deleteMutation.mutate(deleteDialog.id)}
            />
        </div>
    )
}
