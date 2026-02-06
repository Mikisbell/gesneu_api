import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { ReactNode } from "react"

interface ConfirmDialogProps {
    open: boolean
    onOpenChange: (open: boolean) => void
    title: string
    description: string | ReactNode
    confirmText?: string
    cancelText?: string
    onConfirm: () => void
    variant?: "default" | "destructive"
}

/**
 * ConfirmDialog - Reemplazo homogéneo para window.confirm()
 * Úsalo en TODAS las acciones destructivas (delete, desactivar, etc.)
 */
export function ConfirmDialog({
    open,
    onOpenChange,
    title,
    description,
    confirmText = "Confirmar",
    cancelText = "Cancelar",
    onConfirm,
    variant = "default",
}: ConfirmDialogProps) {
    return (
        <AlertDialog open={open} onOpenChange={onOpenChange}>
            <AlertDialogContent>
                <AlertDialogHeader>
                    <AlertDialogTitle>{title}</AlertDialogTitle>
                    <AlertDialogDescription asChild>
                        {typeof description === 'string' ? <p>{description}</p> : description}
                    </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                    <AlertDialogCancel>{cancelText}</AlertDialogCancel>
                    <AlertDialogAction
                        onClick={onConfirm}
                        className={
                            variant === "destructive"
                                ? "bg-destructive text-destructive-foreground hover:bg-destructive/90"
                                : ""
                        }
                    >
                        {confirmText}
                    </AlertDialogAction>
                </AlertDialogFooter>
            </AlertDialogContent>
        </AlertDialog>
    )
}
