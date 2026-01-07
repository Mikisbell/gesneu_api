# PARTE 3: PATRONES DE IMPLEMENTACIÓN
## Services + Repositories + Validation

**Fecha:** 14 de Noviembre, 2025  
**Versión:** 1.0  
**Dependencias:** PARTE 1 y 2 completadas

---

## 🏗️ ARCHITECTURE PATTERNS

### **1. Repository Pattern (Data Access Layer)**
```typescript
// src/lib/repositories/base.repository.ts
import { PrismaClient } from '@/generated/prisma'
import { prisma } from '@/lib/prisma'

export abstract class BaseRepository<T, CreateInput, UpdateInput> {
  protected prisma: PrismaClient = prisma
  protected abstract model: any

  async findMany(where?: any, include?: any): Promise<T[]> {
    return this.model.findMany({ where, include })
  }

  async findUnique(where: any, include?: any): Promise<T | null> {
    return this.model.findUnique({ where, include })
  }

  async create(data: CreateInput): Promise<T> {
    return this.model.create({ data })
  }

  async update(where: any, data: UpdateInput): Promise<T> {
    return this.model.update({ where, data })
  }

  async delete(where: any): Promise<T> {
    return this.model.delete({ where })
  }

  async softDelete(where: any): Promise<T> {
    return this.model.update({
      where,
      data: { activo: false, actualizado_en: new Date() }
    })
  }

  async count(where?: any): Promise<number> {
    return this.model.count({ where })
  }
}
```

### **2. Neumatico Repository (Específico)**
```typescript
// src/lib/repositories/neumatico.repository.ts
import { BaseRepository } from './base.repository'
import { Neumatico, Prisma } from '@/generated/prisma'

export class NeumaticoRepository extends BaseRepository<
  Neumatico,
  Prisma.NeumaticoCreateInput,
  Prisma.NeumaticoUpdateInput
> {
  protected model = this.prisma.neumatico

  // Consultas específicas del dominio
  async findByNumeroSerie(numeroSerie: string): Promise<Neumatico | null> {
    return this.model.findUnique({
      where: { numero_serie: numeroSerie },
      include: {
        modelo: {
          include: { fabricante: true }
        },
        ubicacion_almacen: true,
        ubicacion_vehiculo: true,
        ubicacion_posicion: true
      }
    })
  }

  async findInstalados(): Promise<Neumatico[]> {
    return this.model.findMany({
      where: { 
        estado_actual: 'INSTALADO',
        activo: true 
      },
      include: {
        modelo: { include: { fabricante: true } },
        ubicacion_vehiculo: true,
        ubicacion_posicion: true
      }
    })
  }

  async findByAlmacen(almacenId: string): Promise<Neumatico[]> {
    return this.model.findMany({
      where: {
        ubicacion_almacen_id: almacenId,
        estado_actual: 'EN_STOCK',
        activo: true
      },
      include: {
        modelo: { include: { fabricante: true } }
      }
    })
  }

  async findWithHistorial(neumaticoId: string) {
    return this.model.findUnique({
      where: { id: neumaticoId },
      include: {
        modelo: { include: { fabricante: true } },
        eventos: {
          orderBy: { fecha_evento: 'desc' },
          include: {
            vehiculo: true,
            posicion_montaje: true,
            almacen_destino: true
          }
        },
        historial_estados: {
          orderBy: { fecha_cambio: 'desc' }
        },
        mediciones_profundidad: {
          orderBy: { fecha_medicion: 'desc' },
          take: 10
        }
      }
    })
  }

  // Query compleja para dashboard
  async getInventarioResumen() {
    const [total, enStock, instalados, enReparacion, desechados] = await Promise.all([
      this.model.count({ where: { activo: true } }),
      this.model.count({ where: { estado_actual: 'EN_STOCK', activo: true } }),
      this.model.count({ where: { estado_actual: 'INSTALADO', activo: true } }),
      this.model.count({ where: { estado_actual: 'EN_REPARACION', activo: true } }),
      this.model.count({ where: { estado_actual: 'DESECHADO' } })
    ])

    return { total, enStock, instalados, enReparacion, desechados }
  }
}
```

---

## 🔧 SERVICE LAYER PATTERNS

