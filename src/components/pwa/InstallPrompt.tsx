'use client';

import { useState, useEffect } from 'react';
import { Download, X } from 'lucide-react';
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
        // Check if user dismissed it before
        const isDismissed = localStorage.getItem('install-prompt-dismissed');
        if (isDismissed) return;

        const handler = (e: any) => {
            e.preventDefault();
            setDeferredPrompt(e);
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

    const handleDismiss = () => {
        setShowPrompt(false);
        localStorage.setItem('install-prompt-dismissed', 'true');
    };

    if (!showPrompt) return null;

    return (
        <div className="fixed top-0 left-0 right-0 z-50 bg-slate-900 text-white px-4 py-3 shadow-lg flex items-center justify-between animate-in slide-in-from-top duration-300">
            <div className="flex items-center gap-3">
                <div className="bg-white/10 p-2 rounded-full">
                    <Download className="h-4 w-4 text-sky-400" />
                </div>
                <div>
                    <p className="text-sm font-medium">Instalar GesNeu App</p>
                    <p className="text-xs text-slate-400">Acceso rápido y modo offline</p>
                </div>
            </div>
            <div className="flex items-center gap-3">
                <Button
                    size="sm"
                    variant="outline"
                    className="h-8 bg-transparent border-slate-600 text-white hover:bg-white/10 hover:text-white"
                    onClick={handleInstall}
                >
                    Instalar
                </Button>
                <Button
                    size="sm"
                    variant="ghost"
                    className="h-8 w-8 p-0 text-slate-400 hover:text-white hover:bg-transparent"
                    onClick={handleDismiss}
                >
                    <X className="h-4 w-4" />
                </Button>
            </div>
        </div>
    );
}
