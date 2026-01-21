
import NextAuth from 'next-auth';
import Credentials from 'next-auth/providers/credentials';
import * as bcrypt from 'bcryptjs';
import { prisma } from '@/lib/prisma';
import { SYSTEM_ROLES } from './permissions';
import { authOptions } from './config';

export const { handlers, auth, signIn, signOut } = NextAuth({
    ...authOptions,
    providers: [
        Credentials({
            name: 'credentials',
            credentials: {
                identifier: { label: 'Email o Usuario', type: 'text' },
                password: { label: 'Contraseña', type: 'password' }
            },
            async authorize(credentials) {
                console.log('[Auth] Authorize called with:', credentials?.identifier);
                if (!credentials?.identifier || !credentials?.password) {
                    throw new Error('Credenciales inválidas');
                }

                const identifier = credentials.identifier as string;
                const password = credentials.password as string;

                // Buscar usuario (sin include porque rol está en la tabla misma)
                const usuario = await prisma.usuario.findFirst({
                    where: {
                        OR: [
                            { email: identifier },
                            { username: identifier }
                        ]
                    }
                });

                if (!usuario || !usuario.activo) {
                    return null;
                }

                const passwordMatch = await bcrypt.compare(
                    password,
                    usuario.password_hash
                );

                if (!passwordMatch) {
                    return null;
                }

                // Obtener permisos basados en el ENUM del rol usando SYSTEM_ROLES
                const roleDefinition = SYSTEM_ROLES[usuario.rol as keyof typeof SYSTEM_ROLES];
                const permisos = roleDefinition ? roleDefinition.permisos : [];
                const roleName = roleDefinition ? roleDefinition.nombre : usuario.rol;

                return {
                    id: usuario.id,
                    name: usuario.nombre_completo,
                    email: usuario.email,
                    username: usuario.username,
                    empresa_id: usuario.empresa_id,
                    roles: [roleName],
                    permissions: permisos
                };
            }
        })
    ]
});
