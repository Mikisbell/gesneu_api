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
import { Factory, Loader2 } from 'lucide-react';

interface RecepcionarNeumaticoDialogProps {
    neumaticoId: string;
    numeroSerie: string;
}

export function RecepcionarNeumaticoDialog({ neumaticoId, numeroSerie }: RecepcionarNeumaticoDialogProps) {
    const [open, setOpen] = useState(false);

    // Form State
    const [profundidad, setProfundidad] = useState('18');
    const [costo, setCosto] = useState('');
    const [proveedorId, setProveedorId] = useState(''); // Should match the one sent, but API allows override
    const [almacenId, setAlmacenId] = useState('');

    const queryClient = useQueryClient();

    const { mutate, isPending } = useMutation({
        mutationFn: async () => {
            return await apiClient('/reencauche/retorno', {
                method: 'POST',
                body: JSON.stringify({
                    neumatico_id: neumaticoId,
                    datos_retorno: {
                        profundidad_nueva: Number(profundidad),
                        costo: Number(costo),
                        proveedor_id: proveedorId,
                        almacen_destino_id: almacenId,
                        diseno_banda: "GENERICO" // MVP Default
                    }
                })
            });
        },
        onSuccess: () => {
            toast.success(`Neumático ${numeroSerie} recepcionado correctamente`);
            queryClient.invalidateQueries({ queryKey: ['neumaticos-en-planta'] });
            queryClient.invalidateQueries({ queryKey: ['neumaticos-para-enviar'] });
            queryClient.invalidateQueries({ queryKey: ['indice-reencauchabilidad'] });
            setOpen(false);
        },
        onError: (error: any) => {
            toast.error('Error al recepcionar', {
                description: error.message
            });
        }
    });

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button size="sm" variant="default" className="gap-1 bg-emerald-600 hover:bg-emerald-700">
                    <Factory className="h-4 w-4" /> Recepcionar
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>Recepción de Reencauche</DialogTitle>
                    <DialogDescription>
                        Ingresa los datos técnicos del neumático <strong>{numeroSerie}</strong>.
                    </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="profundidad" className="text-right">
                            Profundidad (mm)
                        </Label>
                        <Input
                            id="profundidad"
                            type="number"
                            className="col-span-3"
                            value={profundidad}
                            onChange={(e) => setProfundidad(e.target.value)}
                        />
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="costo" className="text-right">
                            Costo
                        </Label>
                        <Input
                            id="costo"
                            type="number"
                            className="col-span-3"
                            placeholder="0.00"
                            value={costo}
                            onChange={(e) => setCosto(e.target.value)}
                        />
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="proveedor" className="text-right">
                            Proveedor ID
                        </Label>
                        <Input
                            id="proveedor"
                            className="col-span-3"
                            placeholder="UUID"
                            value={proveedorId}
                            onChange={(e) => setProveedorId(e.target.value)}
                        />
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="almacen" className="text-right">
                            Almacén Destino
                        </Label>
                        <Input
                            id="almacen"
                            className="col-span-3"
                            placeholder="UUID"
                            value={almacenId}
                            onChange={(e) => setAlmacenId(e.target.value)}
                        />
                    </div>
                </div>
                <DialogFooter>
                    <Button variant="outline" onClick={() => setOpen(false)}>Cancelar</Button>
                    <Button
                        onClick={() => mutate()}
                        disabled={isPending || !profundidad || !costo || !proveedorId || !almacenId}
                        className="bg-emerald-600 hover:bg-emerald-700"
                    >
                        {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        Confirmar Retorno
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
