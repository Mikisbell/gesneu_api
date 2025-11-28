'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { neumaticosApi } from '@/lib/api/neumaticos'
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
import { NeumaticoForm } from '@/components/forms/neumatico-form'

export default function NeumaticosPage() {
    const [open, setOpen] = useState(false)

    const { data: neumaticos, isLoading, isError } = useQuery({
        queryKey: ['neumaticos'],
        queryFn: neumaticosApi.getAll,
    })

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
                    <DialogTrigger asChild>
                        <Button>
                            <Plus className="mr-2 h-4 w-4" /> Nuevo Neumático
                        </Button>
                    </DialogTrigger>
                    <DialogContent className="sm:max-w-[600px]">
                        <DialogHeader>
                            <DialogTitle>Registrar Neumático</DialogTitle>
                            <DialogDescription>
                                Ingrese los datos del nuevo neumático para el inventario.
                            </DialogDescription>
                        </DialogHeader>
                        <NeumaticoForm onSuccess={() => setOpen(false)} />
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
