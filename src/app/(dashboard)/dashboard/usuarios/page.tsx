'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { useToast } from '@/components/ui/use-toast';
import { Plus, Loader2, Search, Pencil, Trash2, Shield, UserPlus } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

const ROLES = [
    { value: 'ADMIN', label: 'Administrador', color: 'bg-red-500' },
    { value: 'GESTOR', label: 'Gestor de Flota', color: 'bg-blue-500' },
    { value: 'OPERADOR', label: 'Operador', color: 'bg-green-500' },
    { value: 'CONSULTOR', label: 'Consultor', color: 'bg-gray-500' },
];

interface Usuario {
    id: string;
    username: string;
    email: string;
    nombre_completo: string;
    rol: string;
    activo: boolean;
    creado_en: string;
}

export default function UsuariosPage() {
    const { toast } = useToast();
    const queryClient = useQueryClient();
    const [search, setSearch] = useState('');
    const [isCreateOpen, setIsCreateOpen] = useState(false);
    const [editingUser, setEditingUser] = useState<Usuario | null>(null);

    // Form state
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        nombre_completo: '',
        password: '',
        rol: 'OPERADOR',
    });

    // Fetch usuarios
    const { data, isLoading, refetch } = useQuery({
        queryKey: ['usuarios', search],
        queryFn: async () => {
            const res = await apiClient<{ data: Usuario[]; meta: any }>(`/api/v1/usuarios?search=${search}`);
            return res;
        },
    });

    // Create mutation
    const createMutation = useMutation({
        mutationFn: (data: typeof formData) =>
            apiClient('/api/v1/usuarios', { method: 'POST', body: JSON.stringify(data) }),
        onSuccess: () => {
            toast({ title: '✅ Usuario creado', description: 'El usuario ha sido registrado correctamente.' });
            queryClient.invalidateQueries({ queryKey: ['usuarios'] });
            resetForm();
            setIsCreateOpen(false);
        },
        onError: (error: any) => {
            toast({ title: '❌ Error', description: error.message || 'No se pudo crear el usuario.', variant: 'destructive' });
        },
    });

    // Update mutation
    const updateMutation = useMutation({
        mutationFn: (data: { id: string; updates: Partial<typeof formData> }) =>
            apiClient(`/api/v1/usuarios/${data.id}`, { method: 'PATCH', body: JSON.stringify(data.updates) }),
        onSuccess: () => {
            toast({ title: '✅ Usuario actualizado', description: 'Los cambios han sido guardados.' });
            queryClient.invalidateQueries({ queryKey: ['usuarios'] });
            resetForm();
            setEditingUser(null);
        },
        onError: (error: any) => {
            toast({ title: '❌ Error', description: error.message || 'No se pudo actualizar el usuario.', variant: 'destructive' });
        },
    });

    const resetForm = () => {
        setFormData({ username: '', email: '', nombre_completo: '', password: '', rol: 'OPERADOR' });
    };

    const handleEdit = (user: Usuario) => {
        setEditingUser(user);
        setFormData({
            username: user.username,
            email: user.email,
            nombre_completo: user.nombre_completo,
            password: '',
            rol: user.rol,
        });
    };

    const handleSubmit = () => {
        if (editingUser) {
            const updates: any = { ...formData };
            if (!updates.password) delete updates.password;
            updateMutation.mutate({ id: editingUser.id, updates });
        } else {
            createMutation.mutate(formData);
        }
    };

    const getRoleBadge = (rol: string) => {
        const roleInfo = ROLES.find(r => r.value === rol);
        return (
            <Badge className={`${roleInfo?.color || 'bg-gray-500'} text-white`}>
                {roleInfo?.label || rol}
            </Badge>
        );
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Usuarios</h1>
                    <p className="text-muted-foreground">Gestión de usuarios y roles del sistema</p>
                </div>
                <Button onClick={() => { resetForm(); setIsCreateOpen(true); }}>
                    <UserPlus className="mr-2 h-4 w-4" /> Nuevo Usuario
                </Button>
            </div>

            {/* Search */}
            <Card>
                <CardContent className="pt-6">
                    <div className="flex gap-2">
                        <div className="relative flex-1">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                            <Input
                                placeholder="Buscar por nombre, usuario o email..."
                                value={search}
                                onChange={(e) => setSearch(e.target.value)}
                                className="pl-10"
                            />
                        </div>
                        <Button variant="secondary" onClick={() => refetch()}>
                            Buscar
                        </Button>
                    </div>
                </CardContent>
            </Card>

            {/* Table */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Shield className="h-5 w-5" />
                        Listado de Usuarios
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    {isLoading ? (
                        <div className="flex justify-center py-8">
                            <Loader2 className="h-8 w-8 animate-spin text-primary" />
                        </div>
                    ) : (
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Usuario</TableHead>
                                    <TableHead>Nombre</TableHead>
                                    <TableHead>Email</TableHead>
                                    <TableHead>Rol</TableHead>
                                    <TableHead>Estado</TableHead>
                                    <TableHead className="text-right">Acciones</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {(data?.data || []).map((user) => (
                                    <TableRow key={user.id}>
                                        <TableCell className="font-medium">{user.username}</TableCell>
                                        <TableCell>{user.nombre_completo}</TableCell>
                                        <TableCell className="text-muted-foreground">{user.email}</TableCell>
                                        <TableCell>{getRoleBadge(user.rol)}</TableCell>
                                        <TableCell>
                                            <Badge variant={user.activo ? 'default' : 'secondary'}>
                                                {user.activo ? 'Activo' : 'Inactivo'}
                                            </Badge>
                                        </TableCell>
                                        <TableCell className="text-right">
                                            <Button variant="ghost" size="sm" onClick={() => handleEdit(user)}>
                                                <Pencil className="h-4 w-4" />
                                            </Button>
                                        </TableCell>
                                    </TableRow>
                                ))}
                                {(data?.data || []).length === 0 && (
                                    <TableRow>
                                        <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">
                                            No se encontraron usuarios
                                        </TableCell>
                                    </TableRow>
                                )}
                            </TableBody>
                        </Table>
                    )}
                </CardContent>
            </Card>

            {/* Create/Edit Dialog */}
            <Dialog open={isCreateOpen || !!editingUser} onOpenChange={(open) => {
                if (!open) { setIsCreateOpen(false); setEditingUser(null); resetForm(); }
            }}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>{editingUser ? 'Editar Usuario' : 'Nuevo Usuario'}</DialogTitle>
                        <DialogDescription>
                            {editingUser ? 'Modifique los datos del usuario.' : 'Complete los datos para crear un nuevo usuario.'}
                        </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label>Usuario *</Label>
                                <Input
                                    value={formData.username}
                                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                                    placeholder="usuario123"
                                    disabled={!!editingUser}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label>Email *</Label>
                                <Input
                                    type="email"
                                    value={formData.email}
                                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                    placeholder="usuario@empresa.com"
                                />
                            </div>
                        </div>
                        <div className="space-y-2">
                            <Label>Nombre Completo *</Label>
                            <Input
                                value={formData.nombre_completo}
                                onChange={(e) => setFormData({ ...formData, nombre_completo: e.target.value })}
                                placeholder="Juan Pérez"
                            />
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label>{editingUser ? 'Nueva Contraseña' : 'Contraseña *'}</Label>
                                <Input
                                    type="password"
                                    value={formData.password}
                                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                    placeholder={editingUser ? '(dejar vacío para mantener)' : '••••••••'}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label>Rol *</Label>
                                <Select value={formData.rol} onValueChange={(v) => setFormData({ ...formData, rol: v })}>
                                    <SelectTrigger>
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {ROLES.map((role) => (
                                            <SelectItem key={role.value} value={role.value}>
                                                {role.label}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                        </div>
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => { setIsCreateOpen(false); setEditingUser(null); }}>
                            Cancelar
                        </Button>
                        <Button onClick={handleSubmit} disabled={createMutation.isPending || updateMutation.isPending}>
                            {(createMutation.isPending || updateMutation.isPending) && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                            {editingUser ? 'Guardar Cambios' : 'Crear Usuario'}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
}
