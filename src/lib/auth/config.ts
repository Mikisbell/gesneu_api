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
          }
        });

        if (!usuario) {
          throw new Error('Usuario no encontrado');
        }

        const passwordMatch = await bcrypt.compare(
          password,
          usuario.password_hash
        );

        if (!passwordMatch) {
          throw new Error('Contraseña incorrecta');
        }

        // Simplified: no roles/permissions in schema
        return {
          id: usuario.id,
          name: usuario.nombre_completo,
          email: usuario.email,
          username: usuario.username,
          roles: ['USER'], // Default role
          permissions: ['*'] // Full access by default
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
