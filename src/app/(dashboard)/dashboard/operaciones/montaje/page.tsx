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
import { Truck, Wrench, CheckCircle, ArrowRight, ArrowLeft } from 'lucide-react';

// Wizard steps
type Step = 1 | 2 | 3 | 4;

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
    const [currentStep, setCurrentStep] = useState<Step>(1);

    const form = useForm<MontajeForm>({
        resolver: zodResolver(montajeSchema),
        defaultValues: {
            kilometraje_vehiculo: 0,
            profundidad_mm: 10,
            presion_psi: 100,
            observaciones: '',
        },
    });

    // Fetch available vehicles
    const { data: vehiculos, isLoading: loadingVehiculos } = useQuery({
        queryKey: ['vehiculos'],
        queryFn: () => apiClient<any[]>('/api/v1/vehiculos'),
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
            router.push('/dashboard/neumaticos');
        },
        onError: (error: any) => {
            toast({
                title: '❌ Error en Montaje',
                description: error.message || 'No se pudo completar el montaje',
                variant: 'destructive',
            });
        },
    });

    const handleNext = () => {
        if (currentStep < 4) setCurrentStep((currentStep + 1) as Step);
    };

    const handleBack = () => {
        if (currentStep > 1) setCurrentStep((currentStep - 1) as Step);
    };

    const onSubmit = (data: MontajeForm) => {
        montajeMutation.mutate(data);
    };

    const selectedVehiculo = vehiculos?.find((v: any) => v.id === form.watch('vehiculo_id'));
    const selectedNeumatico = neumaticos?.find((n: any) => n.id === form.watch('neumatico_id'));

    return (
        <div className="container mx-auto py-8 max-w-4xl">
            <div className="mb-8">
                <h1 className="text-3xl font-bold mb-2">Montaje de Neumático</h1>
                <p className="text-muted-foreground">Asigna un neumático a un vehículo en 4 pasos simples</p>
            </div>

            {/* Progress Steps */}
            <div className="flex items-center justify-between mb-8">
                {[1, 2, 3, 4].map((step) => (
                    <div key={step} className="flex items-center flex-1">
                        <div
                            className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${currentStep >= step
                                ? 'bg-primary text-primary-foreground border-primary'
                                : 'bg-background text-muted-foreground border-muted'
                                }`}
                        >
                            {step}
                        </div>
                        {step < 4 && (
                            <div
                                className={`flex-1 h-1 mx-2 ${currentStep > step ? 'bg-primary' : 'bg-muted'}`}
                            />
                        )}
                    </div>
                ))}
            </div>

            <form onSubmit={form.handleSubmit(onSubmit)}>
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            {currentStep === 1 && <><Truck className="w-5 h-5" /> Paso 1: Seleccionar Vehículo</>}
                            {currentStep === 2 && <><Wrench className="w-5 h-5" /> Paso 2: Seleccionar Neumático</>}
                            {currentStep === 3 && <><Wrench className="w-5 h-5" /> Paso 3: Datos de Montaje</>}
                            {currentStep === 4 && <><CheckCircle className="w-5 h-5" /> Paso 4: Confirmar</>}
                        </CardTitle>
                        <CardDescription>
                            {currentStep === 1 && 'Selecciona el vehículo donde se montará el neumático'}
                            {currentStep === 2 && 'Selecciona el neumático disponible en stock'}
                            {currentStep === 3 && 'Ingresa los datos de medición y kilometraje'}
                            {currentStep === 4 && 'Revisa la información y confirma el montaje'}
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {/* Step 1: Select Vehicle */}
                        {currentStep === 1 && (
                            <div className="space-y-4">
                                <Label>Vehículo</Label>
                                {loadingVehiculos ? (
                                    <p className="text-sm text-muted-foreground">Cargando vehículos...</p>
                                ) : (
                                    <select
                                        {...form.register('vehiculo_id')}
                                        className="w-full p-2 border rounded-md"
                                    >
                                        <option value="">Selecciona un vehículo</option>
                                        {vehiculos?.map((vehiculo: any) => (
                                            <option key={vehiculo.id} value={vehiculo.id}>
                                                {vehiculo.placa} - {vehiculo.marca} {vehiculo.modelo}
                                            </option>
                                        ))}
                                    </select>
                                )}
                                {form.formState.errors.vehiculo_id && (
                                    <p className="text-sm text-destructive">{form.formState.errors.vehiculo_id.message}</p>
                                )}
                            </div>
                        )}

                        {/* Step 2: Select Tire */}
                        {currentStep === 2 && (
                            <div className="space-y-4">
                                <Label>Neumático (EN_STOCK)</Label>
                                {loadingNeumaticos ? (
                                    <p className="text-sm text-muted-foreground">Cargando neumáticos...</p>
                                ) : (
                                    <select
                                        {...form.register('neumatico_id')}
                                        className="w-full p-2 border rounded-md"
                                    >
                                        <option value="">Selecciona un neumático</option>
                                        {neumaticos?.map((neumatico: any) => (
                                            <option key={neumatico.id} value={neumatico.id}>
                                                {neumatico.numero_serie} - {neumatico.modelo?.nombre} ({neumatico.modelo?.medida})
                                            </option>
                                        ))}
                                    </select>
                                )}
                                {form.formState.errors.neumatico_id && (
                                    <p className="text-sm text-destructive">{form.formState.errors.neumatico_id.message}</p>
                                )}
                            </div>
                        )}

                        {/* Step 3: Measurement Data */}
                        {currentStep === 3 && (
                            <div className="grid gap-4">
                                <div>
                                    <Label htmlFor="kilometraje_vehiculo">Kilometraje del Vehículo</Label>
                                    <Input
                                        id="kilometraje_vehiculo"
                                        type="number"
                                        {...form.register('kilometraje_vehiculo')}
                                        placeholder="150000"
                                    />
                                    {form.formState.errors.kilometraje_vehiculo && (
                                        <p className="text-sm text-destructive">{form.formState.errors.kilometraje_vehiculo.message}</p>
                                    )}
                                </div>
                                <div>
                                    <Label htmlFor="profundidad_mm">Profundidad (mm)</Label>
                                    <Input
                                        id="profundidad_mm"
                                        type="number"
                                        step="0.1"
                                        {...form.register('profundidad_mm')}
                                        placeholder="15.5"
                                    />
                                    {form.formState.errors.profundidad_mm && (
                                        <p className="text-sm text-destructive">{form.formState.errors.profundidad_mm.message}</p>
                                    )}
                                </div>
                                <div>
                                    <Label htmlFor="presion_psi">Presión (PSI)</Label>
                                    <Input
                                        id="presion_psi"
                                        type="number"
                                        {...form.register('presion_psi')}
                                        placeholder="110"
                                    />
                                    {form.formState.errors.presion_psi && (
                                        <p className="text-sm text-destructive">{form.formState.errors.presion_psi.message}</p>
                                    )}
                                </div>
                                <div>
                                    <Label htmlFor="observaciones">Observaciones (opcional)</Label>
                                    <Textarea
                                        id="observaciones"
                                        {...form.register('observaciones')}
                                        placeholder="Notas adicionales sobre el montaje..."
                                        rows={3}
                                    />
                                </div>
                            </div>
                        )}

                        {/* Step 4: Confirmation */}
                        {currentStep === 4 && (
                            <div className="space-y-4">
                                <div className="bg-muted p-4 rounded-md space-y-2">
                                    <h3 className="font-semibold">Resumen del Montaje</h3>
                                    <div className="grid grid-cols-2 gap-2 text-sm">
                                        <div className="text-muted-foreground">Vehículo:</div>
                                        <div className="font-medium">
                                            {selectedVehiculo?.placa} - {selectedVehiculo?.marca} {selectedVehiculo?.modelo}
                                        </div>
                                        <div className="text-muted-foreground">Neumático:</div>
                                        <div className="font-medium">{selectedNeumatico?.numero_serie}</div>
                                        <div className="text-muted-foreground">Kilometraje:</div>
                                        <div className="font-medium">{form.watch('kilometraje_vehiculo')} km</div>
                                        <div className="text-muted-foreground">Profundidad:</div>
                                        <div className="font-medium">{form.watch('profundidad_mm')} mm</div>
                                        <div className="text-muted-foreground">Presión:</div>
                                        <div className="font-medium">{form.watch('presion_psi')} PSI</div>
                                    </div>
                                    {form.watch('observaciones') && (
                                        <>
                                            <div className="text-sm text-muted-foreground mt-2">Observaciones:</div>
                                            <div className="text-sm">{form.watch('observaciones')}</div>
                                        </>
                                    )}
                                </div>
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Navigation Buttons */}
                <div className="flex justify-between mt-6">
                    <Button
                        type="button"
                        variant="outline"
                        onClick={handleBack}
                        disabled={currentStep === 1}
                    >
                        <ArrowLeft className="w-4 h-4 mr-2" />
                        Atrás
                    </Button>
                    {currentStep < 4 ? (
                        <Button
                            type="button"
                            onClick={handleNext}
                            disabled={
                                (currentStep === 1 && !form.watch('vehiculo_id')) ||
                                (currentStep === 2 && !form.watch('neumatico_id'))
                            }
                        >
                            Siguiente
                            <ArrowRight className="w-4 h-4 ml-2" />
                        </Button>
                    ) : (
                        <Button type="submit" disabled={montajeMutation.isPending}>
                            {montajeMutation.isPending ? 'Montando...' : 'Confirmar Montaje'}
                            <CheckCircle className="w-4 h-4 ml-2" />
                        </Button>
                    )}
                </div>
            </form>
        </div>
    );
}
