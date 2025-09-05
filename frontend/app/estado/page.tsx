'use client'

import { useState, useEffect } from 'react'
import { 
  ChartBarIcon, 
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  EyeIcon,
  TruckIcon
} from '@heroicons/react/24/outline'

interface NeumaticoEstado {
  id: string
  numero_serie: string
  vehiculo_placa: string
  posicion_nombre: string
  profundidad_mm: number
  kilometraje_acumulado: number
  vida_util_restante_km?: number
  prediccion_fecha_reemplazo?: string
  confianza_prediccion?: number
  estado_actual: string
  dias_hasta_reemplazo?: number
}

export default function EstadoPage() {
  const [neumaticos, setNeumaticos] = useState<NeumaticoEstado[]>([])
  const [filtroEstado, setFiltroEstado] = useState('TODOS')
  const [loading, setLoading] = useState(true)
  const [estadisticas, setEstadisticas] = useState({
    total: 0,
    criticos: 0,
    atencion: 0,
    buenos: 0,
    con_prediccion: 0
  })

  useEffect(() => {
    cargarDatos()
  }, [])

  const cargarDatos = async () => {
    try {
      // Cargar neumáticos con información completa
      const response = await fetch('/api/v1/neumaticos/?include_predictions=true&limit=100')
      const data = await response.json()
      
      // Procesar datos para el estado
      const neumaticosProcesados = data.map((neumatico: any) => {
        const diasHastaReemplazo = neumatico.prediccion_fecha_reemplazo 
          ? Math.ceil((new Date(neumatico.prediccion_fecha_reemplazo).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))
          : null

        return {
          id: neumatico.id,
          numero_serie: neumatico.numero_serie,
          vehiculo_placa: neumatico.vehiculo?.placa || 'Sin asignar',
          posicion_nombre: neumatico.posicion?.nombre || 'Almacén',
          profundidad_mm: neumatico.profundidad_remanente_actual_mm || 0,
          kilometraje_acumulado: neumatico.kilometraje_acumulado || 0,
          vida_util_restante_km: neumatico.vida_util_restante_km,
          prediccion_fecha_reemplazo: neumatico.prediccion_fecha_reemplazo,
          confianza_prediccion: neumatico.confianza_prediccion,
          estado_actual: neumatico.estado_actual,
          dias_hasta_reemplazo: diasHastaReemplazo
        }
      })

      setNeumaticos(neumaticosProcesados)
      
      // Calcular estadísticas
      const stats = {
        total: neumaticosProcesados.length,
        criticos: neumaticosProcesados.filter(n => getEstadoSalud(n) === 'CRITICO').length,
        atencion: neumaticosProcesados.filter(n => getEstadoSalud(n) === 'ATENCION').length,
        buenos: neumaticosProcesados.filter(n => getEstadoSalud(n) === 'BUENO').length,
        con_prediccion: neumaticosProcesados.filter(n => n.vida_util_restante_km).length
      }
      
      setEstadisticas(stats)
      
    } catch (error) {
      console.error('Error cargando datos:', error)
    } finally {
      setLoading(false)
    }
  }

  const getEstadoSalud = (neumatico: NeumaticoEstado) => {
    // Criterios para determinar estado de salud
    if (neumatico.profundidad_mm < 2 || 
        (neumatico.dias_hasta_reemplazo && neumatico.dias_hasta_reemplazo < 30) ||
        (neumatico.vida_util_restante_km && neumatico.vida_util_restante_km < 5000)) {
      return 'CRITICO'
    }
    
    if (neumatico.profundidad_mm < 4 || 
        (neumatico.dias_hasta_reemplazo && neumatico.dias_hasta_reemplazo < 90) ||
        (neumatico.vida_util_restante_km && neumatico.vida_util_restante_km < 15000)) {
      return 'ATENCION'
    }
    
    return 'BUENO'
  }

  const getEstadoColor = (estado: string) => {
    const colors = {
      'CRITICO': 'bg-red-100 text-red-800 border-red-200',
      'ATENCION': 'bg-yellow-100 text-yellow-800 border-yellow-200',
      'BUENO': 'bg-green-100 text-green-800 border-green-200'
    }
    return colors[estado] || 'bg-gray-100 text-gray-800 border-gray-200'
  }

  const getEstadoIcon = (estado: string) => {
    const icons = {
      'CRITICO': ExclamationTriangleIcon,
      'ATENCION': ClockIcon,
      'BUENO': CheckCircleIcon
    }
    return icons[estado] || CheckCircleIcon
  }

  const neumaticosFiltered = neumaticos.filter(neumatico => {
    if (filtroEstado === 'TODOS') return true
    return getEstadoSalud(neumatico) === filtroEstado
  })

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando estado de la flota...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Estado de la Flota
        </h2>
        <p className="text-gray-600">
          Vista general del estado de todos los neumáticos con predicciones IA
        </p>
      </div>

      {/* Estadísticas Generales */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
        <div className="card p-6 text-center">
          <TruckIcon className="w-8 h-8 text-gray-600 mx-auto mb-2" />
          <p className="text-2xl font-bold text-gray-900">{estadisticas.total}</p>
          <p className="text-sm text-gray-600">Total Neumáticos</p>
        </div>

        <div className="card p-6 text-center border-l-4 border-red-500">
          <ExclamationTriangleIcon className="w-8 h-8 text-red-600 mx-auto mb-2" />
          <p className="text-2xl font-bold text-red-600">{estadisticas.criticos}</p>
          <p className="text-sm text-gray-600">Críticos</p>
        </div>

        <div className="card p-6 text-center border-l-4 border-yellow-500">
          <ClockIcon className="w-8 h-8 text-yellow-600 mx-auto mb-2" />
          <p className="text-2xl font-bold text-yellow-600">{estadisticas.atencion}</p>
          <p className="text-sm text-gray-600">Requieren Atención</p>
        </div>

        <div className="card p-6 text-center border-l-4 border-green-500">
          <CheckCircleIcon className="w-8 h-8 text-green-600 mx-auto mb-2" />
          <p className="text-2xl font-bold text-green-600">{estadisticas.buenos}</p>
          <p className="text-sm text-gray-600">En Buen Estado</p>
        </div>

        <div className="card p-6 text-center border-l-4 border-blue-500">
          <ChartBarIcon className="w-8 h-8 text-blue-600 mx-auto mb-2" />
          <p className="text-2xl font-bold text-blue-600">{estadisticas.con_prediccion}</p>
          <p className="text-sm text-gray-600">Con Predicción IA</p>
        </div>
      </div>

      {/* Filtros */}
      <div className="card p-4 mb-6">
        <div className="flex flex-wrap gap-2">
          <span className="text-sm font-medium text-gray-700 py-2">Filtrar por estado:</span>
          {[
            { value: 'TODOS', label: 'Todos', count: estadisticas.total },
            { value: 'CRITICO', label: 'Críticos', count: estadisticas.criticos },
            { value: 'ATENCION', label: 'Atención', count: estadisticas.atencion },
            { value: 'BUENO', label: 'Buenos', count: estadisticas.buenos }
          ].map((filtro) => (
            <button
              key={filtro.value}
              onClick={() => setFiltroEstado(filtro.value)}
              className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                filtroEstado === filtro.value
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {filtro.label} ({filtro.count})
            </button>
          ))}
        </div>
      </div>

      {/* Tabla de Neumáticos */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Neumático
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Ubicación
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Profundidad
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Kilometraje
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Predicción IA
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Acción
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {neumaticosFiltered.map((neumatico) => {
                const estadoSalud = getEstadoSalud(neumatico)
                const IconComponent = getEstadoIcon(estadoSalud)
                
                return (
                  <tr key={neumatico.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <IconComponent className="w-5 h-5 mr-2" />
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full border ${getEstadoColor(estadoSalud)}`}>
                          {estadoSalud}
                        </span>
                      </div>
                    </td>
                    
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {neumatico.numero_serie}
                        </div>
                        <div className="text-sm text-gray-500">
                          {neumatico.estado_actual}
                        </div>
                      </div>
                    </td>
                    
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {neumatico.vehiculo_placa}
                        </div>
                        <div className="text-sm text-gray-500">
                          {neumatico.posicion_nombre}
                        </div>
                      </div>
                    </td>
                    
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {neumatico.profundidad_mm} mm
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                        <div 
                          className={`h-2 rounded-full ${
                            neumatico.profundidad_mm < 2 ? 'bg-red-500' :
                            neumatico.profundidad_mm < 4 ? 'bg-yellow-500' : 'bg-green-500'
                          }`}
                          style={{ width: `${Math.min((neumatico.profundidad_mm / 16) * 100, 100)}%` }}
                        ></div>
                      </div>
                    </td>
                    
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {neumatico.kilometraje_acumulado.toLocaleString()} km
                    </td>
                    
                    <td className="px-6 py-4 whitespace-nowrap">
                      {neumatico.vida_util_restante_km ? (
                        <div>
                          <div className="text-sm font-medium text-blue-600">
                            {neumatico.vida_util_restante_km.toLocaleString()} km
                          </div>
                          {neumatico.dias_hasta_reemplazo && (
                            <div className="text-xs text-gray-500">
                              {neumatico.dias_hasta_reemplazo > 0 
                                ? `${neumatico.dias_hasta_reemplazo} días`
                                : 'Vencido'
                              }
                            </div>
                          )}
                          {neumatico.confianza_prediccion && (
                            <div className="text-xs text-gray-500">
                              Conf: {Math.round(neumatico.confianza_prediccion * 100)}%
                            </div>
                          )}
                        </div>
                      ) : (
                        <span className="text-sm text-gray-400">Sin predicción</span>
                      )}
                    </td>
                    
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex space-x-2">
                        <button className="text-blue-600 hover:text-blue-900">
                          <EyeIcon className="w-4 h-4" />
                        </button>
                        {estadoSalud === 'CRITICO' && (
                          <button className="text-red-600 hover:text-red-900 text-xs px-2 py-1 bg-red-100 rounded">
                            Urgente
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
        
        {neumaticosFiltered.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-500">No hay neumáticos que coincidan con el filtro seleccionado</p>
          </div>
        )}
      </div>

      {/* Resumen de Acciones Recomendadas */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <ExclamationTriangleIcon className="w-5 h-5 text-red-600 mr-2" />
            Acciones Inmediatas
          </h3>
          
          <div className="space-y-3">
            {neumaticos
              .filter(n => getEstadoSalud(n) === 'CRITICO')
              .slice(0, 5)
              .map((neumatico) => (
                <div key={neumatico.id} className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {neumatico.vehiculo_placa} - {neumatico.posicion_nombre}
                    </p>
                    <p className="text-xs text-gray-600">
                      Profundidad: {neumatico.profundidad_mm}mm
                    </p>
                  </div>
                  <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded">
                    Cambiar ya
                  </span>
                </div>
              ))}
            
            {estadisticas.criticos === 0 && (
              <p className="text-sm text-gray-500 text-center py-4">
                ✅ No hay neumáticos críticos
              </p>
            )}
          </div>
        </div>

        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <ClockIcon className="w-5 h-5 text-yellow-600 mr-2" />
            Planificar Mantenimiento
          </h3>
          
          <div className="space-y-3">
            {neumaticos
              .filter(n => getEstadoSalud(n) === 'ATENCION')
              .slice(0, 5)
              .map((neumatico) => (
                <div key={neumatico.id} className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {neumatico.vehiculo_placa} - {neumatico.posicion_nombre}
                    </p>
                    <p className="text-xs text-gray-600">
                      {neumatico.dias_hasta_reemplazo 
                        ? `${neumatico.dias_hasta_reemplazo} días restantes`
                        : `${neumatico.profundidad_mm}mm profundidad`
                      }
                    </p>
                  </div>
                  <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                    Monitorear
                  </span>
                </div>
              ))}
            
            {estadisticas.atencion === 0 && (
              <p className="text-sm text-gray-500 text-center py-4">
                ✅ No hay neumáticos que requieran atención inmediata
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
