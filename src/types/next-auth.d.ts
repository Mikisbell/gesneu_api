import 'next-auth';
import { DefaultSession, DefaultUser } from 'next-auth';
import { JWT, DefaultJWT } from 'next-auth/jwt';

declare module 'next-auth' {
    interface Session extends DefaultSession {
        user: {
            id: string;
            username: string;
            empresa_id: string | undefined;
            rol: string;
            roles: string[];
            permissions: string[];
        } & DefaultSession['user'];
        expires: string; // ISO 8601 date string
    }

    interface User extends DefaultUser {
        id: string;
        username: string;
        empresa_id: string;
        rol: string;
        roles: string[];
        permissions: string[];
    }
}

declare module 'next-auth/jwt' {
    interface JWT extends DefaultJWT {
        id: string;
        username: string;
        empresa_id: string;
        rol: string;
        roles: string[];
        permissions: string[];
    }
}
