'use client'

import { Sidebar } from '@/components/layout/sidebar'
import { MobileNav } from '@/components/layout/mobile-nav'
import { Header } from '@/components/layout/header'

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <div className="flex h-screen bg-gray-100 dark:bg-gray-900">
            {/* Sidebar para desktop */}
            <aside className="w-64 hidden md:block">
                <Sidebar />
            </aside>

            {/* Main content */}
            <div className="flex-1 flex flex-col overflow-hidden">
                {/* Header móvil y Desktop */}
                <MobileHeader />
                <Header />

                {/* Contenido principal */}
                <main className="flex-1 overflow-y-auto p-4 md:p-8">
                    {children}
                </main>
            </div>
        </div>
    )
}

function MobileHeader() {
    return (
        <header className="md:hidden flex items-center justify-between p-4 bg-white dark:bg-gray-900 border-b">
            <MobileNav />
            <h1 className="text-xl font-bold text-primary">GesNeu</h1>
            <div className="w-10" /> {/* Spacer para centrar logo */}
        </header>
    )
}
