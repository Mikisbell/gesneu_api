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
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { VehicleSchematic } from '@/components/vehicle/vehicle-schematic';
import { Truck, RotateCw, ArrowRightLeft, Loader2 } from 'lucide-react';

// Form schema for Rotation
const rotacionSchema = z.object({
    vehiculo_id: z.string().uuid(),
    neumatico_id: z.string().uuid(),
    posicion_montaje_id: z.string().uuid(),
    contador_vehiculo: z.number().positive(),
    profundidad_remanente: z.number().positive().optional(),
    presion_psi: z.number().positive().optional(),
    observaciones: z.string().optional(),
});

type RotacionForm = z.infer<typeof rotacionSchema>;

export default function RotacionPage() {
    const router = useRouter();
    const { toast } = useToast();

    // State
    const [selectedVehicleId, setSelectedVehicleId] = useState<string | null>(null);
    const [sourceTire, setSourceTire] = useState<any | null>(null);
    const [targetPosition, setTargetPosition] = useState<any | null>(null);
    const [isDialogOpen, setIsDialogOpen] = useState(false);

    // Form
    const form = useForm<RotacionForm>({
        resolver: zodResolver(rotacionSchema),
        defaultValues: {
            vehiculo_id: '',
            neumatico_id: '',
            posicion_montaje_id: '',
            contador_vehiculo: 0,
            profundidad_remanente: undefined,
            presion_psi: undefined,
            observaciones: '',
        },
    });

    // Queries
    const { data: vehiculos, isLoading: loadingVehiculos } = useQuery({
        queryKey: ['vehiculos'],
        queryFn: () => apiClient<any[]>('/vehiculos'),
    });

    const { data: vehicleDetails, isLoading: loadingDetails, refetch: refetchDetails } = useQuery({
        queryKey: ['vehicle', selectedVehicleId],
        queryFn: () => apiClient<any>(`/vehiculos/${selectedVehicleId}/full`),
        enabled: !!selectedVehicleId,
    });

    // Mutation
    const rotacionMutation = useMutation({
        mutationFn: (data: RotacionForm) => {
            const payload = {
                tipo_evento: 'ROTACION',
                ...data
            };
            return apiClient('/neumaticos/eventos', { method: 'POST', body: JSON.stringify(payload) });
        },
        onSuccess: () => {
            toast({
                title: '✅ Rotación Exitosa',
                description: 'Los neumáticos han sido rotados correctamente.',
            });
            setIsDialogOpen(false);
            setSourceTire(null);
            setTargetPosition(null);
            form.reset({
                vehiculo_id: selectedVehicleId || '',
                contador_vehiculo: form.getValues('contador_vehiculo'),
            });
            refetchDetails();
        },
        onError: (error: any) => {
            toast({
                title: '❌ Error en Rotación',
                description: error.message || 'No se pudo completar la rotación',
                variant: 'destructive',
            });
        },
    });

    // Handlers
    const handleVehicleSelect = (vehicleId: string) => {
        setSelectedVehicleId(vehicleId);
        form.setValue('vehiculo_id', vehicleId);
        setSourceTire(null);
        setTargetPosition(null);
    };

    const handlePositionClick = (posicionId: string, neumaticoId?: string) => {
        // Find position object
        let clickedPos: any = null;
        vehicleDetails?.tipo_vehiculo?.configuraciones?.forEach((c: any) => {
            const p = c.posiciones.find((pos: any) => pos.id === posicionId);
            if (p) clickedPos = { ...p, configuracion_eje: c };
        });

        if (!sourceTire) {
            // Selecting Source
            if (!neumaticoId) {
                toast({
                    title: "Posición Vacía",
                    description: "Selecciona un neumático instalado para comenzar la rotación.",
                    variant: "destructive"
                });
                return;
            }
            // Find tire object (we need details like ID)
            // In a real app, we might need to fetch tire details or look it up from vehicleDetails if included
            // Assuming vehicleDetails includes tires in positions or we can infer it.
            // Actually, vehicleDetails usually has the structure. Let's assume we can get it.
            // For now, let's store the ID and position.
            setSourceTire({ id: neumaticoId, posicion: clickedPos });
            toast({
                title: "Origen Seleccionado",
                description: `Neumático seleccionado en posición ${clickedPos.numero_posicion}. Ahora selecciona el destino.`,
            });
        } else {
            // Selecting Target
            if (posicionId === sourceTire.posicion.id) {
                // Deselect
                setSourceTire(null);
                toast({ title: "Cancelado", description: "Selección cancelada" });
                return;
            }

            setTargetPosition(clickedPos);

            // Prepare form
            form.setValue('neumatico_id', sourceTire.id);
            form.setValue('posicion_montaje_id', posicionId);
            if (vehicleDetails?.odometro_actual) {
                form.setValue('contador_vehiculo', vehicleDetails.odometro_actual);
            }

            setIsDialogOpen(true);
        }
    };

    const onSubmit = (data: RotacionForm) => {
        rotacionMutation.mutate(data);
    };

    return (
        <div className="container mx-auto py-8 max-w-6xl">
            <div className="mb-8">
                <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">
                    <RotateCw className="h-8 w-8" />
                    Rotación de Neumáticos
                </h1>
                <p className="text-muted-foreground">
                    Selecciona un vehículo, luego haz clic en el neumático de origen y la posición de destino.
                </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
                {/* Sidebar */}
                <div className="lg:col-span-1 space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>Vehículo</CardTitle>
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
                                        <SelectItem key={v.id} value={v.id}>{v.placa}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </CardContent>
                    </Card>

                    {sourceTire && (
                        <Card className="border-blue-500 bg-blue-50">
                            <CardHeader>
                                <CardTitle className="text-blue-700 text-sm">Origen</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <p className="font-bold">Posición {sourceTire.posicion.numero_posicion}</p>
                                <p className="text-xs text-blue-600">Selecciona destino en el esquema</p>
                            </CardContent>
                        </Card>
                    )}
                </div>

                {/* Schematic */}
                <div className="lg:col-span-3">
                    {selectedVehicleId ? (
                        loadingDetails ? (
                            <div className="flex justify-center items-center h-64">
                                <Loader2 className="h-8 w-8 animate-spin" />
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

            {/* Confirmation Dialog */}
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Confirmar Rotación</DialogTitle>
                        <DialogDescription>
                            Mover neumático de <strong>Posición {sourceTire?.posicion?.numero_posicion}</strong> a <strong>Posición {targetPosition?.numero_posicion}</strong>.
                        </DialogDescription>
                    </DialogHeader>

                    <Form {...form}>
                        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                            <FormField
                                control={form.control}
                                name="contador_vehiculo"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Kilometraje Actual</FormLabel>
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

                            <DialogFooter>
                                <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>Cancelar</Button>
                                <Button type="submit" disabled={rotacionMutation.isPending}>
                                    {rotacionMutation.isPending ? 'Procesando...' : 'Confirmar Rotación'}
                                </Button>
                            </DialogFooter>
                        </form>
                    </Form>
                </DialogContent>
            </Dialog>
        </div>
    );
}


