import type { NextAuthConfig } from 'next-auth';
import Credentials from 'next-auth/providers/credentials';
import * as bcrypt from 'bcryptjs';
import { prisma } from '@/lib/prisma';

export const authOptions: NextAuthConfig = {
  providers: [
    Credentials({
      name: 'credentials',
      credentials: {
        username: { label: 'Usuario', type: 'text' },
        password: { label: 'Contraseña', type: 'password' }
      },
      async authorize(credentials) {
        if (!credentials?.username || !credentials?.password) {
          throw new Error('Credenciales inválidas');
        }

        const username = credentials.username as string;
        const password = credentials.password as string;

        const usuario = await prisma.usuario.findUnique({
          where: { username },
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

        // Recopilar todos los permisos del usuario
        const permisos: string[] = [];
        const roles: string[] = [];

        usuario.roles.forEach(ur => {
          roles.push(ur.rol.nombre);
          ur.rol.permisos.forEach(rp => {
            if (!permisos.includes(rp.permiso.nombre)) {
              permisos.push(rp.permiso.nombre);
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