### **1. Base Service Pattern**
```typescript
// src/lib/services/base.service.ts
import { BaseRepository } from '@/lib/repositories/base.repository'

export abstract class BaseService<T, CreateInput, UpdateInput> {
  constructor(protected repository: BaseRepository<T, CreateInput, UpdateInput>) {}

  async findAll(filters?: any): Promise<T[]> {
    return this.repository.findMany(filters)
  }

  async findById(id: string): Promise<T | null> {
    return this.repository.findUnique({ id })
  }

  async create(data: CreateInput, userId?: string): Promise<T> {
    const enrichedData = this.enrichCreateData(data, userId)
    return this.repository.create(enrichedData)
  }

  async update(id: string, data: UpdateInput, userId?: string): Promise<T> {
    const enrichedData = this.enrichUpdateData(data, userId)
    return this.repository.update({ id }, enrichedData)
  }

  async delete(id: string): Promise<T> {
    return this.repository.softDelete({ id })
  }

  protected enrichCreateData(data: any, userId?: string): any {
    return {
      ...data,
      creado_por: userId,
      creado_en: new Date()
    }
  }

  protected enrichUpdateData(data: any, userId?: string): any {
    return {
      ...data,
      actualizado_por: userId,
      actualizado_en: new Date()
    }
  }
}
```

