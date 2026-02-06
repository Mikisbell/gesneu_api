import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { Button } from "@/components/ui/button"
import { LucideIcon } from "lucide-react"
import { ReactNode } from "react"

interface EmptyStateProps {
    icon: ReactNode
    title: string
    description: string
    action?: ReactNode
}

/**
 * EmptyState - Componente homogéneo para estados vacíos
 * Úsalo en TODAS las páginas cuando no haya datos
 */
export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
    return (
        <Card className="border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-12 text-center">
                <div className="rounded-full bg-muted p-3 mb-4">
                    {icon}
                </div>
                <CardTitle className="mb-2">{title}</CardTitle>
                <CardDescription className="mb-6 max-w-sm">
                    {description}
                </CardDescription>
                {action && <div>{action}</div>}
            </CardContent>
        </Card>
    )
}

/**
 * SkeletonTable - Loading state homogéneo para tablas
 * Úsalo en TODAS las DataTables mientras cargan
 */
export function SkeletonTable({ rows = 5 }: { rows?: number }) {
    return (
        <div className="space-y-3">
            {Array.from({ length: rows }).map((_, i) => (
                <div key={i} className="flex items-center space-x-4">
                    <Skeleton className="h-12 w-12 rounded-full" />
                    <div className="space-y-2 flex-1">
                        <Skeleton className="h-4 w-full" />
                        <Skeleton className="h-4 w-3/4" />
                    </div>
                </div>
            ))}
        </div>
    )
}

/**
 * PageHeader - Encabezado homogéneo para todas las páginas
 */
interface PageHeaderProps {
    title: string
    description?: string
    action?: ReactNode
}

export function PageHeader({ title, description, action }: PageHeaderProps) {
    return (
        <div className="flex items-center justify-between mb-6">
            <div>
                <h1 className="text-3xl font-bold tracking-tight">{title}</h1>
                {description && (
                    <p className="text-muted-foreground mt-2">{description}</p>
                )}
            </div>
            {action && <div>{action}</div>}
        </div>
    )
}

/**
 * LoadingButton - Botón con estado de carga homogéneo
 */
interface LoadingButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    loading?: boolean
    loadingText?: string
    children: ReactNode
}

export function LoadingButton({
    loading,
    loadingText,
    children,
    disabled,
    ...props
}: LoadingButtonProps) {
    return (
        <Button disabled={disabled || loading} {...props}>
            {loading && (
                <svg
                    className="animate-spin -ml-1 mr-2 h-4 w-4"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                >
                    <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                    />
                    <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                </svg>
            )}
            {loading ? loadingText || children : children}
        </Button>
    )
}
