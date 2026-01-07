'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { CreateInspeccionSchema, CreateInspeccionDTO } from '@/lib/validators/inspeccion.validator';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import { Gauge, Save, Loader2 } from 'lucide-react';

interface InspectionModalProps {
    neumaticoId: string;
    serial: string;
    isOpen: boolean;
    onClose: () => void;
    onSuccess?: () => void;
}

export function InspectionModal({ neumaticoId, serial, isOpen, onClose, onSuccess }: InspectionModalProps) {
    const [isSubmitting, setIsSubmitting] = useState(false);
    const { toast } = useToast();

    const form = useForm<CreateInspeccionDTO>({
        resolver: zodResolver(CreateInspeccionSchema),
        defaultValues: {
            neumatico_id: neumaticoId,
            presion_psi: undefined,
            observaciones: ''
        }
    });

    const onSubmit = async (data: CreateInspeccionDTO) => {
        setIsSubmitting(true);
        try {
            const response = await fetch('/api/v1/inspecciones', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });

            if (!response.ok) throw new Error('Error al registrar inspección');

            toast({
                title: 'Inspección Registrada',
                description: `Lectura guardada para neumático ${serial}`,
                variant: 'default',
            });
            form.reset();
            onSuccess?.();
            onClose();
        } catch (error) {
            toast({
                title: 'Error',
                description: 'No se pudo guardar la lectura. Intente nuevamente.',
                variant: 'destructive',
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="sm:max-w-md">
                <DialogHeader>
                    <DialogTitle className="flex items-center gap-2 text-xl">
                        <Gauge className="h-6 w-6 text-blue-600" />
                        Inspección Manual
                    </DialogTitle>
                    <DialogDescription>
                        Registrando presión para <strong>{serial}</strong>
                    </DialogDescription>
                </DialogHeader>

                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6 py-4">
                    <div className="space-y-4">
                        <div className="grid gap-2">
                            <Label htmlFor="presion" className="text-lg">Presión (PSI)</Label>
                            <Input
                                id="presion"
                                type="number"
                                step="0.1"
                                placeholder="0.0"
                                className="h-14 text-2xl font-bold text-center"
                                autoFocus
                                {...form.register('presion_psi', { valueAsNumber: true })}
                            />
                            {form.formState.errors.presion_psi && (
                                <p className="text-sm text-red-500">{form.formState.errors.presion_psi.message}</p>
                            )}
                        </div>

                        <div className="grid gap-2">
                            <Label htmlFor="obs">Observaciones (Opcional)</Label>
                            <Input
                                id="obs"
                                placeholder="Ej: Válvula con fuga leve..."
                                {...form.register('observaciones')}
                            />
                        </div>
                    </div>

                    <DialogFooter>
                        <Button type="button" variant="outline" onClick={onClose} className="w-full sm:w-auto">
                            Cancelar
                        </Button>
                        <Button type="submit" disabled={isSubmitting} className="w-full sm:w-auto bg-blue-600 hover:bg-blue-700">
                            {isSubmitting ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Guardando...
                                </>
                            ) : (
                                <>
                                    <Save className="mr-2 h-4 w-4" />
                                    Guardar Lectura
                                </>
                            )}
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}
