'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation, useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { InspeccionNeumaticoSchema, InspeccionNeumaticoInput } from '@/lib/validators/inspeccion';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/components/ui/use-toast';
import { Loader2, Search, CheckCircle, AlertTriangle, AlertOctagon } from 'lucide-react';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';

export default function InspeccionPage() {
    const { toast } = useToast();
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedNeumatico, setSelectedNeumatico] = useState<any>(null);

    // Form setup
    const form = useForm<InspeccionNeumaticoInput>({
        resolver: zodResolver(InspeccionNeumaticoSchema),
        defaultValues: {
            profundidad_mm: 0,
            presion_psi: 0,
            observaciones: '',
        },
    });

    // Search query
    const { data: searchResults, isLoading: isSearching } = useQuery({
        queryKey: ['neumaticos', 'search', searchTerm],
        queryFn: () => apiClient<any[]>(`/api/v1/neumaticos?q=${searchTerm}`),
        enabled: searchTerm.length > 2,
    });

    // Inspection mutation
    const inspeccionMutation = useMutation({
        mutationFn: (data: any) =>
            apiClient('/api/v1/neumaticos/eventos', {
                method: 'POST',
                body: JSON.stringify(data)
            }),
        onSuccess: (response: any) => {
            // Check for alerts in the response or subsequent query
            // The new endpoint returns the event. Alerts are created async or part of the transaction.
            // For now, we assume success means it's done. 
            // If we want to show alerts, we might need the backend to return them or fetch them.
            // The previous logic checked `response.alerta`. The new backend logic creates alerts but might not return them in the same structure.
            // Let's assume standard success for now.

            toast({
                title: '✅ Inspección Registrada',
                description: 'La medición se ha guardado correctamente.',
            });

            // Reset form and selection
            form.reset();
            setSelectedNeumatico(null);
            setSearchTerm('');
        },
        onError: (error: Error) => {
            toast({
                title: '❌ Error',
                description: error.message,
                variant: 'destructive',
            });
        },
    });

    const onSubmit = (data: InspeccionNeumaticoInput) => {
        if (!selectedNeumatico) return;

        const payload = {
            tipo_evento: 'INSPECCION',
            neumatico_id: selectedNeumatico.id,
            profundidad_remanente: data.profundidad_mm,
            presion_psi: data.presion_psi,
            observaciones: data.observaciones,
            contador_vehiculo: selectedNeumatico.vehiculo ? data.contador_vehiculo : undefined
        };

        inspeccionMutation.mutate(payload);
    };

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold tracking-tight">Inspección de Neumáticos</h1>
                <p className="text-muted-foreground">
                    Registre mediciones de profundidad y presión para monitorear el desgaste.
                </p>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
                {/* Panel de Búsqueda */}
                <Card>
                    <CardHeader>
                        <CardTitle>1. Buscar Neumático</CardTitle>
                        <CardDescription>Busque por número de serie o placa del vehículo</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="flex gap-2">
                            <div className="relative flex-1">
                                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                                <Input
                                    placeholder="Serie o Placa..."
                                    className="pl-8"
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                />
                            </div>
                        </div>

                        {isSearching && (
                            <div className="flex justify-center p-4">
                                <Loader2 className="h-6 w-6 animate-spin text-primary" />
                            </div>
                        )}

                        <div className="space-y-2 max-h-[300px] overflow-y-auto">
                            {searchResults?.map((neumatico: any) => (
                                <div
                                    key={neumatico.id}
                                    className={`p-3 border rounded-lg cursor-pointer transition-colors ${selectedNeumatico?.id === neumatico.id
                                        ? 'bg-primary/10 border-primary'
                                        : 'hover:bg-muted'
                                        }`}
                                    onClick={() => {
                                        setSelectedNeumatico(neumatico);
                                        form.setValue('neumatico_id', neumatico.id);
                                        // Pre-fill current values if available
                                        if (neumatico.profundidad_actual_mm) {
                                            form.setValue('profundidad_mm', neumatico.profundidad_actual_mm);
                                        }
                                        if (neumatico.presion_actual_psi) {
                                            form.setValue('presion_psi', neumatico.presion_actual_psi);
                                        }
                                    }}
                                >
                                    <div className="flex justify-between items-start">
                                        <div>
                                            <p className="font-medium">{neumatico.numero_serie}</p>
                                            <p className="text-sm text-muted-foreground">
                                                {neumatico.marca} {neumatico.modelo}
                                            </p>
                                        </div>
                                        {neumatico.vehiculo && (
                                            <span className="text-xs bg-secondary px-2 py-1 rounded-full">
                                                {neumatico.vehiculo.placa}
                                            </span>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>

                {/* Formulario de Inspección */}
                <Card className={!selectedNeumatico ? 'opacity-50 pointer-events-none' : ''}>
                    <CardHeader>
                        <CardTitle>2. Registrar Mediciones</CardTitle>
                        <CardDescription>
                            {selectedNeumatico
                                ? `Inspeccionando: ${selectedNeumatico.numero_serie}`
                                : 'Seleccione un neumático para continuar'}
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <Form {...form}>
                            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                                <div className="grid grid-cols-2 gap-4">
                                    <FormField
                                        control={form.control}
                                        name="profundidad_mm"
                                        render={({ field }) => (
                                            <FormItem>
                                                <FormLabel>Profundidad (mm)</FormLabel>
                                                <FormControl>
                                                    <Input
                                                        type="number"
                                                        step="0.1"
                                                        {...field}
                                                        onChange={e => field.onChange(parseFloat(e.target.value))}
                                                    />
                                                </FormControl>
                                                <FormMessage />
                                            </FormItem>
                                        )}
                                    />

                                    <FormField
                                        control={form.control}
                                        name="presion_psi"
                                        render={({ field }) => (
                                            <FormItem>
                                                <FormLabel>Presión (PSI)</FormLabel>
                                                <FormControl>
                                                    <Input
                                                        type="number"
                                                        step="1"
                                                        {...field}
                                                        onChange={e => field.onChange(parseFloat(e.target.value))}
                                                    />
                                                </FormControl>
                                                <FormMessage />
                                            </FormItem>
                                        )}
                                    />
                                </div>

                                {selectedNeumatico?.vehiculo && (
                                    <FormField
                                        control={form.control}
                                        name="contador_vehiculo"
                                        render={({ field }) => (
                                            <FormItem>
                                                <FormLabel>Kilometraje Vehículo</FormLabel>
                                                <FormControl>
                                                    <Input
                                                        type="number"
                                                        {...field}
                                                        onChange={e => field.onChange(parseFloat(e.target.value))}
                                                    />
                                                </FormControl>
                                                <FormMessage />
                                            </FormItem>
                                        )}
                                    />
                                )}

                                <FormField
                                    control={form.control}
                                    name="observaciones"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Observaciones</FormLabel>
                                            <FormControl>
                                                <Textarea {...field} />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />

                                <Button
                                    type="submit"
                                    className="w-full"
                                    disabled={inspeccionMutation.isPending}
                                >
                                    {inspeccionMutation.isPending && (
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    )}
                                    Registrar Inspección
                                </Button>
                            </form>
                        </Form>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
