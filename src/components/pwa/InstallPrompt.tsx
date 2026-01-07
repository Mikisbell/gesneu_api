'use client';

import { useState, useEffect } from 'react';
import { Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog';

export function InstallPrompt() {
    const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
    const [showPrompt, setShowPrompt] = useState(false);

    useEffect(() => {
        const handler = (e: any) => {
            e.preventDefault();
            setDeferredPrompt(e);
            // Solo mostrar si no está instalado ya (opcional: guardar en localStorage si el usuario lo rechazó)
            setShowPrompt(true);
        };

        window.addEventListener('beforeinstallprompt', handler);

        return () => {
            window.removeEventListener('beforeinstallprompt', handler);
        };
    }, []);

    const handleInstall = async () => {
        if (!deferredPrompt) return;

        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;

        if (outcome === 'accepted') {
            setDeferredPrompt(null);
            setShowPrompt(false);
        }
    };

    return (
        <Dialog open={showPrompt} onOpenChange={setShowPrompt}>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle className="flex items-center gap-2">
                        <Download className="h-5 w-5 text-blue-600" />
                        Instalar GesNeu App
                    </DialogTitle>
                    <DialogDescription>
                        Instala la aplicación en tu dispositivo para un acceso más rápido y funcionamiento offline en el patio de maniobras.
                    </DialogDescription>
                </DialogHeader>
                <DialogFooter className="flex flex-col sm:flex-row gap-2">
                    <Button type="button" variant="default" onClick={handleInstall} className="flex-1">
                        Instalar
                    </Button>
                    <Button type="button" variant="ghost" onClick={() => setShowPrompt(false)} className="flex-1">
                        Más tarde
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
