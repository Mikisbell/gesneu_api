import type { NextAuthConfig } from 'next-auth';
import Credentials from 'next-auth/providers/credentials';
import * as bcrypt from 'bcryptjs';
import { prisma } from '@/lib/prisma';

export const authOptions: NextAuthConfig = {
  providers: [
    Credentials({
      name: 'credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Contraseña', type: 'password' }
      },
      async authorize(credentials) {
        console.log('🔐 [AUTH] Starting authorization...');
        console.log('🔐 [AUTH] Received credentials:', { email: credentials?.email, hasPassword: !!credentials?.password });

        if (!credentials?.email || !credentials?.password) {
          console.error('❌ [AUTH] Missing credentials');
          throw new Error('Credenciales inválidas');
        }

        const email = credentials.email as string;
        const password = credentials.password as string;

        console.log('🔍 [AUTH] Looking up user:', email);
        const usuario = await prisma.usuario.findUnique({
          where: { email },
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

        if (!usuario) {
          console.error('❌ [AUTH] User not found:', email);
          throw new Error('Usuario no encontrado o inactivo');
        }

        if (!usuario.activo) {
          console.error('❌ [AUTH] User inactive:', email);
          throw new Error('Usuario no encontrado o inactivo');
        }

        console.log('✅ [AUTH] User found:', { username: usuario.username, email: usuario.email, activo: usuario.activo });

        const passwordMatch = await bcrypt.compare(
          password,
          usuario.password_hash
        );

        console.log('🔑 [AUTH] Password match:', passwordMatch);

        if (!passwordMatch) {
          console.error('❌ [AUTH] Password mismatch for:', email);
          throw new Error('Contraseña incorrecta');
        }

        // Recopilar todos los permisos del usuario
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
        console.log('DEBUG: JWT Callback (Login) - User Permissions:', token.permissions);
      } else {
        console.log('DEBUG: JWT Callback (Subsequent) - Token Permissions:', token.permissions);
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.id as string;
        (session.user as any).username = token.username;
        (session.user as any).roles = token.roles;
        (session.user as any).permissions = token.permissions;
        console.log('DEBUG: Session Callback - User Permissions:', (session.user as any).permissions);
      }
      return session;
    }
  },
  secret: process.env.NEXTAUTH_SECRET || 'development-secret-change-in-production'
};
