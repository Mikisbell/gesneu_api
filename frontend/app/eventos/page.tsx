'use client'

import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { 
  ClipboardDocumentListIcon, 
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  FireIcon
} from '@heroicons/react/24/outline'

// Schema de validación
const eventoSchema = z.object({
  tipo_evento: z.enum(['INCIDENTE', 'OBSERVACION', 'ALERTA', 'MANTENIMIENTO_URGENTE']),
  vehiculo_id: z.string().min(1, 'Selecciona un vehículo'),
  posicion_id: z.string().optional(),
  prioridad: z.enum(['BAJA', 'MEDIA', 'ALTA', 'CRITICA']),
  descripcion: z.string().min(10, 'Descripción debe tener al menos 10 caracteres'),
  observaciones: z.string().optional(),
  requiere_accion_inmediata: z.boolean().default(false)
})

type EventoForm = z.infer<typeof eventoSchema>

export default function EventosPage() {
  const [vehiculos, setVehiculos] = useState([])
  const [posiciones, setPosiciones] = useState([])
  const [eventosRecientes, setEventosRecientes] = useState([])
  const [loading, setLoading] = useState(false)

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors, isSubmitting }
  } = useForm<EventoForm>({
    resolver: zodResolver(eventoSchema),
    defaultValues: {
      requiere_accion_inmediata: false
    }
  })

  const vehiculoSeleccionado = watch('vehiculo_id')
  const tipoEvento = watch('tipo_evento')
  const prioridad = watch('prioridad')

  // Cargar datos iniciales
  useEffect(() => {
    Promise.all([
      fetch('/api/v1/vehiculos/').then(res => res.json()),
      fetch('/api/v1/vehiculos/posiciones-neumatico').then(res => res.json()),
      fetch('/api/v1/eventos/?limit=10').then(res => res.json())
    ]).then(([vehiculosData, posicionesData, eventosData]) => {
      setVehiculos(vehiculosData)
      setPosiciones(posicionesData)
      setEventosRecientes(eventosData.data || eventosData)
    }).catch(console.error)
  }, [])

  const onSubmit = async (data: EventoForm) => {
    try {
      setLoading(true)

      // Buscar neumático en la posición si se especificó
      let neumatico_id = null
      if (data.posicion_id) {
        const neumaticoResponse = await fetch(
          `/api/v1/neumaticos/?vehiculo_id=${data.vehiculo_id}&posicion_id=${data.posicion_id}`
        )
        const neumaticos = await neumaticoResponse.json()
        if (neumaticos.length > 0) {
          neumatico_id = neumaticos[0].id
        }
      }

      // Registrar evento
      const eventoData = {
        neumatico_id,
        vehiculo_id: data.vehiculo_id,
        tipo_evento: data.tipo_evento,
        descripcion: data.descripcion,
        observaciones: data.observaciones,
        prioridad: data.prioridad,
        datos_adicionales: {
          posicion_id: data.posicion_id,
          requiere_accion_inmediata: data.requiere_accion_inmediata,
          registrado_por: 'operador_campo'
        }
      }

      const response = await fetch('/api/v1/eventos/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(eventoData)
      })

      if (!response.ok) throw new Error('Error al registrar evento')

      // Si es crítico y hay neumático, disparar predicción IA
      if (data.prioridad === 'CRITICA' && neumatico_id) {
        try {
          await fetch('/api/v1/ml/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ neumatico_id })
          })
        } catch (error) {
          console.warn('Predicción IA no disponible:', error)
        }
      }

      // Mostrar éxito y limpiar formulario
      alert('Evento registrado exitosamente')
      reset()
      
      // Recargar eventos recientes
      const eventosResponse = await fetch('/api/v1/eventos/?limit=10')
      const eventosData = await eventosResponse.json()
      setEventosRecientes(eventosData.data || eventosData)

    } catch (error) {
      console.error('Error:', error)
      alert('Error al registrar evento')
    } finally {
      setLoading(false)
    }
  }

  const getPrioridadColor = (prioridad: string) => {
    const colors = {
      'BAJA': 'text-gray-600 bg-gray-100',
      'MEDIA': 'text-blue-600 bg-blue-100',
      'ALTA': 'text-orange-600 bg-orange-100',
      'CRITICA': 'text-red-600 bg-red-100'
    }
    return colors[prioridad] || 'text-gray-600 bg-gray-100'
  }

  const getTipoIcon = (tipo: string) => {
    const icons = {
      'INCIDENTE': ExclamationTriangleIcon,
      'OBSERVACION': ClipboardDocumentListIcon,
      'ALERTA': FireIcon,
      'MANTENIMIENTO_URGENTE': ClockIcon
    }
    return icons[tipo] || ClipboardDocumentListIcon
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Registro de Eventos Rápidos
        </h2>
        <p className="text-gray-600">
          Registra incidentes, observaciones y alertas en tiempo real
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Formulario de Registro */}
        <div className="lg:col-span-2">
          <form onSubmit={handleSubmit(onSubmit)} className="card p-6 space-y-6">
            {/* Tipo de Evento */}
            <div>
              <label className="form-label">Tipo de Evento</label>
              <div className="grid grid-cols-2 gap-4">
                {[
                  { value: 'INCIDENTE', label: 'Incidente', icon: '⚠️', color: 'border-red-500' },
                  { value: 'OBSERVACION', label: 'Observación', icon: '👁️', color: 'border-blue-500' },
                  { value: 'ALERTA', label: 'Alerta', icon: '🚨', color: 'border-orange-500' },
                  { value: 'MANTENIMIENTO_URGENTE', label: 'Mant. Urgente', icon: '🔧', color: 'border-purple-500' }
                ].map((tipo) => (
                  <label key={tipo.value} className="cursor-pointer">
                    <input
                      type="radio"
                      {...register('tipo_evento')}
                      value={tipo.value}
                      className="sr-only"
                    />
                    <div className={`border-2 rounded-lg p-3 text-center transition-colors ${
                      tipoEvento === tipo.value 
                        ? `${tipo.color} bg-opacity-10` 
                        : 'border-gray-200 hover:border-gray-300'
                    }`}>
                      <div className="text-xl mb-1">{tipo.icon}</div>
                      <div className="text-sm font-medium">{tipo.label}</div>
                    </div>
                  </label>
                ))}
              </div>
              {errors.tipo_evento && (
                <p className="text-red-600 text-sm mt-1">{errors.tipo_evento.message}</p>
              )}
            </div>

            {/* Prioridad */}
            <div>
              <label className="form-label">Prioridad</label>
              <div className="grid grid-cols-4 gap-2">
                {[
                  { value: 'BAJA', label: 'Baja', color: 'border-gray-400' },
                  { value: 'MEDIA', label: 'Media', color: 'border-blue-400' },
                  { value: 'ALTA', label: 'Alta', color: 'border-orange-400' },
                  { value: 'CRITICA', label: 'Crítica', color: 'border-red-500' }
                ].map((prio) => (
                  <label key={prio.value} className="cursor-pointer">
                    <input
                      type="radio"
                      {...register('prioridad')}
                      value={prio.value}
                      className="sr-only"
                    />
                    <div className={`border-2 rounded-lg p-2 text-center transition-colors text-sm ${
                      prioridad === prio.value 
                        ? `${prio.color} bg-opacity-10` 
                        : 'border-gray-200 hover:border-gray-300'
                    }`}>
                      {prio.label}
                    </div>
                  </label>
                ))}
              </div>
              {errors.prioridad && (
                <p className="text-red-600 text-sm mt-1">{errors.prioridad.message}</p>
              )}
            </div>

            {/* Ubicación */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="form-label">Vehículo</label>
                <select {...register('vehiculo_id')} className="form-input">
                  <option value="">Seleccionar vehículo...</option>
                  {vehiculos.map((vehiculo: any) => (
                    <option key={vehiculo.id} value={vehiculo.id}>
                      {vehiculo.placa} - {vehiculo.marca}
                    </option>
                  ))}
                </select>
                {errors.vehiculo_id && (
                  <p className="text-red-600 text-sm mt-1">{errors.vehiculo_id.message}</p>
                )}
              </div>

              <div>
                <label className="form-label">Posición (Opcional)</label>
                <select {...register('posicion_id')} className="form-input">
                  <option value="">Sin posición específica</option>
                  {posiciones.map((posicion: any) => (
                    <option key={posicion.id} value={posicion.id}>
                      {posicion.nombre} ({posicion.eje})
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Descripción */}
            <div>
              <label className="form-label">Descripción del Evento</label>
              <textarea
                {...register('descripcion')}
                rows={3}
                className="form-input"
                placeholder="Describe qué sucedió de manera clara y concisa..."
              />
              {errors.descripcion && (
                <p className="text-red-600 text-sm mt-1">{errors.descripcion.message}</p>
              )}
            </div>

            {/* Observaciones */}
            <div>
              <label className="form-label">Observaciones Adicionales</label>
              <textarea
                {...register('observaciones')}
                rows={2}
                className="form-input"
                placeholder="Detalles adicionales, contexto, condiciones ambientales..."
              />
            </div>

            {/* Acción Inmediata */}
            <div className="flex items-center">
              <input
                type="checkbox"
                {...register('requiere_accion_inmediata')}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label className="ml-2 block text-sm text-gray-900">
                Requiere acción inmediata
              </label>
            </div>

            {/* Botones */}
            <div className="flex space-x-4">
              <button
                type="submit"
                disabled={isSubmitting || loading}
                className={`flex-1 ${
                  prioridad === 'CRITICA' ? 'btn-danger' : 'btn-primary'
                }`}
              >
                {isSubmitting ? 'Registrando...' : 'Registrar Evento'}
              </button>
              
              <button
                type="button"
                className="btn-secondary"
                onClick={() => reset()}
              >
                Limpiar
              </button>
            </div>
          </form>
        </div>

        {/* Panel de Eventos Recientes */}
        <div className="space-y-6">
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Eventos Recientes
            </h3>
            
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {eventosRecientes.length > 0 ? (
                eventosRecientes.map((evento: any, index) => {
                  const IconComponent = getTipoIcon(evento.tipo_evento)
                  return (
                    <div key={index} className="border rounded-lg p-3">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center">
                          <IconComponent className="w-4 h-4 text-gray-600 mr-2" />
                          <span className="text-sm font-medium">
                            {evento.tipo_evento}
                          </span>
                        </div>
                        <span className={`status-badge text-xs ${getPrioridadColor(evento.prioridad)}`}>
                          {evento.prioridad}
                        </span>
                      </div>
                      
                      <p className="text-sm text-gray-700 mb-1">
                        {evento.descripcion}
                      </p>
                      
                      <div className="text-xs text-gray-500">
                        {new Date(evento.fecha_evento || evento.created_at).toLocaleString()}
                      </div>
                    </div>
                  )
                })
              ) : (
                <p className="text-gray-500 text-sm text-center py-4">
                  No hay eventos recientes
                </p>
              )}
            </div>
          </div>

          {/* Guía Rápida */}
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Guía Rápida
            </h3>
            
            <div className="space-y-3 text-sm">
              <div className="flex items-start">
                <ExclamationTriangleIcon className="w-4 h-4 text-red-600 mr-2 mt-0.5" />
                <div>
                  <p className="font-medium">Incidente</p>
                  <p className="text-gray-600">Daños, averías, accidentes</p>
                </div>
              </div>

              <div className="flex items-start">
                <ClipboardDocumentListIcon className="w-4 h-4 text-blue-600 mr-2 mt-0.5" />
                <div>
                  <p className="font-medium">Observación</p>
                  <p className="text-gray-600">Desgaste, comportamiento anormal</p>
                </div>
              </div>

              <div className="flex items-start">
                <FireIcon className="w-4 h-4 text-orange-600 mr-2 mt-0.5" />
                <div>
                  <p className="font-medium">Alerta</p>
                  <p className="text-gray-600">Condiciones de riesgo</p>
                </div>
              </div>

              <div className="flex items-start">
                <ClockIcon className="w-4 h-4 text-purple-600 mr-2 mt-0.5" />
                <div>
                  <p className="font-medium">Mant. Urgente</p>
                  <p className="text-gray-600">Requiere intervención inmediata</p>
                </div>
              </div>
            </div>
          </div>

          {/* Estadísticas del Día */}
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Estadísticas del Día
            </h3>
            
            <div className="grid grid-cols-2 gap-4 text-center">
              <div>
                <p className="text-2xl font-bold text-blue-600">7</p>
                <p className="text-xs text-gray-600">Eventos Total</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-red-600">2</p>
                <p className="text-xs text-gray-600">Críticos</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-orange-600">3</p>
                <p className="text-xs text-gray-600">Alta Prioridad</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-green-600">5</p>
                <p className="text-xs text-gray-600">Resueltos</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
