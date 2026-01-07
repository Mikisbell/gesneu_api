'use client';

import { WifiOff } from "lucide-react";

export default function OfflinePage() {
    return (
        <div className="flex min-h-screen flex-col items-center justify-center bg-gray-100 p-4 text-center dark:bg-gray-900">
            <div className="mb-6 rounded-full bg-red-100 p-6 dark:bg-red-900/30">
                <WifiOff className="h-12 w-12 text-red-600 dark:text-red-400" />
            </div>
            <h1 className="mb-2 text-2xl font-bold text-gray-900 dark:text-white">
                Sin Conexión
            </h1>
            <p className="mb-8 max-w-md text-gray-600 dark:text-gray-300">
                Parece que has perdido la conexión a internet. Algunas funciones pueden no
                estar disponibles hasta que te reconectes.
            </p>
            <button
                onClick={() => window.location.reload()}
                className="rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-medium text-white transition-colors hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-300 dark:focus:ring-blue-800"
            >
                Reintentar conexión
            </button>
        </div>
    );
}
