'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { proveedoresApi } from '@/lib/api/proveedores'
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
import { ProveedorForm } from '@/components/forms/proveedor-form'

export default function ProveedoresPage() {
    const [open, setOpen] = useState(false)
    const [editingProveedor, setEditingProveedor] = useState<any>(null)

    const { data: proveedores, isLoading, isError } = useQuery({
        queryKey: ['proveedores'],
        queryFn: proveedoresApi.getAll,
    })

    const handleEdit = (proveedor: any) => {
        setEditingProveedor(proveedor)
        setOpen(true)
    }

    const handleClose = () => {
        setOpen(false)
        setEditingProveedor(null)
    }

    const columns = getColumns({ onEdit: handleEdit })

    if (isError) {
        return (
            <div className="p-8 text-center text-red-500">
                Error al cargar los proveedores. Por favor intente nuevamente.
            </div>
        )
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold tracking-tight">Proveedores</h1>

                <Dialog open={open} onOpenChange={setOpen}>
                    <Button onClick={() => {
                        setEditingProveedor(null)
                        setOpen(true)
                    }}>
                        <Plus className="mr-2 h-4 w-4" /> Nuevo Proveedor
                    </Button>
                    <DialogContent className="sm:max-w-[600px]">
                        <DialogHeader>
                            <DialogTitle>{editingProveedor ? 'Editar Proveedor' : 'Registrar Proveedor'}</DialogTitle>
                            <DialogDescription>
                                {editingProveedor
                                    ? 'Modifique los datos del proveedor seleccionado.'
                                    : 'Ingrese los datos del nuevo proveedor para el catálogo.'}
                            </DialogDescription>
                        </DialogHeader>
                        <ProveedorForm
                            initialData={editingProveedor}
                            onSuccess={handleClose}
                        />
                    </DialogContent>
                </Dialog>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Listado de Proveedores</CardTitle>
                </CardHeader>
                <CardContent>
                    {isLoading ? (
                        <div className="flex justify-center py-8">
                            <Loader2 className="h-8 w-8 animate-spin text-primary" />
                        </div>
                    ) : (
                        <DataTable
                            columns={columns}
                            data={proveedores || []}
                            searchKey="nombre"
                        />
                    )}
                </CardContent>
            </Card>
        </div>
    )
}
