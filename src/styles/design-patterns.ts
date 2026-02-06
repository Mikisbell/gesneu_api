/**
 * 🎨 GesNeu Design System - Guía de Homogeneidad
 * 
 * Este archivo contiene TODOS los patrones que debes seguir
 * para mantener consistencia en toda la aplicación.
 */

// ============================================
// 1. ESTRUCTURA DE PÁGINAS
// ============================================

/**
 * ✅ PATRÓN CORRECTO - Usar en TODAS las páginas
 */
export const CORRECT_PAGE_PATTERN = `
'use client'

import { PageHeader } from '@/components/ui/patterns'
import { EmptyState, SkeletonTable } from '@/components/ui/patterns'
import { useQuery } from '@tanstack/react-query'
import { Plus, Package } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function ExamplePage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['items'],
    queryFn: fetchItems,
  })

  return (
    <div className="space-y-6">
      {/* 1️⃣ Header homogéneo */}
      <PageHeader
        title="Título de la Página"
        description="Descripción opcional"
        action={
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Nuevo Item
          </Button>
        }
      />

      {/* 2️⃣ Loading state homogéneo */}
      {isLoading && <SkeletonTable rows={5} />}

      {/* 3️⃣ Error state homogéneo */}
      {isError && (
        <EmptyState
          icon={<AlertTriangle className="h-4 w-4" />}
          title="Error al cargar datos"
          description="No pudimos conectar con el servidor."
          action={<Button onClick={refetch}>Reintentar</Button>}
        />
      )}

      {/* 4️⃣ Empty state homogéneo */}
      {data?.length === 0 && (
        <EmptyState
          icon={<Package className="h-4 w-4" />}
          title="No hay items registrados"
          description="Comienza agregando tu primer item."
          action={<Button>Agregar Item</Button>}
        />
      )}

      {/* 5️⃣ Data display */}
      {data && data.length > 0 && (
        <DataTable columns={columns} data={data} />
      )}
    </div>
  )
}
`

// ============================================
// 2. FORMULARIOS
// ============================================

export const CORRECT_FORM_PATTERN = `
import { LoadingButton } from '@/components/ui/patterns'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useToast } from '@/components/ui/use-toast'

export function ExampleForm({ initialData, onSuccess }) {
  const { toast } = useToast()
  const queryClient = useQueryClient()

  const form = useForm({
    resolver: zodResolver(schema),
    defaultValues: {
      // valores por defecto
    },
  })

  // Auto-fill cuando editas (SIEMPRE incluir esto)
  useEffect(() => {
    if (initialData) {
      form.reset({
        field1: initialData.field1,
        field2: initialData.field2,
      })
    }
  }, [initialData, form])

  const mutation = useMutation({
    mutationFn: (data) => 
      initialData ? api.update(initialData.id, data) : api.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] })
      toast({
        title: initialData ? "Actualizado" : "Creado",
        description: "La operación se completó exitosamente.",
      })
      form.reset()
      onSuccess?.()
    },
    onError: (error: Error) => {
      toast({
        variant: "destructive",
        title: "Error",
        description: error.message,
      })
    },
  })

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(mutation.mutate)}>
        {/* campos del formulario */}
        
        <LoadingButton
          type="submit"
          loading={mutation.isPending}
          loadingText="Guardando..."
        >
          Guardar
        </LoadingButton>
      </form>
    </Form>
  )
}
`

// ============================================
// 3. ACCIONES DESTRUCTIVAS
// ============================================

export const CORRECT_DELETE_PATTERN = `
import { ConfirmDialog } from '@/components/ui/confirm-dialog'
import { useState } from 'react'

export function DeleteButton({ itemId, itemName }) {
  const [open, setOpen] = useState(false)
  
  const mutation = useMutation({
    mutationFn: () => api.delete(itemId),
    // ✨ Optimistic update
    onMutate: async () => {
      await queryClient.cancelQueries({ queryKey: ['items'] })
      const previous = queryClient.getQueryData(['items'])
      queryClient.setQueryData(['items'], (old) => 
        old.filter(item => item.id !== itemId)
      )
      return { previous }
    },
    onError: (err, variables, context) => {
      queryClient.setQueryData(['items'], context.previous)
    },
  })

  return (
    <>
      <Button 
        variant="destructive" 
        size="sm"
        onClick={() => setOpen(true)}
      >
        Eliminar
      </Button>

      <ConfirmDialog
        open={open}
        onOpenChange={setOpen}
        title="¿Eliminar item?"
        description={
          <>
            Esta acción eliminará permanentemente <strong>{itemName}</strong>.
            Esta acción no se puede deshacer.
          </>
        }
        confirmText="Eliminar"
        cancelText="Cancelar"
        variant="destructive"
        onConfirm={() => {
          mutation.mutate()
          setOpen(false)
        }}
      />
    </>
  )
}
`

// ============================================
// 4. SPACING & LAYOUT
// ============================================

export const SPACING_RULES = {
  // Usar SIEMPRE estas clases para spacing
  pageContainer: "space-y-6",          // Entre secciones principales
  cardContent: "space-y-4",            // Dentro de cards/forms
  formFields: "grid grid-cols-2 gap-4", // Formularios
  buttonGroup: "flex gap-2",           // Grupo de botones

  // Padding estándar
  pagePadding: "p-6",
  cardPadding: "p-4",

  // Margins
  sectionMargin: "mb-6",
  fieldMargin: "mb-4",
}

// ============================================
// 5. COLORES & VARIANTS
// ============================================

export const COLOR_RULES = {
  // Estados
  success: "bg-green-500/10 text-green-700",
  warning: "bg-yellow-500/10 text-yellow-700",
  error: "bg-destructive/10 text-destructive",
  info: "bg-blue-500/10 text-blue-700",

  // Badges
  badgeSuccess: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  badgeWarning: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  badgeError: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
}

// ============================================
// 6. ANIMACIONES
// ============================================

export const ANIMATION_RULES = {
  // Usar SIEMPRE estas clases para animaciones
  fadeIn: "animate-in fade-in duration-200",
  slideUp: "animate-in slide-in-from-bottom-4 duration-300",
  scaleIn: "animate-in zoom-in-95 duration-150",

  // Hover effects
  cardHover: "transition-all hover:shadow-md hover:scale-[1.02]",
  buttonHover: "transition-colors",
}

// ============================================
// 7. ICONOS
// ============================================

export const ICON_RULES = {
  // Tamaños estándar
  small: "h-4 w-4",
  medium: "h-5 w-5",
  large: "h-6 w-6",

  // Con texto
  withText: "mr-2 h-4 w-4",

  // Colores
  muted: "text-muted-foreground",
  primary: "text-primary",
  destructive: "text-destructive",
}

// ============================================
// 8. CHECKLIST DE HOMOGENEIDAD
// ============================================

export const HOMOGENEITY_CHECKLIST = \`
Antes de hacer commit, verifica:

□ Usaste PageHeader para el título
□ Agregaste SkeletonTable para loading
□ Agregaste EmptyState cuando no hay datos
□ Usaste ConfirmDialog en vez de window.confirm
□ Implementaste optimistic updates en DELETE
□ Los botones usan LoadingButton con estado
□ Los iconos usan las clases estándar (h-4 w-4)
□ El spacing usa space-y-6 entre secciones
□ Los forms tienen auto-fill con useEffect
□ Los toasts son consistentes (mismos mensajes)
\`
