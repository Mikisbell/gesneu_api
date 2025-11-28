'use client'

import { useState } from 'react'
import { signIn } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { Loader2 } from 'lucide-react'

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
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useToast } from '@/hooks/use-toast'

const formSchema = z.object({
    email: z.string().email({
        message: "Por favor ingrese un email válido.",
    }),
    password: z.string().min(1, {
        message: "La contraseña es requerida.",
    }),
})

export default function LoginPage() {
    const router = useRouter()
    const { toast } = useToast()
    const [isLoading, setIsLoading] = useState(false)

    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            email: "",
            password: "",
        },
    })

    async function onSubmit(values: z.infer<typeof formSchema>) {
        setIsLoading(true)

        try {
            const result = await signIn('credentials', {
                email: values.email,
                password: values.password,
                redirect: false,
            })

            if (result?.error) {
                toast({
                    variant: "destructive",
                    title: "Error de inicio de sesión",
                    description: "Credenciales inválidas. Por favor verifique.",
                })
            } else {
                toast({
                    title: "Bienvenido",
                    description: "Inicio de sesión exitoso.",
                })
                router.push('/dashboard')
                router.refresh()
            }
        } catch (error) {
            toast({
                variant: "destructive",
                title: "Error",
                description: "Ocurrió un error inesperado.",
            })
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <Card>
            <CardHeader className="space-y-1">
                <CardTitle className="text-2xl text-center">GesNeu</CardTitle>
                <CardDescription className="text-center">
                    Ingrese sus credenciales para acceder al sistema
                </CardDescription>
            </CardHeader>
            <CardContent>
                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                        <FormField
                            control={form.control}
                            name="email"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Email</FormLabel>
                                    <FormControl>
                                        <Input placeholder="usuario@gesneu.com" {...field} />
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
                                        <Input type="password" placeholder="••••••••" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <Button className="w-full" type="submit" disabled={isLoading}>
                            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                            Ingresar
                        </Button>
                    </form>
                </Form>
            </CardContent>
        </Card>
    )
}