### **2. Neumatico Service (Business Logic)**
```typescript
// src/lib/services/neumatico.service.ts
import { BaseService } from './base.service'
import { NeumaticoRepository } from '@/lib/repositories/neumatico.repository'
import { AlertaService } from './alerta.service'
import { AuditoriaService } from './auditoria.service'
import { Neumatico, EstadoNeumaticoEnum, TipoEventoNeumaticoEnum } from '@/generated/prisma'

export class NeumaticoService extends BaseService<Neumatico, any, any> {
  constructor(
    protected repository: NeumaticoRepository,
    private alertaService: AlertaService,
    private auditoriaService: AuditoriaService
  ) {
    super(repository)
  }

  // Lógica de negocio específica
  async registrarEvento(eventoData: any, userId: string): Promise<{
    neumatico: Neumatico,
    evento: any
  }> {
    const { tipo_evento, neumatico_id } = eventoData

    // Validaciones de negocio
    await this.validarEvento(tipo_evento, neumatico_id, eventoData)

    // Transacción completa
    return this.repository.prisma.$transaction(async (tx) => {
      // 1. Procesar evento según tipo
      const neumatico = await this.procesarEventoPorTipo(
        tipo_evento, 
        neumatico_id, 
        eventoData, 
        tx
      )

      // 2. Crear registro de evento
      const evento = await tx.eventoNeumatico.create({
        data: {
          ...eventoData,
          creado_por: userId,
          creado_en: new Date()
        }
      })

      // 3. Verificar alertas
      await this.alertaService.verificarAlertas(neumatico.id, tx)

      // 4. Auditoría
      await this.auditoriaService.registrarCambio(
        'neumaticos',
        neumatico.id,
        'evento_registrado',
        { tipo_evento, evento_id: evento.id },
        userId,
        tx
      )

      return { neumatico, evento }
    })
  }

  private async procesarEventoPorTipo(
    tipoEvento: TipoEventoNeumaticoEnum,
    neumaticoId: string,
    eventoData: any,
    tx: any
  ): Promise<Neumatico> {
    switch (tipoEvento) {
      case 'INSTALACION':
        return this.procesarInstalacion(neumaticoId, eventoData, tx)
      
      case 'DESMONTAJE':
        return this.procesarDesmontaje(neumaticoId, eventoData, tx)
      
      case 'ROTACION':
        return this.procesarRotacion(neumaticoId, eventoData, tx)
      
      case 'INSPECCION':
        return this.procesarInspeccion(neumaticoId, eventoData, tx)
      
      case 'REENCAUCHE_ENTRADA':
        return this.procesarReencaucheEntrada(neumaticoId, eventoData, tx)
      
      case 'REENCAUCHE_SALIDA':
        return this.procesarReencaucheSalida(neumaticoId, eventoData, tx)
      
      case 'DESECHO':
        return this.procesarDesecho(neumaticoId, eventoData, tx)
      
      default:
        throw new Error(`Tipo de evento no soportado: ${tipoEvento}`)
    }
  }

  private async procesarInstalacion(
    neumaticoId: string,
    eventoData: any,
    tx: any
  ): Promise<Neumatico> {
    const { vehiculo_id, posicion_montaje_id, kilometraje_vehiculo } = eventoData

    // Validar que la posición esté disponible
    await this.validarPosicionDisponible(vehiculo_id, posicion_montaje_id, tx)

    // Actualizar neumático
    return tx.neumatico.update({
      where: { id: neumaticoId },
      data: {
        estado_actual: EstadoNeumaticoEnum.INSTALADO,
        ubicacion_vehiculo_id: vehiculo_id,
        ubicacion_posicion_id: posicion_montaje_id,
        ubicacion_almacen_id: null,
        fecha_instalacion: new Date(),
        km_instalacion: kilometraje_vehiculo,
        actualizado_en: new Date()
      }
    })
  }

  private async procesarDesmontaje(
    neumaticoId: string,
    eventoData: any,
    tx: any
  ): Promise<Neumatico> {
    const { kilometraje_vehiculo, almacen_destino_id, estado_destino } = eventoData

    const neumatico = await tx.neumatico.findUnique({
      where: { id: neumaticoId }
    })

    // Calcular kilometraje acumulado
    const kmRecorridos = kilometraje_vehiculo - (neumatico.km_instalacion || 0)
    const nuevoKmAcumulado = (neumatico.kilometraje_acumulado || 0) + kmRecorridos

    return tx.neumatico.update({
      where: { id: neumaticoId },
      data: {
        estado_actual: estado_destino || EstadoNeumaticoEnum.EN_STOCK,
        ubicacion_vehiculo_id: null,
        ubicacion_posicion_id: null,
        ubicacion_almacen_id: almacen_destino_id,
        kilometraje_acumulado: nuevoKmAcumulado,
        fecha_desmontaje: new Date(),
        actualizado_en: new Date()
      }
    })
  }

  private async procesarReencaucheSalida(
    neumaticoId: string,
    eventoData: any,
    tx: any
  ): Promise<Neumatico> {
    const { profundidad_nueva, almacen_destino_id } = eventoData

    const neumatico = await tx.neumatico.findUnique({
      where: { id: neumaticoId }
    })

    return tx.neumatico.update({
      where: { id: neumaticoId },
      data: {
        estado_actual: EstadoNeumaticoEnum.EN_STOCK,
        ubicacion_almacen_id: almacen_destino_id,
        profundidad_actual_mm: profundidad_nueva,
        profundidad_inicial_mm: profundidad_nueva,
        vida_actual: (neumatico.vida_actual || 1) + 1,
        reencauches_realizados: (neumatico.reencauches_realizados || 0) + 1,
        es_reencauchado: true,
        kilometraje_acumulado: 0, // Reset para nueva vida
        actualizado_en: new Date()
      }
    })
  }

  // Validaciones de negocio
  private async validarEvento(
    tipoEvento: TipoEventoNeumaticoEnum,
    neumaticoId: string,
    eventoData: any
  ): Promise<void> {
    const neumatico = await this.repository.findUnique({ id: neumaticoId })
    
    if (!neumatico) {
      throw new Error('Neumático no encontrado')
    }

    // Validaciones específicas por tipo de evento
    switch (tipoEvento) {
      case 'INSTALACION':
        if (neumatico.estado_actual !== EstadoNeumaticoEnum.EN_STOCK) {
          throw new Error('Solo se pueden instalar neumáticos en stock')
        }
        break

      case 'DESMONTAJE':
        if (neumatico.estado_actual !== EstadoNeumaticoEnum.INSTALADO) {
          throw new Error('Solo se pueden desmontar neumáticos instalados')
        }
        break

      case 'REENCAUCHE_ENTRADA':
        const modelo = await this.repository.prisma.modeloNeumatico.findUnique({
          where: { id: neumatico.modelo_id }
        })
        
        if (neumatico.reencauches_realizados >= (modelo?.reencauches_maximos || 0)) {
          throw new Error('Neumático ha alcanzado el límite de reencauches')
        }
        break
    }
  }

  private async validarPosicionDisponible(
    vehiculoId: string,
    posicionId: string,
    tx: any
  ): Promise<void> {
    const neumaticoEnPosicion = await tx.neumatico.findFirst({
      where: {
        ubicacion_vehiculo_id: vehiculoId,
        ubicacion_posicion_id: posicionId,
        estado_actual: EstadoNeumaticoEnum.INSTALADO,
        activo: true
      }
    })

    if (neumaticoEnPosicion) {
      throw new Error('La posición ya está ocupada por otro neumático')
    }
  }

  // Queries específicas del dominio
  async getHistorialCompleto(neumaticoId: string) {
    return this.repository.findWithHistorial(neumaticoId)
  }

  async getNeumaticosPorVencer(diasAnticipacion: number = 30) {
    const fechaLimite = new Date()
    fechaLimite.setDate(fechaLimite.getDate() + diasAnticipacion)

    return this.repository.prisma.neumatico.findMany({
      where: {
        estado_actual: EstadoNeumaticoEnum.INSTALADO,
        activo: true,
        // Lógica compleja para calcular vencimiento basado en km o tiempo
      },
      include: {
        modelo: { include: { fabricante: true } },
        ubicacion_vehiculo: true,
        ubicacion_posicion: true
      }
    })
  }
}
```

