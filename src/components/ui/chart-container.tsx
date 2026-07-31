'use client';

import { useIsClient } from '@/hooks/use-is-client';
import { cn } from '@/lib/utils';

interface ChartContainerProps {
    children: React.ReactNode;
    /** Alto del contenedor. Default: h-[300px] */
    className?: string;
    /** Placeholder mientras hidrata el cliente */
    fallback?: React.ReactNode;
}

/**
 * Wrapper para charts de Recharts que previene el warning:
 * "The width(-1) and height(-1) of chart should be greater than 0"
 *
 * El warning ocurre porque ResponsiveContainer usa ResizeObserver que no
 * existe en SSR (Next.js). Este componente retarda el render del chart
 * hasta que el cliente esté completamente hidratado.
 */
export function ChartContainer({
    children,
    className,
    fallback,
}: ChartContainerProps) {
    const isClient = useIsClient();

    if (!isClient) {
        return (
            <div
                className={cn('flex items-center justify-center bg-muted/20 rounded-md', className)}
                aria-hidden="true"
            >
                {fallback ?? (
                    <div className="flex flex-col items-center gap-2 text-muted-foreground">
                        <div className="h-8 w-8 animate-spin rounded-full border-2 border-muted-foreground/30 border-t-muted-foreground" />
                        <span className="text-xs">Cargando gráfico…</span>
                    </div>
                )}
            </div>
        );
    }

    return <div className={className}>{children}</div>;
}
