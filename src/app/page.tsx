import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Truck, Shield, MapPin, Clock, CheckCircle, ArrowRight } from 'lucide-react'

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Navbar */}
      <header className="border-b bg-white dark:bg-gray-900 sticky top-0 z-50">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Truck className="h-8 w-8 text-primary" />
            <span className="text-2xl font-bold tracking-tight">GesNeu Logistics</span>
          </div>
          <nav className="hidden md:flex gap-6">
            <Link href="#servicios" className="text-sm font-medium hover:text-primary transition-colors">
              Servicios
            </Link>
            <Link href="#tecnologia" className="text-sm font-medium hover:text-primary transition-colors">
              Tecnología
            </Link>
            <Link href="#nosotros" className="text-sm font-medium hover:text-primary transition-colors">
              Nosotros
            </Link>
          </nav>
          <div className="flex gap-4">
            <Link href="/login">
              <Button>Iniciar Sesión</Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative bg-slate-900 text-white py-24 lg:py-32 overflow-hidden">
        <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075&auto=format&fit=crop')] bg-cover bg-center opacity-20" />
        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-3xl space-y-6">
            <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight leading-tight">
              Transporte de Minerales Seguro y Eficiente
            </h1>
            <p className="text-xl text-slate-300 max-w-2xl">
              Soluciones logísticas de alta gama para la industria minera. Flota moderna, conductores certificados y monitoreo en tiempo real para garantizar su carga.
            </p>
            <div className="flex gap-4 pt-4">
              <Link href="/login">
                <Button size="lg" className="text-lg px-8">
                  Acceder a la Plataforma <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
              <Button size="lg" variant="outline" className="text-lg px-8 bg-transparent text-white border-white hover:bg-white hover:text-slate-900">
                Contactar Ventas
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="servicios" className="py-20 bg-gray-50 dark:bg-gray-800">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-3xl font-bold mb-4">Excelencia en Logística Minera</h2>
            <p className="text-muted-foreground text-lg">
              Combinamos experiencia, tecnología y los más altos estándares de seguridad para mover su negocio.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <Card className="border-none shadow-lg">
              <CardHeader>
                <Truck className="h-12 w-12 text-primary mb-4" />
                <CardTitle>Flota de Alta Gama</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Camiones modernos equipados con la última tecnología en seguridad y rendimiento. Mantenimiento predictivo para garantizar disponibilidad 24/7.
                </p>
              </CardContent>
            </Card>

            <Card className="border-none shadow-lg">
              <CardHeader>
                <Shield className="h-12 w-12 text-primary mb-4" />
                <CardTitle>Seguridad Garantizada</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Protocolos estrictos, conductores certificados y escolta satelital. Su carga está asegurada y protegida en cada kilómetro del trayecto.
                </p>
              </CardContent>
            </Card>

            <Card className="border-none shadow-lg">
              <CardHeader>
                <MapPin className="h-12 w-12 text-primary mb-4" />
                <CardTitle>Tracking en Tiempo Real</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Visibilidad total de su operación. Monitoree la ubicación, estado y tiempos de entrega de su carga desde nuestra plataforma digital exclusiva.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Stats/Trust Section */}
      <section className="py-20 bg-white dark:bg-gray-900">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="space-y-6">
              <h2 className="text-3xl font-bold">¿Por qué elegir GesNeu Logistics?</h2>
              <div className="space-y-4">
                <div className="flex gap-4">
                  <CheckCircle className="h-6 w-6 text-green-500 flex-shrink-0" />
                  <div>
                    <h3 className="font-semibold">Conductores Elite</h3>
                    <p className="text-muted-foreground">Personal altamente capacitado y evaluado constantemente.</p>
                  </div>
                </div>
                <div className="flex gap-4">
                  <CheckCircle className="h-6 w-6 text-green-500 flex-shrink-0" />
                  <div>
                    <h3 className="font-semibold">Puntualidad Record</h3>
                    <p className="text-muted-foreground">98% de entregas a tiempo en rutas de alta complejidad.</p>
                  </div>
                </div>
                <div className="flex gap-4">
                  <CheckCircle className="h-6 w-6 text-green-500 flex-shrink-0" />
                  <div>
                    <h3 className="font-semibold">Soporte 24/7</h3>
                    <p className="text-muted-foreground">Centro de control activo todo el día, todos los días.</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="bg-slate-100 dark:bg-slate-800 rounded-2xl p-8 grid grid-cols-2 gap-8">
              <div className="text-center">
                <div className="text-4xl font-bold text-primary mb-2">+500</div>
                <div className="text-sm text-muted-foreground">Camiones Activos</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold text-primary mb-2">10k</div>
                <div className="text-sm text-muted-foreground">Viajes Completados</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold text-primary mb-2">0%</div>
                <div className="text-sm text-muted-foreground">Incidentes Críticos</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold text-primary mb-2">24h</div>
                <div className="text-sm text-muted-foreground">Monitoreo</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 text-slate-300 py-12 mt-auto">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div className="col-span-2">
              <div className="flex items-center gap-2 mb-4 text-white">
                <Truck className="h-6 w-6" />
                <span className="text-xl font-bold">GesNeu Logistics</span>
              </div>
              <p className="max-w-sm">
                Líderes en transporte de minerales y carga pesada. Comprometidos con la seguridad, la eficiencia y la innovación tecnológica.
              </p>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Enlaces Rápidos</h4>
              <ul className="space-y-2">
                <li><Link href="#" className="hover:text-white transition-colors">Inicio</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Servicios</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Cobertura</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Portal Conductores</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Contacto</h4>
              <ul className="space-y-2">
                <li className="flex items-center gap-2"><MapPin className="h-4 w-4" /> Lima, Perú</li>
                <li className="flex items-center gap-2"><Clock className="h-4 w-4" /> Lun - Dom: 24 Horas</li>
                <li>contacto@gesneu.com</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-slate-800 pt-8 text-center text-sm">
            © 2024 GesNeu Logistics. Todos los derechos reservados.
          </div>
        </div>
      </footer>
    </div>
  )
}
