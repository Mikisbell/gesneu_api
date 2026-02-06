'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { toast } from 'sonner';
import { apiClient } from '@/lib/api/client';
import { Truck, Loader2 } from 'lucide-react';

interface EnviarNeumaticoDialogProps {
    neumaticoId: string;
    numeroSerie: string;
}

export function EnviarNeumaticoDialog({ neumaticoId, numeroSerie }: EnviarNeumaticoDialogProps) {
    const [open, setOpen] = useState(false);
    const [proveedorId, setProveedorId] = useState(''); // TODO: Replace with ComboBox
    const queryClient = useQueryClient();

    const { mutate, isPending } = useMutation({
        mutationFn: async () => {
            return await apiClient('/reencauche/enviar', {
                method: 'POST',
                body: JSON.stringify({
                    neumatico_id: neumaticoId,
                    proveedor_id: proveedorId // Sending mock or manual ID
                })
            });
        },
        onSuccess: () => {
            toast.success(`Neumático ${numeroSerie} enviado a reencauche`);
            queryClient.invalidateQueries({ queryKey: ['neumaticos-para-enviar'] });
            queryClient.invalidateQueries({ queryKey: ['neumaticos-en-planta'] });
            queryClient.invalidateQueries({ queryKey: ['indice-reencauchabilidad'] });
            setOpen(false);
        },
        onError: (error: any) => {
            toast.error('Error al enviar neumático', {
                description: error.message
            });
        }
    });

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button size="sm" variant="outline" className="gap-1">
                    <Truck className="h-4 w-4" /> Enviar
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>Enviar a Reencauche</DialogTitle>
                    <DialogDescription>
                        Selecciona el proveedor para procesar el neumático <strong>{numeroSerie}</strong>.
                    </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="proveedor" className="text-right">
                            Proveedor
                        </Label>
                        {/* Placeholder for Provider Select - Using Input for MVP compatibility */}
                        <Input
                            id="proveedor"
                            className="col-span-3"
                            placeholder="ID del Proveedor (UUID)"
                            value={proveedorId}
                            onChange={(e) => setProveedorId(e.target.value)}
                        />
                    </div>
                </div>
                <DialogFooter>
                    <Button variant="outline" onClick={() => setOpen(false)}>Cancelar</Button>
                    <Button onClick={() => mutate()} disabled={isPending || !proveedorId}>
                        {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        Confirmar Envío
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
