'use client';

import { useState } from 'react';
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
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Plus } from 'lucide-react';
import { toast } from 'sonner';
import { createWebhook } from '@/lib/actions/webhook.actions';
import { WebhookEventType } from '@prisma/client';
// UI Components
import { Checkbox } from '@/components/ui/checkbox';

const EVENT_OPTIONS = Object.values(WebhookEventType);

export function WebhookDialog() {
    const [open, setOpen] = useState(false);
    const [loading, setLoading] = useState(false);

    // Form states
    const [nombre, setNombre] = useState('');
    const [url, setUrl] = useState('');
    const [selectedEvents, setSelectedEvents] = useState<WebhookEventType[]>([]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (selectedEvents.length === 0) {
            toast.error('Selecciona al menos un evento');
            return;
        }

        try {
            setLoading(true);
            await createWebhook({
                nombre,
                url,
                eventos: selectedEvents,
            });
            toast.success('Webhook creado correctamente');
            setOpen(false);
            setNombre('');
            setUrl('');
            setSelectedEvents([]);
        } catch (error) {
            toast.error('Error al crear webhook');
        } finally {
            setLoading(false);
        }
    };

    const toggleEvent = (event: WebhookEventType) => {
        setSelectedEvents((prev) =>
            prev.includes(event)
                ? prev.filter((e) => e !== event)
                : [...prev, event]
        );
    };

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button>
                    <Plus className="mr-2 h-4 w-4" /> Nuevo Webhook
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[500px]">
                <DialogHeader>
                    <DialogTitle>Crear Integración Webhook</DialogTitle>
                    <DialogDescription>
                        Configura un endpoint para recibir notificaciones en tiempo real.
                    </DialogDescription>
                </DialogHeader>
                <form onSubmit={handleSubmit} className="space-y-4 py-4">
                    <div className="space-y-2">
                        <Label htmlFor="nombre">Nombre</Label>
                        <Input
                            id="nombre"
                            placeholder="Ej: Notificar SAP"
                            value={nombre}
                            onChange={(e) => setNombre(e.target.value)}
                            required
                        />
                    </div>
                    <div className="space-y-2">
                        <Label htmlFor="url">URL Endpoint (POST)</Label>
                        <Input
                            id="url"
                            placeholder="https://api.tu-erp.com/webhooks/gesneu"
                            value={url}
                            onChange={(e) => setUrl(e.target.value)}
                            type="url"
                            required
                        />
                    </div>
                    <div className="space-y-2">
                        <Label>Eventos a Suscribir</Label>
                        <div className="grid grid-cols-2 gap-2 border rounded-md p-3">
                            {EVENT_OPTIONS.map((event) => (
                                <div key={event} className="flex items-center space-x-2">
                                    <Checkbox
                                        id={event}
                                        checked={selectedEvents.includes(event)}
                                        onCheckedChange={() => toggleEvent(event)}
                                    />
                                    <Label htmlFor={event} className="text-xs font-mono cursor-pointer">
                                        {event}
                                    </Label>
                                </div>
                            ))}
                        </div>
                    </div>
                    <DialogFooter>
                        <Button type="submit" disabled={loading}>
                            {loading ? 'Guardando...' : 'Crear Webhook'}
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}
