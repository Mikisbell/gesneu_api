'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { apiClient } from '@/lib/api/client';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { useToast } from '@/hooks/use-toast';
import { Search, Trash2, AlertTriangle, Loader2 } from 'lucide-react';

// Form schema
const desechoFormSchema = z.object({
    neumatico_id: z.string().uuid('Debe seleccionar un neumático válido'),
    motivo_desecho_id: z.string().uuid('Debe seleccionar un motivo de desecho'),
    observaciones: z.string().optional(),
});

type DesechoForm = z.infer<typeof desechoFormSchema>;

export default function DesechoPage() {
    const { toast } = useToast();
    const queryClient = useQueryClient();
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedTire, setSelectedTire] = useState<any>(null);
    const [showConfirmDialog, setShowConfirmDialog] = useState(false);

    // Form
    const form = useForm<DesechoForm>({
        resolver: zodResolver(desechoFormSchema),
        defaultValues: {
            neumatico_id: '',
            motivo_desecho_id: '',
            observaciones: '',
        },
    });

    // Fetch tire by serial number
    const { data: searchedTire, isLoading: isSearching, refetch: searchTire } = useQuery({
        queryKey: ['neumatico-search', searchTerm],
        queryFn: async () => {
            if (!searchTerm) return null;
            const response = await apiClient(`/api/v1/neumaticos?numero_serie=${searchTerm}`) as Response;
            const data = await response.json();
            return data.data?.[0] || null;
        },
        enabled: false,
    });

    // Fetch disposal reasons
    const { data: motivos } = useQuery({
        queryKey: ['motivos-desecho'],
        queryFn: async () => {
            const response = await apiClient('/api/v1/catalogos/motivos-desecho') as Response;
            const data = await response.json();
            return data.data || [];
        },
    });

    // Mutation to register disposal
    const mutation = useMutation({
        mutationFn: async (data: DesechoForm) => {
            const payload = {
                tipo_evento: 'DESECHO',
                neumatico_id: data.neumatico_id,
                motivo_desecho_id: data.motivo_desecho_id,
                observaciones: data.observaciones,
            };
            return apiClient('/api/v1/neumaticos/eventos', {
                method: 'POST',
                body: JSON.stringify(payload)
            });
        },
        onSuccess: () => {
            toast({
                title: 'Desecho registrado',
                description: 'El neumático ha sido dado de baja exitosamente.',
            });
            queryClient.invalidateQueries({ queryKey: ['neumaticos'] });
            form.reset();
            setSelectedTire(null);
            setSearchTerm('');
            setShowConfirmDialog(false);
        },
        onError: (error: any) => {
            toast({
                title: 'Error',
                description: error.message || 'No se pudo registrar el desecho.',
                variant: 'destructive',
            });
        },
    });

    // Handle search
    const handleSearch = async () => {
        if (!searchTerm.trim()) {
            toast({
                title: 'Campo vacío',
                description: 'Ingrese un número de serie para buscar.',
                variant: 'destructive',
            });
            return;
        }

        const result = await searchTire();
        if (result.data) {
            setSelectedTire(result.data);
            form.setValue('neumatico_id', result.data.id);
        } else {
            toast({
                title: 'No encontrado',
                description: 'No se encontró un neumático con ese número de serie.',
                variant: 'destructive',
            });
            setSelectedTire(null);
        }
    };

    // Check if tire is installed
    const isTireInstalled = selectedTire?.estado_actual === 'INSTALADO';

    // Handle form submission
    const onSubmit = (data: DesechoForm) => {
        if (isTireInstalled) {
            toast({
                title: 'Error',
                description: 'El neumático está instalado. Debe desmontarlo primero.',
                variant: 'destructive',
            });
            return;
        }
        setShowConfirmDialog(true);
    };

    const confirmDisposal = () => {
        mutation.mutate(form.getValues());
    };

    return (
        <div className="container mx-auto p-6 max-w-4xl">
            <div className="mb-6">
                <h1 className="text-3xl font-bold">Desecho de Neumático</h1>
                <p className="text-muted-foreground mt-2">
                    Dar de baja un neumático de forma definitiva
                </p>
            </div>

            {/* Search Section */}
            <Card className="mb-6">
                <CardHeader>
                    <CardTitle>Buscar Neumático</CardTitle>
                    <CardDescription>Ingrese el número de serie del neumático a desechar</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="flex gap-2">
                        <Input
                            placeholder="Número de serie..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                        />
                        <Button onClick={handleSearch} disabled={isSearching}>
                            {isSearching ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
                            <span className="ml-2">Buscar</span>
                        </Button>
                    </div>

                    {selectedTire && (
                        <div className="mt-4 p-4 bg-muted rounded-lg">
                            <h3 className="font-semibold mb-2">Neumático Seleccionado</h3>
                            <div className="grid grid-cols-2 gap-2 text-sm">
                                <div>
                                    <span className="text-muted-foreground">Serie:</span>
                                    <span className="ml-2 font-medium">{selectedTire.numero_serie}</span>
                                </div>
                                <div>
                                    <span className="text-muted-foreground">Estado:</span>
                                    <span className={`ml-2 font-medium ${isTireInstalled ? 'text-red-600' : 'text-green-600'}`}>
                                        {selectedTire.estado_actual}
                                    </span>
                                </div>
                                <div>
                                    <span className="text-muted-foreground">Modelo:</span>
                                    <span className="ml-2">{selectedTire.modelo?.nombre || 'N/A'}</span>
                                </div>
                                <div>
                                    <span className="text-muted-foreground">Profundidad:</span>
                                    <span className="ml-2">{selectedTire.profundidad_remanente_actual_mm || 'N/A'} mm</span>
                                </div>
                            </div>

                            {isTireInstalled && (
                                <div className="mt-4 p-4 bg-destructive/10 text-destructive rounded-lg border border-destructive/20 flex gap-2">
                                    <AlertTriangle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                                    <p className="text-sm">
                                        Este neumático está instalado en un vehículo. Debe desmontarlo antes de desecharlo.
                                    </p>
                                </div>
                            )}
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Disposal Form */}
            {selectedTire && !isTireInstalled && (
                <Card>
                    <CardHeader>
                        <CardTitle>Datos de Desecho</CardTitle>
                        <CardDescription>Complete la información para registrar el desecho</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <Form {...form}>
                            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                                <FormField
                                    control={form.control}
                                    name="motivo_desecho_id"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Motivo de Desecho *</FormLabel>
                                            <Select onValueChange={field.onChange} value={field.value}>
                                                <FormControl>
                                                    <SelectTrigger>
                                                        <SelectValue placeholder="Seleccione un motivo..." />
                                                    </SelectTrigger>
                                                </FormControl>
                                                <SelectContent>
                                                    {motivos?.map((motivo: any) => (
                                                        <SelectItem key={motivo.id} value={motivo.id}>
                                                            {motivo.nombre}
                                                        </SelectItem>
                                                    ))}
                                                </SelectContent>
                                            </Select>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />

                                <FormField
                                    control={form.control}
                                    name="observaciones"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Observaciones</FormLabel>
                                            <FormControl>
                                                <Textarea
                                                    placeholder="Detalles adicionales sobre el desecho..."
                                                    {...field}
                                                />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />

                                <Button type="submit" className="w-full" disabled={mutation.isPending}>
                                    <Trash2 className="mr-2 h-4 w-4" />
                                    {mutation.isPending ? 'Registrando...' : 'Registrar Desecho'}
                                </Button>
                            </form>
                        </Form>
                    </CardContent>
                </Card>
            )}

            {/* Confirmation Dialog */}
            <Dialog open={showConfirmDialog} onOpenChange={setShowConfirmDialog}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Confirmar Desecho</DialogTitle>
                        <DialogDescription>
                            Esta acción dará de baja el neumático de forma definitiva.
                        </DialogDescription>
                    </DialogHeader>
                    <div className="py-4">
                        <div className="space-y-2 text-sm">
                            <div>
                                <span className="font-medium">Neumático:</span>
                                <span className="ml-2">{selectedTire?.numero_serie}</span>
                            </div>
                            <div>
                                <span className="font-medium">Motivo:</span>
                                <span className="ml-2">
                                    {motivos?.find((m: any) => m.id === form.getValues('motivo_desecho_id'))?.nombre}
                                </span>
                            </div>
                            {form.getValues('observaciones') && (
                                <div>
                                    <span className="font-medium">Observaciones:</span>
                                    <p className="mt-1 text-muted-foreground">{form.getValues('observaciones')}</p>
                                </div>
                            )}
                        </div>
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setShowConfirmDialog(false)}>
                            Cancelar
                        </Button>
                        <Button variant="destructive" onClick={confirmDisposal} disabled={mutation.isPending}>
                            {mutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                            Confirmar Desecho
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
}
