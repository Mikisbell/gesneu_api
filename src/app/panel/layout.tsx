import type { Metadata } from 'next';

export const metadata: Metadata = {
    title: 'Dashboard | GesNeu',
    description: 'Panel de control del Sistema de Gestión de Neumáticos',
};

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
            {children}
        </div>
    );
}
