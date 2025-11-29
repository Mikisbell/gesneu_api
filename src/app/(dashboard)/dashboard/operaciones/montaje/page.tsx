'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/components/ui/use-toast';
import { apiClient } from '@/lib/api/client';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { VehicleSchematic } from '@/components/vehicle/vehicle-schematic';
import { Truck } from 'lucide-react';

// Form schema

// Form schema
const montajeSchema = z.object({
    neumatico_id: z.string().uuid(),
    vehiculo_id: z.string().uuid(),
    posicion_neumatico_id: z.string().uuid().optional(),
    kilometraje_vehiculo: z.number().positive(),
    profundidad_mm: z.number().positive().max(25),
    presion_psi: z.number().positive().max(150),
    observaciones: z.string().optional(),
});

type MontajeForm = z.infer<typeof montajeSchema>;

export default function MontajePage() {
    const router = useRouter();
    const { toast } = useToast();

    // State
    const [selectedVehicleId, setSelectedVehicleId] = useState<string | null>(null);
    const [selectedPosition, setSelectedPosition] = useState<any | null>(null);
    const [isDialogOpen, setIsDialogOpen] = useState(false);

    // Form for the dialog
    const form = useForm<MontajeForm>({
        resolver: zodResolver(montajeSchema),
        defaultValues: {
            vehiculo_id: '',
            neumatico_id: '',
            kilometraje_vehiculo: 0,
            profundidad_mm: 10,
            presion_psi: 100,
            observaciones: '',
        },
    });

    // Fetch available vehicles (List)
    const { data: vehiculos, isLoading: loadingVehiculos } = useQuery({
        queryKey: ['vehiculos'],
        queryFn: () => apiClient<any[]>('/api/v1/vehiculos'),
    });

    // Fetch full vehicle details when selected
    const { data: vehicleDetails, isLoading: loadingDetails, refetch: refetchDetails } = useQuery({
        queryKey: ['vehicle', selectedVehicleId],
        queryFn: () => apiClient<any>(`/api/v1/vehiculos/${selectedVehicleId}/full`),
        enabled: !!selectedVehicleId,
    });

    // Fetch available tires (EN_STOCK)
    const { data: neumaticos, isLoading: loadingNeumaticos } = useQuery({
        queryKey: ['neumaticos', 'EN_STOCK'],
        queryFn: () => apiClient<any[]>('/api/v1/neumaticos?estado=EN_STOCK'),
    });

    // Montaje mutation
    const montajeMutation = useMutation({
        mutationFn: (data: MontajeForm) => apiClient('/api/v1/operaciones/montaje', { method: 'POST', body: JSON.stringify(data) }),
        onSuccess: () => {
            toast({
                title: '✅ Montaje Exitoso',
                description: 'El neumático ha sido montado correctamente.',
            });
            setIsDialogOpen(false);
            form.reset({
                vehiculo_id: selectedVehicleId || '',
                kilometraje_vehiculo: form.getValues('kilometraje_vehiculo'), // Keep mileage
                profundidad_mm: 10,
                presion_psi: 100,
                observaciones: '',
            });
            refetchDetails(); // Refresh schematic
        },
        onError: (error: any) => {
            toast({
                title: '❌ Error en Montaje',
                description: error.message || 'No se pudo completar el montaje',
                variant: 'destructive',
            });
        },
    });

    const handleVehicleSelect = (vehicleId: string) => {
        setSelectedVehicleId(vehicleId);
        form.setValue('vehiculo_id', vehicleId);
    };

    const handlePositionClick = (posicionId: string, neumaticoId?: string) => {
        if (neumaticoId) {
            toast({
                title: "Posición Ocupada",
                description: "Esta posición ya tiene un neumático montado. Debes desmontarlo primero.",
                variant: "destructive"
            });
            return;
        }

        // Find position object from details
        let foundPos = null;
        vehicleDetails?.tipo_vehiculo?.configuraciones?.forEach((c: any) => {
            const p = c.posiciones.find((pos: any) => pos.id === posicionId);
            if (p) foundPos = p;
        });

        setSelectedPosition(foundPos);
        form.setValue('posicion_neumatico_id', posicionId);
        // Pre-fill mileage if available from vehicle
        if (vehicleDetails?.kilometraje_actual) {
            form.setValue('kilometraje_vehiculo', vehicleDetails.kilometraje_actual);
        }
        setIsDialogOpen(true);
    };

    const onSubmit = (data: MontajeForm) => {
        montajeMutation.mutate(data);
    };

    return (
        <div className="container mx-auto py-8 max-w-6xl">
            <div className="mb-8 flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold mb-2">Montaje de Neumáticos</h1>
                    <p className="text-muted-foreground">Selecciona un vehículo y haz clic en una posición vacía para montar un neumático.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
                {/* Sidebar: Vehicle Selection */}
                <div className="lg:col-span-1 space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>Vehículo</CardTitle>
                            <CardDescription>Selecciona para ver esquema</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <Select onValueChange={handleVehicleSelect} value={selectedVehicleId || ''}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Seleccionar..." />
                                </SelectTrigger>
                                <SelectContent>
                                    {loadingVehiculos ? (
                                        <SelectItem value="loading" disabled>Cargando...</SelectItem>
                                    ) : vehiculos?.map((v: any) => (
                                        <SelectItem key={v.id} value={v.id}>
                                            {v.placa}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>

                            {selectedVehicleId && vehicleDetails && (
                                <div className="mt-4 text-sm space-y-2 text-muted-foreground">
                                    <div><span className="font-semibold">Marca:</span> {vehicleDetails.marca}</div>
                                    <div><span className="font-semibold">Modelo:</span> {vehicleDetails.modelo}</div>
                                    <div><span className="font-semibold">Km:</span> {vehicleDetails.kilometraje_actual}</div>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </div>

                {/* Main: Schematic */}
                <div className="lg:col-span-3">
                    {selectedVehicleId ? (
                        loadingDetails ? (
                            <div className="flex justify-center items-center h-64">
                                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
                            </div>
                        ) : (
                            <VehicleSchematic
                                vehiculo={vehicleDetails}
                                onPositionClick={handlePositionClick}
                            />
                        )
                    ) : (
                        <div className="flex flex-col items-center justify-center h-96 border-2 border-dashed rounded-lg bg-slate-50 text-muted-foreground">
                            <Truck className="w-16 h-16 mb-4 opacity-20" />
                            <p>Selecciona un vehículo para comenzar</p>
                        </div>
                    )}
                </div>
            </div>

            {/* Mounting Dialog */}
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                <DialogContent className="sm:max-w-[500px]">
                    <DialogHeader>
                        <DialogTitle>Montar Neumático</DialogTitle>
                        <DialogDescription>
                            Posición: {selectedPosition?.numero_posicion} ({selectedPosition?.lado_vehiculo}) - Eje {selectedPosition?.configuracion_eje_id}
                        </DialogDescription>
                    </DialogHeader>

                    <Form {...form}>
                        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                            <FormField
                                control={form.control}
                                name="neumatico_id"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Neumático (Stock)</FormLabel>
                                        <Select onValueChange={field.onChange} value={field.value}>
                                            <FormControl>
                                                <SelectTrigger>
                                                    <SelectValue placeholder="Seleccionar neumático..." />
                                                </SelectTrigger>
                                            </FormControl>
                                            <SelectContent>
                                                {loadingNeumaticos ? (
                                                    <SelectItem value="loading" disabled>Cargando...</SelectItem>
                                                ) : neumaticos?.length === 0 ? (
                                                    <SelectItem value="empty" disabled>No hay neumáticos disponibles</SelectItem>
                                                ) : (
                                                    neumaticos?.map((n: any) => (
                                                        <SelectItem key={n.id} value={n.id}>
                                                            {n.numero_serie} - {n.modelo?.medida}
                                                        </SelectItem>
                                                    ))
                                                )}
                                            </SelectContent>
                                        </Select>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />

                            <div className="grid grid-cols-2 gap-4">
                                <FormField
                                    control={form.control}
                                    name="profundidad_mm"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Profundidad (mm)</FormLabel>
                                            <FormControl>
                                                <Input type="number" step="0.1" {...field} onChange={e => field.onChange(parseFloat(e.target.value))} />
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
                                                <Input type="number" {...field} onChange={e => field.onChange(parseFloat(e.target.value))} />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />
                            </div>

                            <FormField
                                control={form.control}
                                name="kilometraje_vehiculo"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Kilometraje Vehículo</FormLabel>
                                        <FormControl>
                                            <Input type="number" {...field} onChange={e => field.onChange(parseFloat(e.target.value))} />
                                        </FormControl>
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
                                            <Textarea {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />

                            <div className="flex justify-end pt-4">
                                <Button type="submit" disabled={montajeMutation.isPending}>
                                    {montajeMutation.isPending ? 'Montando...' : 'Confirmar Montaje'}
                                </Button>
                            </div>
                        </form>
                    </Form>
                </DialogContent>
            </Dialog>
        </div>
    );
}