---

## ✅ VALIDATION PATTERNS

### **1. Zod Schemas (Input Validation)**
```typescript
// src/lib/validators/neumatico.schemas.ts
import { z } from 'zod'
import { EstadoNeumaticoEnum, TipoEventoNeumaticoEnum } from '@/generated/prisma'

export const NeumaticoCreateSchema = z.object({
  numero_serie: z.string().min(1).max(50),
  modelo_id: z.string().uuid(),
  dot: z.string().length(4).regex(/^\d{4}$/),
  profundidad_inicial_mm: z.number().positive().max(25),
  fecha_compra: z.date().optional(),
  costo_compra: z.number().positive().optional()
})

export const NeumaticoUpdateSchema = z.object({
  profundidad_actual_mm: z.number().positive().max(25).optional(),
  presion_actual_psi: z.number().positive().max(150).optional(),
  ubicacion_almacen_id: z.string().uuid().optional(),
  activo: z.boolean().optional()
})

export const EventoNeumaticoSchema = z.object({
  tipo_evento: z.nativeEnum(TipoEventoNeumaticoEnum),
  neumatico_id: z.string().uuid(),
  fecha_evento: z.date().default(() => new Date()),
  kilometraje_vehiculo: z.number().positive().optional(),
  profundidad_remanente: z.number().positive().max(25).optional(),
  presion_psi: z.number().positive().max(150).optional(),
  vehiculo_id: z.string().uuid().optional(),
  posicion_montaje_id: z.string().uuid().optional(),
  almacen_destino_id: z.string().uuid().optional(),
  proveedor_id: z.string().uuid().optional(),
  motivo_desecho_id: z.string().uuid().optional(),
  costo_evento: z.number().positive().optional(),
  notas: z.string().max(1000).optional()
}).refine((data) => {
  // Validaciones condicionales según tipo de evento
  if (data.tipo_evento === 'INSTALACION') {
    return data.vehiculo_id && data.posicion_montaje_id && data.kilometraje_vehiculo
  }
  if (data.tipo_evento === 'DESMONTAJE') {
    return data.kilometraje_vehiculo && data.almacen_destino_id
  }
  if (data.tipo_evento === 'DESECHO') {
    return data.motivo_desecho_id
  }
  return true
}, {
  message: "Campos requeridos faltantes para el tipo de evento"
})

export const NeumaticoQuerySchema = z.object({
  page: z.string().transform(Number).pipe(z.number().positive()),
  limit: z.string().transform(Number).pipe(z.number().positive().max(100)),
  estado: z.nativeEnum(EstadoNeumaticoEnum).optional(),
  modelo_id: z.string().uuid().optional(),
  almacen_id: z.string().uuid().optional(),
  vehiculo_id: z.string().uuid().optional(),
  search: z.string().optional()
})

export type NeumaticoCreate = z.infer<typeof NeumaticoCreateSchema>
export type NeumaticoUpdate = z.infer<typeof NeumaticoUpdateSchema>
export type EventoNeumatico = z.infer<typeof EventoNeumaticoSchema>
export type NeumaticoQuery = z.infer<typeof NeumaticoQuerySchema>
```

