// src/lib/auth/config.ts
import { NextAuthOptions } from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'
import { PrismaAdapter } from '@next-auth/prisma-adapter'
import { prisma } from '@/lib/prisma'
import { compare } from 'bcryptjs'
import type { AuthUser } from '@/lib/types/api'

export const authOptions: NextAuthOptions = {
  adapter: PrismaAdapter(prisma),
  providers: [
    CredentialsProvider({
      name: 'credentials',
      credentials: {
        username: { label: 'Username', type: 'text' },
        password: { label: 'Password', type: 'password' }
      },
      async authorize(credentials) {
        if (!credentials?.username || !credentials?.password) {
          return null
        }

        const user = await prisma.usuario.findUnique({
          where: { username: credentials.username },
          include: {
            roles: {
              include: {
                rol: {
                  include: {
                    permisos: {
                      include: {
                        permiso: true
                      }
                    }
                  }
                }
              }
            }
          }
        })

        if (!user || !user.activo) {
          return null
        }

        // Verificar si la cuenta está bloqueada
        if (user.bloqueado_hasta && user.bloqueado_hasta > new Date()) {
          throw new Error('Cuenta temporalmente bloqueada')
        }

        const isPasswordValid = await compare(credentials.password, user.password_hash)
        
        if (!isPasswordValid) {
          // Incrementar intentos fallidos
          await prisma.usuario.update({
            where: { id: user.id },
            data: {
              intentos_login: user.intentos_login + 1,
              bloqueado_hasta: user.intentos_login >= 4 
                ? new Date(Date.now() + 15 * 60 * 1000) // 15 minutos
                : undefined
            }
          })
          return null
        }

        // Reset intentos fallidos y actualizar último login
        await prisma.usuario.update({
          where: { id: user.id },
          data: {
            intentos_login: 0,
            bloqueado_hasta: null,
            ultimo_login: new Date()
          }
        })

        // Registrar login exitoso en auditoría
        await prisma.auditoriaLog.create({
          data: {
            esquema_tabla: 'public',
            nombre_tabla: 'usuarios',
            operacion: 'LOGIN',
            usuario_aplicacion_id: user.id,
            usuario_aplicacion_username: user.username,
            contexto_aplicacion: {
              evento: 'login_exitoso',
              timestamp: new Date().toISOString(),
              ip: 'unknown' // Se puede obtener del request en el middleware
            }
          }
        })

        const authUser: AuthUser = {
          id: user.id,
          username: user.username,
          email: user.email,
          nombre_completo: user.nombre_completo,
          roles: user.roles.map((ur: any) => ({
            id: ur.rol.id,
            nombre: ur.rol.nombre,
            permisos: ur.rol.permisos.map((rp: any) => rp.permiso.codigo)
          })),
          permissions: user.roles.flatMap((ur: any) =>
            ur.rol.permisos.map((rp: any) => rp.permiso.codigo)
          )
        }

        return authUser
      }
    })
  ],
  session: {
    strategy: 'jwt',
    maxAge: 8 * 60 * 60, // 8 horas
  },
  jwt: {
    maxAge: 8 * 60 * 60, // 8 horas
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        const authUser = user as AuthUser
        ;(token as any).sub = authUser.id
        ;(token as any).username = authUser.username
        ;(token as any).roles = authUser.roles
        ;(token as any).permissions = authUser.permissions
      }
      return token
    },
    async session({ session, token }) {
      if (token && session.user) {
        const sUser = session.user as any
        sUser.id = (token as any).sub
        sUser.username = (token as any).username
        sUser.roles = (token as any).roles
        sUser.permissions = (token as any).permissions
      }
      return session
    }
  },
  pages: {
    signIn: '/auth/login',
    error: '/auth/error'
  },
  events: {
    async signOut({ token }) {
      // Registrar logout
      if (token?.sub) {
        await prisma.auditoriaLog.create({
          data: {
            esquema_tabla: 'public',
            nombre_tabla: 'usuarios',
            operacion: 'LOGOUT',
            usuario_aplicacion_id: token.sub as string,
            usuario_aplicacion_username: token.username as string,
            contexto_aplicacion: {
              evento: 'logout',
              timestamp: new Date().toISOString()
            }
          }
        })
      }
    }
  }
}
