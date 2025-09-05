import Link from 'next/link'
import { 
  ClipboardDocumentListIcon, 
  WrenchScrewdriverIcon, 
  EyeIcon,
  ChartBarIcon 
} from '@heroicons/react/24/outline'

export default function HomePage() {
  const operatorActions = [
    {
      title: 'Inspección de Neumáticos',
      description: 'Registrar mediciones de profundidad y estado visual',
      icon: EyeIcon,
      href: '/inspeccion',
      color: 'bg-blue-500',
      urgent: false
    },
    {
      title: 'Montaje/Desmontaje',
      description: 'Registrar cambios de posición y reemplazos',
      icon: WrenchScrewdriverIcon,
      href: '/montaje',
      color: 'bg-green-500',
      urgent: false
    },
    {
      title: 'Eventos Rápidos',
      description: 'Registro rápido de incidentes y observaciones',
      icon: ClipboardDocumentListIcon,
      href: '/eventos',
      color: 'bg-orange-500',
      urgent: true
    },
    {
      title: 'Estado de Flota',
      description: 'Vista general del estado de neumáticos',
      icon: ChartBarIcon,
      href: '/estado',
      color: 'bg-purple-500',
      urgent: false
    }
  ]

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Panel del Operador
        </h2>
        <p className="text-gray-600">
          Selecciona una acción para registrar datos en campo
        </p>
      </div>

      {/* Acciones Principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {operatorActions.map((action) => (
          <Link
            key={action.href}
            href={action.href}
            className="group relative"
          >
            <div className="card p-6 hover:shadow-lg transition-shadow duration-200 h-full">
              {action.urgent && (
                <div className="absolute -top-2 -right-2 w-4 h-4 bg-red-500 rounded-full animate-pulse"></div>
              )}
              
              <div className="flex items-center mb-4">
                <div className={`${action.color} p-3 rounded-lg`}>
                  <action.icon className="w-6 h-6 text-white" />
                </div>
              </div>
              
              <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-primary-600 transition-colors">
                {action.title}
              </h3>
              
              <p className="text-gray-600 text-sm">
                {action.description}
              </p>
            </div>
          </Link>
        ))}
      </div>

      {/* Estadísticas Rápidas */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Inspecciones Hoy</p>
              <p className="text-2xl font-bold text-gray-900">12</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <EyeIcon className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Cambios Realizados</p>
              <p className="text-2xl font-bold text-gray-900">3</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <WrenchScrewdriverIcon className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Eventos Registrados</p>
              <p className="text-2xl font-bold text-gray-900">7</p>
            </div>
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
              <ClipboardDocumentListIcon className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Alertas Importantes */}
      <div className="mt-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Alertas Importantes
        </h3>
        
        <div className="space-y-3">
          <div className="card p-4 border-l-4 border-red-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-900">Neumático crítico detectado</p>
                <p className="text-sm text-gray-600">Vehículo ABC-123 - Posición delantera izquierda</p>
              </div>
              <span className="status-danger">Crítico</span>
            </div>
          </div>

          <div className="card p-4 border-l-4 border-yellow-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-900">Inspección pendiente</p>
                <p className="text-sm text-gray-600">Vehículo DEF-456 - Programada para hoy</p>
              </div>
              <span className="status-warning">Pendiente</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
