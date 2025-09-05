import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'GesNeu - Gestión de Neumáticos',
  description: 'Sistema de gestión de neumáticos con IA predictiva',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es">
      <body className="bg-gray-50 min-h-screen">
        <div className="min-h-screen flex flex-col">
          <header className="bg-white shadow-sm border-b border-gray-200">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between items-center py-4">
                <div className="flex items-center">
                  <h1 className="text-2xl font-bold text-gray-900">GesNeu</h1>
                  <span className="ml-2 text-sm text-gray-500">Operador</span>
                </div>
                <div className="flex items-center space-x-4">
                  <span className="text-sm text-gray-600">Usuario: Operador</span>
                  <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm font-medium">O</span>
                  </div>
                </div>
              </div>
            </div>
          </header>
          
          <main className="flex-1">
            {children}
          </main>
          
          <footer className="bg-white border-t border-gray-200 py-4">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <p className="text-center text-sm text-gray-500">
                GesNeu v1.3.0 - Sprint 4 MVP Operador
              </p>
            </div>
          </footer>
        </div>
      </body>
    </html>
  )
}