### **2. Business Rules Validation**
```typescript
// src/lib/validators/business-rules.ts
import { prisma } from '@/lib/prisma'

export class BusinessRulesValidator {
  static async validateNeumaticoCreation(data: any): Promise<void> {
    // Validar número de serie único
    const existingNeumatico = await prisma.neumatico.findUnique({
      where: { numero_serie: data.numero_serie }
    })
    
    if (existingNeumatico) {
      throw new Error(`Número de serie ${data.numero_serie} ya existe`)
    }

    // Validar que el modelo existe y está activo
    const modelo = await prisma.modeloNeumatico.findUnique({
      where: { id: data.modelo_id }
    })
    
    if (!modelo || !modelo.activo) {
      throw new Error('Modelo de neumático no válido o inactivo')
    }

    // Validar DOT (año de fabricación no mayor a 10 años)
    const dotYear = parseInt(data.dot.substring(2, 4))
    const currentYear = new Date().getFullYear() % 100
    const yearDiff = currentYear - dotYear
    
    if (yearDiff > 10 || yearDiff < 0) {
      throw new Error('DOT indica un año de fabricación no válido')
    }
  }

  static async validateEventoNeumatico(eventoData: any): Promise<void> {
    const { tipo_evento, neumatico_id, vehiculo_id, posicion_montaje_id } = eventoData

    // Validaciones específicas por tipo de evento
    if (tipo_evento === 'INSTALACION') {
      await this.validateInstalacion(neumatico_id, vehiculo_id, posicion_montaje_id)
    }
    
    if (tipo_evento === 'ROTACION') {
      await this.validateRotacion(neumatico_id, vehiculo_id, posicion_montaje_id)
    }
  }

  private static async validateInstalacion(
    neumaticoId: string,
    vehiculoId: string,
    posicionId: string
  ): Promise<void> {
    // Validar compatibilidad modelo-posición
    const neumatico = await prisma.neumatico.findUnique({
      where: { id: neumaticoId },
      include: { modelo: true }
    })

    const vehiculo = await prisma.vehiculo.findUnique({
      where: { id: vehiculoId },
      include: { tipo_vehiculo: true }
    })

    const posicion = await prisma.posicionNeumatico.findUnique({
      where: { id: posicionId },
      include: { configuracion_eje: true }
    })

    // Verificar que el modelo puede ir en esa posición
    const modeloPosicionPermitida = await prisma.modelosPosicionesPermitidas.findFirst({
      where: {
        modelo_id: neumatico!.modelo_id,
        tipo_vehiculo_id: vehiculo!.tipo_vehiculo_id,
        tipo_eje: posicion!.configuracion_eje.tipo_eje
      }
    })

    if (!modeloPosicionPermitida) {
      throw new Error('El modelo de neumático no es compatible con esta posición')
    }

    // Validar restricciones de reencauchados
    if (neumatico!.es_reencauchado && !posicion!.configuracion_eje.permite_reencauchados) {
      throw new Error('No se pueden instalar neumáticos reencauchados en esta posición')
    }
  }
}
```

---

## 🔄 FACTORY PATTERNS

### **1. Service Factory**
```typescript
// src/lib/services/service.factory.ts
import { NeumaticoService } from './neumatico.service'
import { VehiculoService } from './vehiculo.service'
import { AlertaService } from './alerta.service'
import { AuditoriaService } from './auditoria.service'
import { NeumaticoRepository } from '@/lib/repositories/neumatico.repository'

export class ServiceFactory {
  private static instances = new Map()

  static getNeumaticoService(): NeumaticoService {
    if (!this.instances.has('NeumaticoService')) {
      const repository = new NeumaticoRepository()
      const alertaService = this.getAlertaService()
      const auditoriaService = this.getAuditoriaService()
      
      this.instances.set('NeumaticoService', 
        new NeumaticoService(repository, alertaService, auditoriaService)
      )
    }
    return this.instances.get('NeumaticoService')
  }

  static getAlertaService(): AlertaService {
    if (!this.instances.has('AlertaService')) {
      this.instances.set('AlertaService', new AlertaService())
    }
    return this.instances.get('AlertaService')
  }

  static getAuditoriaService(): AuditoriaService {
    if (!this.instances.has('AuditoriaService')) {
      this.instances.set('AuditoriaService', new AuditoriaService())
    }
    return this.instances.get('AuditoriaService')
  }
}
```

---

**Estado:** ✅ PARTE 3 completada  
**Próximo:** PARTE 4 - Sistema de Seguridad y RBAC
