import { useEffect, useState } from 'react';

/**
 * Retorna `true` una vez que el componente se ha hidratado en el cliente.
 * Útil para evitar renderizar componentes que dependen del DOM (como charts de Recharts)
 * durante el SSR de Next.js, lo cual genera warnings de width(-1) / height(-1).
 */
export function useIsClient(): boolean {
    const [isClient, setIsClient] = useState(false);

    useEffect(() => {
        setIsClient(true);
    }, []);

    return isClient;
}
