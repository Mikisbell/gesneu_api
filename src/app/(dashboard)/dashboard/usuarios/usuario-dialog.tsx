'use client'

import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog'
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { createUsuarioSchema, CreateUsuarioDTO } from '@/lib/validators/usuarios'
import { toast } from 'sonner'
import { createUsuario, updateUsuario } from '@/lib/actions/usuario.actions'
import { UsuarioColumn } from './columns'

interface UsuarioDialogProps {
    open: boolean
    onOpenChange: (open: boolean) => void
    userToEdit?: UsuarioColumn | null
}

export function UsuarioDialog({ open, onOpenChange, userToEdit }: UsuarioDialogProps) {
    const isEditing = !!userToEdit
    const [loading, setLoading] = useState(false)

    // Ajustar validador: Si estamos editando, password es opcional
    // Por simplicidad usaremos el schema de crear y manejaremos exceptions, o un schema dinámico.
    // Para simplificar: usaremos el schema base y si es edit, el field password no es required en backend, pero zod lo pide.
    // Solución rápida: Pasamos valores vacíos si es edit y no se toca.

    const form = useForm<CreateUsuarioDTO>({
        resolver: zodResolver(createUsuarioSchema),
        defaultValues: {
            username: '',
            nombre_completo: '',
            email: '',
            password: '',
            rol: 'OPERADOR',
        }
    })

    useEffect(() => {
        if (userToEdit) {
            form.reset({
                username: userToEdit.username,
                nombre_completo: userToEdit.nombre_completo,
                email: userToEdit.email,
                password: 'dummy_password', // Mock password to satisfy required (backend handles update logic)
                rol: userToEdit.rol as any
            })
        } else {
            form.reset({
                username: '',
                nombre_completo: '',
                email: '',
                password: '',
                rol: 'OPERADOR',
            })
        }
    }, [userToEdit, form])

    async function onSubmit(data: CreateUsuarioDTO) {
        setLoading(true)
        try {
            if (isEditing) {
                // Remove password from payload if it's the dummy one or empty
                const payload: any = { ...data }
                if (payload.password === 'dummy_password' || !payload.password) {
                    delete payload.password
                }

                await updateUsuario(userToEdit!.id, payload)
                toast.success('Usuario actualizado correctamente')
            } else {
                await createUsuario(data)
                toast.success('Usuario creado correctamente')
            }
            onOpenChange(false)
        } catch (error: any) {
            toast.error(error.message || 'Error al guardar usuario')
        } finally {
            setLoading(false)
        }
    }

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>{isEditing ? 'Editar Usuario' : 'Nuevo Usuario'}</DialogTitle>
                    <DialogDescription>
                        {isEditing ? 'Modifica los datos del usuario.' : 'Crea un nuevo usuario para acceder al sistema.'}
                    </DialogDescription>
                </DialogHeader>

                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                        <FormField
                            control={form.control}
                            name="nombre_completo"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Nombre Completo</FormLabel>
                                    <FormControl>
                                        <Input placeholder="Juan Pérez" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="username"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Usuario</FormLabel>
                                    <FormControl>
                                        <Input placeholder="juan.perez" {...field} disabled={isEditing} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="email"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Email</FormLabel>
                                    <FormControl>
                                        <Input type="email" placeholder="juan@empresa.com" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        {(!isEditing || (isEditing && form.watch('password') !== 'dummy_password')) && (
                            <FormField
                                control={form.control}
                                name="password"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Contraseña {isEditing && '(Opcional)'}</FormLabel>
                                        <FormControl>
                                            <Input type="password" {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        )}

                        {/* Campo de contraseña visible en modo edición solo si user quiere cambiarla */}
                        {isEditing && form.watch('password') === 'dummy_password' && (
                            <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                className="w-full"
                                onClick={() => form.setValue('password', '')}
                            >
                                Cambiar Contraseña
                            </Button>
                        )}


                        <FormField
                            control={form.control}
                            name="rol"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Rol</FormLabel>
                                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                                        <FormControl>
                                            <SelectTrigger>
                                                <SelectValue placeholder="Selecciona un rol" />
                                            </SelectTrigger>
                                        </FormControl>
                                        <SelectContent>
                                            <SelectItem value="OPERADOR">Operador (Campo)</SelectItem>
                                            <SelectItem value="GESTOR">Gestor (Avanzado)</SelectItem>
                                            <SelectItem value="ADMIN">Administrador</SelectItem>
                                        </SelectContent>
                                    </Select>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <DialogFooter>
                            <Button type="submit" disabled={loading}>
                                {loading ? 'Guardando...' : 'Guardar'}
                            </Button>
                        </DialogFooter>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    )
}
