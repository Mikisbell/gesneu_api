'use client'

import { useState, Suspense } from 'react'
import { signIn } from 'next-auth/react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { Loader2, Eye, EyeOff, Truck } from 'lucide-react'

import { Button } from '@/components/ui/button'
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card'
import { useToast } from '@/components/ui/use-toast'

const formSchema = z.object({
    identifier: z.string().min(1, {
        message: "Por favor ingrese su email o usuario.",
    }),
    password: z.string().min(1, {
        message: "La contraseña es requerida.",
    }),
})

function LoginForm() {
    const router = useRouter()
    const searchParams = useSearchParams()
    const { toast } = useToast()
    const [isLoading, setIsLoading] = useState(false)
    const [showPassword, setShowPassword] = useState(false)

    const callbackUrl = searchParams.get('callbackUrl') || '/dashboard'

    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            identifier: "",
            password: "",
        },
    })

    async function onSubmit(values: z.infer<typeof formSchema>) {
        setIsLoading(true)

        try {
            const result = await signIn('credentials', {
                identifier: values.identifier,
                password: values.password,
                redirect: false,
                callbackUrl,
            })

            if (result?.error) {
                console.error('❌ Login error:', result.error)

                // Detailed error message for debugging
                let errorTitle = "Error de inicio de sesión";
                let errorDescription = result.error;

                if (result.error.includes('Credenciales')) {
                    errorDescription = "Email o contraseña incorrectos. Verifica tus credenciales.";
                } else if (result.error.includes('Usuario no encontrado')) {
                    errorDescription = "No existe una cuenta con este email.";
                } else if (result.error.includes('inactivo')) {
                    errorDescription = "Tu cuenta está inactiva. Contacta al administrador.";
                } else if (result.error.includes('Contraseña incorrecta')) {
                    errorDescription = "Contraseña incorrecta. Intenta nuevamente.";
                } else if (result.error === 'CredentialsSignin') {
                    errorTitle = "Error de Autenticación";
                    errorDescription = `Verifica tus credenciales. Si el problema persiste en Vercel, revisa las variables de entorno (NEXTAUTH_URL, NEXTAUTH_SECRET, DATABASE_URL).`;
                }

                toast({
                    variant: "destructive",
                    title: errorTitle,
                    description: errorDescription,
                })
            } else if (result?.ok) {
                toast({
                    title: "¡Bienvenido!",
                    description: "Iniciando sesión...",
                })
                router.push(callbackUrl)
                router.refresh()
            } else {
                toast({
                    variant: "destructive",
                    title: "Error de Configuración",
                    description: "No se pudo conectar con el servidor de autenticación. Si estás en Vercel, verifica: NEXTAUTH_URL debe ser https://gesneu.vercel.app",
                })
            }
        } catch (error) {
            console.error('💥 Login exception:', error)
            toast({
                variant: "destructive",
                title: "Error del Sistema",
                description: `Error: ${error instanceof Error ? error.message : 'Desconocido'}. Verifica la conexión a la base de datos (DATABASE_URL en Vercel).`,
            })
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <Card className="w-full max-w-md shadow-xl border-none">
            <CardHeader className="space-y-2 text-center pb-8">
                <div className="flex justify-center mb-4">
                    <div className="h-12 w-12 bg-primary/10 rounded-full flex items-center justify-center">
                        <Truck className="h-6 w-6 text-primary" />
                    </div>
                </div>
                <CardTitle className="text-2xl font-bold tracking-tight">Bienvenido a GesNeu</CardTitle>
                <CardDescription className="text-base">
                    Ingrese sus credenciales para continuar
                </CardDescription>
            </CardHeader>
            <CardContent>
                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                        <FormField
                            control={form.control}
                            name="identifier"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Email o Usuario</FormLabel>
                                    <FormControl>
                                        <Input
                                            placeholder="admin@gesneu.com"
                                            className="h-11"
                                            {...field}
                                        />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <FormField
                            control={form.control}
                            name="password"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Contraseña</FormLabel>
                                    <FormControl>
                                        <div className="relative">
                                            <Input
                                                type={showPassword ? "text" : "password"}
                                                placeholder="••••••••"
                                                className="h-11 pr-10"
                                                {...field}
                                            />
                                            <Button
                                                type="button"
                                                variant="ghost"
                                                size="sm"
                                                className="absolute right-0 top-0 h-11 w-11 px-3 hover:bg-transparent"
                                                onClick={() => setShowPassword(!showPassword)}
                                            >
                                                {showPassword ? (
                                                    <EyeOff className="h-4 w-4 text-muted-foreground" />
                                                ) : (
                                                    <Eye className="h-4 w-4 text-muted-foreground" />
                                                )}
                                                <span className="sr-only">
                                                    {showPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
                                                </span>
                                            </Button>
                                        </div>
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <Button className="w-full h-11 text-base" type="submit" disabled={isLoading}>
                            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                            Iniciar Sesión
                        </Button>
                    </form>
                </Form>
            </CardContent>
            <CardFooter className="flex justify-center pb-8">
                <p className="text-sm text-muted-foreground">
                    ¿Olvidó su contraseña? <a href="#" className="text-primary hover:underline font-medium">Recuperar acceso</a>
                </p>
            </CardFooter>
        </Card>
    )
}

export default function LoginPage() {
    return (
        <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-900 p-4">
            <Suspense fallback={<div className="flex items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>}>
                <LoginForm />
            </Suspense>
        </div>
    )
}
