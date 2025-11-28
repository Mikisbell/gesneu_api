import type { NextAuthConfig } from 'next-auth';
import Credentials from 'next-auth/providers/credentials';
import * as bcrypt from 'bcryptjs';
import { prisma } from '@/lib/prisma';

export const authOptions: NextAuthConfig = {
  providers: [
    Credentials({
      name: 'credentials',
      credentials: {
        identifier: { label: 'Email o Usuario', type: 'text' },
        password: { label: 'Contraseña', type: 'password' }
      },
      async authorize(credentials) {
        if (!credentials?.identifier || !credentials?.password) {
          throw new Error('Credenciales inválidas');
        }

        const identifier = credentials.identifier as string;
        const password = credentials.password as string;

        // Try to find user by email or username
        const usuario = await prisma.usuario.findFirst({
          where: {
            OR: [
              { email: identifier },
              { username: identifier }
            ]
          },
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
        });

        if (!usuario || !usuario.activo) {
          throw new Error('Usuario no encontrado o inactivo');
        }

        const passwordMatch = await bcrypt.compare(
          password,
          usuario.password_hash
        );

        if (!passwordMatch) {
          throw new Error('Contraseña incorrecta');
        }

        // Collect all user permissions
        const permisos: string[] = [];
        const roles: string[] = [];

        usuario.roles.forEach((ur: any) => {
          roles.push(ur.rol.nombre);
          ur.rol.permisos.forEach((rp: any) => {
            if (!permisos.includes(rp.permiso.codigo)) {
              permisos.push(rp.permiso.codigo);
            }
          });
        });

        return {
          id: usuario.id,
          name: usuario.nombre_completo,
          email: usuario.email,
          username: usuario.username,
          roles,
          permissions: permisos
        };
      }
    })
  ],
  pages: {
    signIn: '/login',
    error: '/login'
  },
  session: {
    strategy: 'jwt',
    maxAge: 30 * 24 * 60 * 60 // 30 días
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
        token.username = (user as any).username;
        token.roles = (user as any).roles;
        token.permissions = (user as any).permissions;
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.id as string;
        (session.user as any).username = token.username;
        (session.user as any).roles = token.roles;
        (session.user as any).permissions = token.permissions;
      }
      return session;
    }
  },
  secret: process.env.NEXTAUTH_SECRET || 'development-secret-change-in-production'
};
