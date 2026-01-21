'use client'

import { useEffect, useState, useTransition } from 'react'
import { DataTable } from '@/components/ui/data-table'
import { Button } from '@/components/ui/button'
import { Plus } from 'lucide-react'
import { getUsuarios, deleteUsuario, toggleUsuarioEstado } from '@/lib/actions/usuario.actions'
import { columns, UsuarioColumn } from './columns'
import { UsuarioDialog } from './usuario-dialog'
import { toast } from 'sonner'
import { PageHeader } from '@/components/layout/page-header'

export default function UsuariosPage() {
    const [data, setData] = useState<UsuarioColumn[]>([])
    const [dialogOpen, setDialogOpen] = useState(false)
    const [editingUser, setEditingUser] = useState<UsuarioColumn | null>(null)
    const [loading, startTransition] = useTransition()

    const loadData = () => {
        startTransition(async () => {
            try {
                const users = await getUsuarios() as unknown as UsuarioColumn[]
                setData(users)
            } catch (error) {
                toast.error('Error cargando usuarios')
            }
        })
    }

    useEffect(() => {
        loadData()
    }, [])

    const handleCreate = () => {
        setEditingUser(null)
        setDialogOpen(true)
    }

    const handleEdit = (user: UsuarioColumn) => {
        setEditingUser(user)
        setDialogOpen(true)
    }

    const handleToggle = async (id: string, current: boolean) => {
        try {
            await toggleUsuarioEstado(id, !current)
            toast.success(`Usuario ${!current ? 'activado' : 'desactivado'}`)
            loadData()
        } catch (error: any) {
            toast.error(error.message)
        }
    }

    const handleDelete = async (id: string) => {
        if (!confirm('¿Estás seguro de eliminar este usuario? Esta acción no se puede deshacer.')) return

        try {
            await deleteUsuario(id)
            toast.success('Usuario eliminado')
            loadData()
        } catch (error: any) {
            toast.error(error.message)
        }
    }

    // Refresh cuando cierra dialogo (por si guardó)
    const handleDialogChange = (open: boolean) => {
        setDialogOpen(open)
        if (!open) loadData()
    }

    return (
        <div className="space-y-6">
            <PageHeader
                title="Gestión de Usuarios"
                description="Administra el acceso y roles de los usuarios del sistema."
            >
                <Button onClick={handleCreate}>
                    <Plus className="mr-2 h-4 w-4" />
                    Nuevo Usuario
                </Button>
            </PageHeader>

            <DataTable
                columns={columns(handleEdit, handleToggle, handleDelete)}
                data={data}
                searchKey="nombre_completo"
            />

            <UsuarioDialog
                open={dialogOpen}
                onOpenChange={handleDialogChange}
                userToEdit={editingUser}
            />
        </div>
    )
}
