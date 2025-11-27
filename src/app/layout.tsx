import './globals.css'

export const metadata = {
  title: 'GesNeu - Gestión de Neumáticos',
  description: 'Sistema Enterprise de Gestión de Neumáticos',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  )
}
