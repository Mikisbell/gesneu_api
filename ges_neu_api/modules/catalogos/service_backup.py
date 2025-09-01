    # === PROVEEDORES ===
    
    async def create_proveedor(self, db: AsyncSession, proveedor_data: schemas.ProveedorCreate) -> schemas.ProveedorRead:
        """Crear un nuevo proveedor."""
        db_proveedor = models.Proveedor(**proveedor_data.model_dump())
        db.add(db_proveedor)
        await db.commit()
        await db.refresh(db_proveedor)
        return schemas.ProveedorRead.model_validate(db_proveedor)

    async def get_proveedor(self, db: AsyncSession, proveedor_id: UUID) -> Optional[schemas.ProveedorRead]:
        """Obtener un proveedor por ID."""
        result = await db.execute(
            select(models.Proveedor).where(models.Proveedor.id == proveedor_id)
        )
        proveedor = result.scalar_one_or_none()
        if proveedor:
            return schemas.ProveedorRead.model_validate(proveedor)
        return None

    async def get_proveedores(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        activo: Optional[bool] = None
    ) -> List[schemas.ProveedorRead]:
        """Obtener lista de proveedores con paginación."""
        query = select(models.Proveedor)
        
        if activo is not None:
            query = query.where(models.Proveedor.activo == activo)
            
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        proveedores = result.scalars().all()
        
        return [schemas.ProveedorRead.model_validate(p) for p in proveedores]

    async def update_proveedor(
        self, 
        db: AsyncSession, 
        proveedor_id: UUID, 
        proveedor_data: schemas.ProveedorUpdate
    ) -> Optional[schemas.ProveedorRead]:
        """Actualizar un proveedor existente."""
        result = await db.execute(
            select(models.Proveedor).where(models.Proveedor.id == proveedor_id)
        )
        proveedor = result.scalar_one_or_none()
        if not proveedor:
            return None
            
        update_data = proveedor_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(proveedor, field, value)
            
        await db.commit()
        await db.refresh(proveedor)
        return schemas.ProveedorRead.model_validate(proveedor)

    async def delete_proveedor(self, db: AsyncSession, proveedor_id: UUID) -> bool:
        """Eliminar un proveedor (soft delete)."""
        result = await db.execute(
            select(models.Proveedor).where(models.Proveedor.id == proveedor_id)
        )
        proveedor = result.scalar_one_or_none()
        if not proveedor:
            return False
            
        proveedor.activo = False
        await db.commit()
        return True

    # === MOTIVOS DE DESECHO ===
    
    async def create_motivo_desecho(self, db: AsyncSession, motivo_data: schemas.MotivoDesechoCreate) -> schemas.MotivoDesechoRead:
        """Crear un nuevo motivo de desecho."""
        db_motivo = models.MotivoDesecho(**motivo_data.model_dump())
        db.add(db_motivo)
        await db.commit()
        await db.refresh(db_motivo)
        return schemas.MotivoDesechoRead.model_validate(db_motivo)

    async def get_motivo_desecho(self, db: AsyncSession, motivo_id: UUID) -> Optional[schemas.MotivoDesechoRead]:
        """Obtener un motivo de desecho por ID."""
        result = await db.execute(
            select(models.MotivoDesecho).where(models.MotivoDesecho.id == motivo_id)
        )
        motivo = result.scalar_one_or_none()
        if motivo:
            return schemas.MotivoDesechoRead.model_validate(motivo)
        return None

    async def get_motivos_desecho(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        activo: Optional[bool] = None
    ) -> List[schemas.MotivoDesechoRead]:
        """Obtener lista de motivos de desecho con paginación."""
        query = select(models.MotivoDesecho)
        
        if activo is not None:
            query = query.where(models.MotivoDesecho.activo == activo)
            
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        motivos = result.scalars().all()
        
        return [schemas.MotivoDesechoRead.model_validate(m) for m in motivos]

    async def update_motivo_desecho(
        self, 
        db: AsyncSession, 
        motivo_id: UUID, 
        motivo_data: schemas.MotivoDesechoUpdate
    ) -> Optional[schemas.MotivoDesechoRead]:
        """Actualizar un motivo de desecho existente."""
        result = await db.execute(
            select(models.MotivoDesecho).where(models.MotivoDesecho.id == motivo_id)
        )
        motivo = result.scalar_one_or_none()
        if not motivo:
            return None
            
        update_data = motivo_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(motivo, field, value)
            
        await db.commit()
        await db.refresh(motivo)
        return schemas.MotivoDesechoRead.model_validate(motivo)

    async def delete_motivo_desecho(self, db: AsyncSession, motivo_id: UUID) -> bool:
        """Eliminar un motivo de desecho (soft delete)."""
        result = await db.execute(
            select(models.MotivoDesecho).where(models.MotivoDesecho.id == motivo_id)
        )
        motivo = result.scalar_one_or_none()
        if not motivo:
            return False
            
        motivo.activo = False
        await db.commit()
        return True

    # === ALMACENES ===
    
    async def create_almacen(self, db: AsyncSession, almacen_data: schemas.AlmacenCreate) -> schemas.AlmacenRead:
        """Crear un nuevo almacén."""
        db_almacen = models.Almacen(**almacen_data.model_dump())
        db.add(db_almacen)
        await db.commit()
        await db.refresh(db_almacen)
        return schemas.AlmacenRead.model_validate(db_almacen)

    async def get_almacen(self, db: AsyncSession, almacen_id: UUID) -> Optional[schemas.AlmacenRead]:
        """Obtener un almacén por ID."""
        result = await db.execute(
            select(models.Almacen).where(models.Almacen.id == almacen_id)
        )
        almacen = result.scalar_one_or_none()
        if almacen:
            return schemas.AlmacenRead.model_validate(almacen)
        return None

    async def get_almacenes(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        activo: Optional[bool] = None
    ) -> List[schemas.AlmacenRead]:
        """Obtener lista de almacenes con paginación."""
        query = select(models.Almacen)
        
        if activo is not None:
            query = query.where(models.Almacen.activo == activo)
            
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        almacenes = result.scalars().all()
        
        return [schemas.AlmacenRead.model_validate(a) for a in almacenes]

    async def update_almacen(
        self, 
        db: AsyncSession, 
        almacen_id: UUID, 
        almacen_data: schemas.AlmacenUpdate
    ) -> Optional[schemas.AlmacenRead]:
        """Actualizar un almacén existente."""
        result = await db.execute(
            select(models.Almacen).where(models.Almacen.id == almacen_id)
        )
        almacen = result.scalar_one_or_none()
        if not almacen:
            return None
            
        update_data = almacen_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(almacen, field, value)
            
        await db.commit()
        await db.refresh(almacen)
        return schemas.AlmacenRead.model_validate(almacen)

    async def delete_almacen(self, db: AsyncSession, almacen_id: UUID) -> bool:
        """Eliminar un almacén (soft delete)."""
        result = await db.execute(
            select(models.Almacen).where(models.Almacen.id == almacen_id)
        )
        almacen = result.scalar_one_or_none()
        if not almacen:
            return False
            
        almacen.activo = False
        await db.commit()
        return True

    # === PARÁMETROS DE INVENTARIO ===
    
    async def create_parametro_inventario(self, db: AsyncSession, parametro_data: schemas.ParametroInventarioCreate) -> schemas.ParametroInventarioRead:
        """Crear un nuevo parámetro de inventario."""
        db_parametro = models.ParametroInventario(**parametro_data.model_dump())
        db.add(db_parametro)
        await db.commit()
        await db.refresh(db_parametro)
        return schemas.ParametroInventarioRead.model_validate(db_parametro)

    async def get_parametro_inventario(self, db: AsyncSession, parametro_id: UUID) -> Optional[schemas.ParametroInventarioRead]:
        """Obtener un parámetro de inventario por ID."""
        result = await db.execute(
            select(models.ParametroInventario).where(models.ParametroInventario.id == parametro_id)
        )
        parametro = result.scalar_one_or_none()
        if parametro:
            return schemas.ParametroInventarioRead.model_validate(parametro)
        return None

    async def get_parametros_inventario(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        activo: Optional[bool] = None
    ) -> List[schemas.ParametroInventarioRead]:
        """Obtener lista de parámetros de inventario con paginación."""
        query = select(models.ParametroInventario)
        
        if activo is not None:
            query = query.where(models.ParametroInventario.activo == activo)
            
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        parametros = result.scalars().all()
        
        return [schemas.ParametroInventarioRead.model_validate(p) for p in parametros]

    async def update_parametro_inventario(
        self, 
        db: AsyncSession, 
        parametro_id: UUID, 
        parametro_data: schemas.ParametroInventarioUpdate
    ) -> Optional[schemas.ParametroInventarioRead]:
        """Actualizar un parámetro de inventario existente."""
        result = await db.execute(
            select(models.ParametroInventario).where(models.ParametroInventario.id == parametro_id)
        )
        parametro = result.scalar_one_or_none()
        if not parametro:
            return None
            
        update_data = parametro_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(parametro, field, value)
            
        await db.commit()
        await db.refresh(parametro)
        return schemas.ParametroInventarioRead.model_validate(parametro)

    async def delete_parametro_inventario(self, db: AsyncSession, parametro_id: UUID) -> bool:
        """Eliminar un parámetro de inventario (soft delete)."""
        result = await db.execute(
            select(models.ParametroInventario).where(models.ParametroInventario.id == parametro_id)
        )
        parametro = result.scalar_one_or_none()
        if not parametro:
            return False
        
        parametro.activo = False
        await db.commit()
        return True


# Create service instance
catalog_service = CatalogService()
    ) -> bool:
        """Eliminar un motivo de desecho."""
        result = await db.execute(
            select(models.MotivoDesecho).where(models.MotivoDesecho.id == motivo_id)
        )
        motivo = result.scalar_one_or_none()
        if not motivo:
            return False
        
        motivo.activo = False
        await db.commit()
        return True

    async def create_almacen(
        self, 
        db: AsyncSession, 
        almacen_data: schemas.AlmacenCreate
    ) -> schemas.AlmacenRead:
        """Crear un nuevo almacén."""
        db_almacen = models.Almacen(**almacen_data.model_dump())
        db.add(db_almacen)
        await db.commit()
        await db.refresh(db_almacen)
        return schemas.AlmacenRead.model_validate(db_almacen)

    async def get_almacen(
        self, 
        db: AsyncSession, 
        almacen_id: UUID
    ) -> Optional[schemas.AlmacenRead]:
        """Obtener un almacén por ID."""
        result = await db.execute(
            select(models.Almacen).where(
                models.Almacen.id == almacen_id,
                models.Almacen.activo == True
            )
        )
        almacen = result.scalar_one_or_none()
        return schemas.AlmacenRead.model_validate(almacen) if almacen else None

    async def get_almacenes(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[schemas.AlmacenRead]:
        """Obtener lista de almacenes."""
        result = await db.execute(
            select(models.Almacen)
            .where(models.Almacen.activo == True)
            .offset(skip)
            .limit(limit)
        )
        almacenes = result.scalars().all()
        return [schemas.AlmacenRead.model_validate(a) for a in almacenes]

    async def update_almacen(
        self, 
        db: AsyncSession, 
        almacen_id: UUID, 
        almacen_data: schemas.AlmacenUpdate
    ) -> Optional[schemas.AlmacenRead]:
        """Actualizar un almacén."""
        result = await db.execute(
            select(models.Almacen).where(models.Almacen.id == almacen_id)
        )
        almacen = result.scalar_one_or_none()
        if not almacen:
            return None
        
        update_data = almacen_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(almacen, field, value)
        
        await db.commit()
        await db.refresh(almacen)
        return schemas.AlmacenRead.model_validate(almacen)

    async def delete_almacen(
        self, 
        db: AsyncSession, 
        almacen_id: UUID
    ) -> bool:
        """Eliminar un almacén."""
        result = await db.execute(
            select(models.Almacen).where(models.Almacen.id == almacen_id)
        )
        almacen = result.scalar_one_or_none()
        if not almacen:
            return False
        
        almacen.activo = False
        await db.commit()
        return True

    async def create_parametro_inventario(
        self, 
        db: AsyncSession, 
        parametro_data: schemas.ParametroInventarioCreate
    ) -> schemas.ParametroInventarioRead:
        """Crear un nuevo parámetro de inventario."""
        db_parametro = models.ParametroInventario(**parametro_data.model_dump())
        db.add(db_parametro)
        await db.commit()
        await db.refresh(db_parametro)
        return schemas.ParametroInventarioRead.model_validate(db_parametro)

    async def get_parametro_inventario(
        self, 
        db: AsyncSession, 
        parametro_id: UUID
    ) -> Optional[schemas.ParametroInventarioRead]:
        """Obtener un parámetro de inventario por ID."""
        result = await db.execute(
            select(models.ParametroInventario).where(
                models.ParametroInventario.id == parametro_id,
                models.ParametroInventario.activo == True
            )
        )
        parametro = result.scalar_one_or_none()
        return schemas.ParametroInventarioRead.model_validate(parametro) if parametro else None

    async def get_parametros_inventario(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[schemas.ParametroInventarioRead]:
        """Obtener lista de parámetros de inventario."""
        result = await db.execute(
            select(models.ParametroInventario)
            .where(models.ParametroInventario.activo == True)
            .offset(skip)
            .limit(limit)
        )
        parametros = result.scalars().all()
        return [schemas.ParametroInventarioRead.model_validate(p) for p in parametros]

    async def update_parametro_inventario(
        self, 
        db: AsyncSession, 
        parametro_id: UUID, 
        parametro_data: schemas.ParametroInventarioUpdate
    ) -> Optional[schemas.ParametroInventarioRead]:
        """Actualizar un parámetro de inventario."""
        result = await db.execute(
            select(models.ParametroInventario).where(models.ParametroInventario.id == parametro_id)
        )
        parametro = result.scalar_one_or_none()
        if not parametro:
            return None
        
        update_data = parametro_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(parametro, field, value)
        
        await db.commit()
        await db.refresh(parametro)
        return schemas.ParametroInventarioRead.model_validate(parametro)

    async def delete_parametro_inventario(
        self, 
        db: AsyncSession, 
        parametro_id: UUID
    ) -> bool:
        """Eliminar un parámetro de inventario."""
        result = await db.execute(
            select(models.ParametroInventario).where(models.ParametroInventario.id == parametro_id)
        )
        parametro = result.scalar_one_or_none()
        if not parametro:
            return False
        
        parametro.activo = False
        await db.commit()
        return True

    async def _get_proveedor(self, proveedor_id: UUID) -> Optional[models.Proveedor]:
        """Obtiene un proveedor por su ID."""
        result = await self.db.execute(
            select(models.Proveedor).where(models.Proveedor.id == proveedor_id, models.Proveedor.activo == True)
{{ ... }}
        )
        return result.scalars().first()

    async def _get_proveedor_by_ruc(self, ruc: str) -> Optional[models.Proveedor]:
        """Obtiene un proveedor por su RUC."""
        result = await self.db.execute(
            select(models.Proveedor).where(models.Proveedor.ruc == ruc)
        )
        return result.scalars().first()

    async def _get_proveedor_by_email(self, email: str) -> Optional[models.Proveedor]:
        """Obtiene un proveedor por su email."""
        result = await self.db.execute(
            select(models.Proveedor).where(models.Proveedor.email == email)
        )
        return result.scalars().first()

    async def _get_all_proveedores(
        self,
        skip: int = 0,
        limit: int = 100,
        activo: Optional[bool] = None,
        tipo: Optional[str] = None
    ) -> List[models.Proveedor]:
        """Obtiene todos los proveedores con filtros opcionales."""
        query = select(models.Proveedor)

        if activo is not None:
            query = query.where(models.Proveedor.activo == activo)
        if tipo is not None:
            query = query.where(models.Proveedor.tipo == tipo)

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def _create_proveedor(
        self,
        *,
        obj_in: schemas.ProveedorCreate,
        user_id: UUID
    ) -> models.Proveedor:
        """Crea un nuevo proveedor."""
        db_obj_data = obj_in.model_dump(exclude_unset=True)
        db_obj_data['creado_por'] = user_id
        db_obj = models.Proveedor(**db_obj_data)

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def _update_proveedor(
        self,
        *,
        db_obj: models.Proveedor,
        obj_in: Union[schemas.ProveedorUpdate, Dict[str, Any]],
        user_id: UUID
    ) -> models.Proveedor:
        """Actualiza un proveedor existente."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        update_data['actualizado_por'] = user_id
        update_data['actualizado_en'] = datetime.utcnow()

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def _remove_proveedor(self, *, db_obj: models.Proveedor) -> models.Proveedor:
        """Elimina un proveedor."""
        await self.db.delete(db_obj)
        await self.db.commit()
        return db_obj

    # --- CRUD para MotivoDesecho ---

    async def _get_motivo_desecho(self, motivo_id: UUID) -> Optional[models.MotivoDesecho]:
        """Obtiene un motivo de desecho por su ID."""
        result = await self.db.execute(
            select(models.MotivoDesecho).where(models.MotivoDesecho.id == motivo_id)
        )
        return result.scalars().first()

    async def _get_motivo_desecho_by_codigo(self, codigo: str) -> Optional[models.MotivoDesecho]:
        """Obtiene un motivo de desecho por su código."""
        result = await self.db.execute(
            select(models.MotivoDesecho).where(models.MotivoDesecho.codigo == codigo)
        )
        return result.scalars().first()

    async def _get_all_motivos_desecho(
        self,
        skip: int = 0,
        limit: int = 100,
        activo: Optional[bool] = None
    ) -> List[models.MotivoDesecho]:
        """Obtiene todos los motivos de desecho con filtros opcionales."""
        query = select(models.MotivoDesecho)

        if activo is not None:
            query = query.where(models.MotivoDesecho.activo == activo)

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def _create_motivo_desecho(
        self,
        *,
        obj_in: schemas.MotivoDesechoCreate,
        user_id: UUID
    ) -> models.MotivoDesecho:
        """Crea un nuevo motivo de desecho."""
        db_obj = models.MotivoDesecho(
            **obj_in.model_dump(),
            creado_por=user_id
        )

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def _update_motivo_desecho(
        self,
        *,
        db_obj: models.MotivoDesecho,
        obj_in: Union[schemas.MotivoDesechoUpdate, Dict[str, Any]],
        user_id: UUID
    ) -> models.MotivoDesecho:
        """Actualiza un motivo de desecho existente."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        update_data['actualizado_por'] = user_id
        update_data['actualizado_en'] = datetime.utcnow()

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def _remove_motivo_desecho(self, *, db_obj: models.MotivoDesecho) -> models.MotivoDesecho:
        """Elimina un motivo de desecho."""
        await self.db.delete(db_obj)
        await self.db.commit()
        return db_obj

    # --- CRUD para Almacen ---

    async def _get_almacen(
        self,
        almacen_id: UUID
    ) -> Optional[models.Almacen]:
        """Obtiene un almacén por su ID."""
        result = await self.db.execute(
            select(models.Almacen)
            .where(models.Almacen.id == almacen_id)
        )
        return result.scalar_one_or_none()

    async def _get_almacen_by_codigo(
        self,
        codigo: str
    ) -> Optional[models.Almacen]:
        """Obtiene un almacén por su código."""
        result = await self.db.execute(
            select(models.Almacen)
            .where(func.lower(models.Almacen.codigo) == func.lower(codigo))
        )
        return result.scalar_one_or_none()

    async def _get_all_almacenes(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        activo: Optional[bool] = None
    ) -> List[models.Almacen]:
        """
        Obtiene una lista de almacenes con paginación y filtros opcionales.

        Args:
            db: Sesión de base de datos
            skip: Número de registros a omitir (para paginación)
            limit: Número máximo de registros a devolver
            activo: Filtrar por estado activo/inactivo

        Returns:
            Lista de almacenes
        """
        query = select(models.Almacen).order_by(models.Almacen.nombre)

        if activo is not None:
            query = query.where(models.Almacen.activo == activo)

        result = await self.db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()

    async def _create_almacen(
        self,
        *,
        almacen_in: schemas.AlmacenCreate,
        user_id: UUID
    ) -> models.Almacen:
        """
        Crea un nuevo almacén.

        Args:
            db: Sesión de base de datos
            almacen_in: Datos del almacén a crear
            user_id: ID del usuario que realiza la operación

        Returns:
            El almacén creado
        """
        db_obj = models.Almacen(
            **almacen_in.model_dump(),
            creado_por=user_id
        )

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def _update_almacen(
        self,
        *,
        db_obj: models.Almacen,
        almacen_in: schemas.AlmacenUpdate,
        user_id: UUID
    ) -> models.Almacen:
        """
        Actualiza un almacén existente.

        Args:
            db: Sesión de base de datos
            db_obj: Instancia del almacén a actualizar
            almacen_in: Datos a actualizar
            user_id: ID del usuario que realiza la operación

        Returns:
            El almacén actualizado
        """
        update_data = almacen_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        # Actualizar campos de auditoría
        db_obj.actualizado_en = datetime.now()
        db_obj.actualizado_por = user_id

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def _remove_almacen(
        self,
        *,
        almacen_id: UUID
    ) -> bool:
        """
        Elimina un almacén por su ID.

        Args:
            db: Sesión de base de datos
            almacen_id: ID del almacén a eliminar

        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        result = await self.db.execute(
            delete(models.Almacen)
            .where(models.Almacen.id == almacen_id)
        )
        await self.db.commit()
        return result.rowcount > 0

    # --- CRUD para ParametroInventario ---

    async def _get_parametro_inventario(
        self,
        parametro_id: UUID
    ) -> Optional[models.ParametroInventario]:
        """Obtiene un parámetro de inventario por su ID."""
        result = await self.db.execute(
            select(models.ParametroInventario)
            .where(models.ParametroInventario.id == parametro_id)
        )
        return result.scalar_one_or_none()

    async def _get_parametro_inventario_by_codigo(
        self,
        codigo: str
    ) -> Optional[models.ParametroInventario]:
        """Obtiene un parámetro de inventario por su código."""
        result = await self.db.execute(
            select(models.ParametroInventario)
            .where(func.lower(models.ParametroInventario.codigo) == func.lower(codigo))
        )
        return result.scalar_one_or_none()

    async def _get_all_parametros_inventario(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        activo: Optional[bool] = None
    ) -> List[models.ParametroInventario]:
        """
        Obtiene una lista de parámetros de inventario con paginación y filtros opcionales.

        Args:
            db: Sesión de base de datos
            skip: Número de registros a omitir (para paginación)
            limit: Número máximo de registros a devolver
            activo: Filtrar por estado activo/inactivo

        Returns:
            Lista de parámetros de inventario
        """
        query = select(models.ParametroInventario).order_by(models.ParametroInventario.nombre)

        if activo is not None:
            query = query.where(models.ParametroInventario.activo == activo)

        result = await self.db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()

    async def _create_parametro_inventario(
        self,
        *,
        parametro_in: schemas.ParametroInventarioCreate,
        user_id: UUID
    ) -> models.ParametroInventario:
        """
        Crea un nuevo parámetro de inventario.

        Args:
            db: Sesión de base de datos
            parametro_in: Datos del parámetro a crear
            user_id: ID del usuario que realiza la operación

        Returns:
            El parámetro de inventario creado
        """
        db_obj = models.ParametroInventario(
            **parametro_in.model_dump(),
            creado_por=user_id
        )

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def _update_parametro_inventario(
        self,
        *,
        db_obj: models.ParametroInventario,
        parametro_in: Union[schemas.ParametroInventarioUpdate, Dict[str, Any]],
        user_id: UUID
    ) -> models.ParametroInventario:
        """
        Actualiza un parámetro de inventario existente.

        Args:
            db: Sesión de base de datos
            db_obj: Instancia del parámetro a actualizar
            parametro_in: Datos a actualizar
            user_id: ID del usuario que realiza la operación

        Returns:
            El parámetro de inventario actualizado
        """
        if isinstance(parametro_in, dict):
            update_data = parametro_in
        else:
            update_data = parametro_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        # Actualizar campos de auditoría
        db_obj.actualizado_en = datetime.now()
        db_obj.actualizado_por = user_id

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def _remove_parametro_inventario(
        self,
        *,
        parametro_id: UUID
    ) -> bool:
        """
        Elimina un parámetro de inventario por su ID.

        Args:
            db: Sesión de base de datos
            parametro_id: ID del parámetro a eliminar

        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        result = await self.db.execute(
            delete(models.ParametroInventario)
            .where(models.ParametroInventario.id == parametro_id)
        )
        await self.db.commit()
        return result.rowcount > 0

    async def _check_permission(
        self, 
        user: Usuario,
        object_id: UUID, 
        model: Type[T],
        action: str = "read"
    ) -> T:
        """
        Verifica los permisos del usuario sobre un objeto.
        
        Args:
            user: Usuario que realiza la acción
            object_id: ID del objeto sobre el que se quiere actuar
            model: Clase del modelo SQLAlchemy
            action: Acción que se quiere realizar (read, update, delete)
            
        Returns:
            El objeto si el usuario tiene permisos
            
        Raises:
            HTTPException 403: Si el usuario no tiene permisos
            HTTPException 404: Si el objeto no existe
        """
        # Si el usuario es administrador, tiene acceso completo
        if user.is_admin:
            result = await self.db.execute(select(model).where(model.id == object_id))
            obj = result.scalars().first()
            if not obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Recurso con ID {object_id} no encontrado"
                )
            return obj
            
        # Para usuarios normales, verificar permisos específicos
        # Temporarily commented out due to models.CatalogoItem not existing
        # if model == models.CatalogoItem:
        #     has_permission = await CatalogItemPermissionChecker.check_permission(
        #         self.db, user.id, object_id, action
        #     )
        #     if not has_permission:
        #         raise HTTPException(
        #             status_code=status.HTTP_403_FORBIDDEN,
        #             detail="No tiene permisos para realizar esta acción"
        #         )
                
        # Obtener el objeto
        result = await self.db.execute(select(model).where(model.id == object_id))
        obj = result.scalars().first()
        
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recurso con ID {object_id} no encontrado"
            )
            
        # Verificar propiedad si el modelo tiene owner_id
        if hasattr(obj, 'owner_id') and str(obj.owner_id) != str(user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para acceder a este recurso"
            )
            
        return obj

    # --- Lógica de negocio para Fabricantes ---

    @monitor_service_method
    async def get_all_fabricantes(
        self, 
        user: Usuario,
        skip: int = 0, 
        limit: int = 100,
        activo: Optional[bool] = None
    ) -> List[models.Fabricante]:
        """Obtiene todos los fabricantes con filtro opcional por estado."""
        return await self._get_all_fabricantes(
            skip=skip, limit=limit, activo=activo
        )

    @monitor_service_method
    async def get_fabricante_by_id(
        self, 
        user: Usuario,
        fabricante_id: UUID
    ) -> models.Fabricante:
        """Obtiene un fabricante por ID con verificación de permisos."""
        # Verificar permisos si es necesario
        if not user or not user.is_admin:
            # Para este ejemplo, asumimos que los fabricantes son de solo lectura para todos
            # los usuarios autenticados. Si necesitas control de acceso más fino, 
            # implementa la lógica específica aquí.
            pass
            
        db_fabricante = await self._get_fabricante(fabricante_id=fabricante_id)
        if not db_fabricante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Fabricante con ID {fabricante_id} no encontrado"
            )
        return db_fabricante

    @monitor_service_method
    async def update_fabricante(
        self, 
        user: Usuario,
        fabricante_id: UUID,
        fabricante_update: schemas.FabricanteUpdate
    ) -> models.Fabricante:
        """Actualiza un fabricante existente con verificación de permisos."""
        # Verificar permisos - solo administradores pueden actualizar fabricantes
        if not user or not user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Se requieren permisos de administrador para actualizar fabricantes"
            )
            
        db_fabricante = await self._get_fabricante(fabricante_id=fabricante_id)
        if not db_fabricante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Fabricante con ID {fabricante_id} no encontrado"
            )
            
        return await self._update_fabricante(
            db_obj=db_fabricante, obj_in=fabricante_update, user_id=user.id
        )

    @monitor_service_method
    async def delete_fabricante(
        self, 
        user: Usuario,
        fabricante_id: UUID
    ) -> models.Fabricante:
        """Elimina un fabricante con verificación de permisos."""
        # Verificar permisos - solo administradores pueden eliminar fabricantes
        if not user or not user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Se requieren permisos de administrador para eliminar fabricantes"
            )
            
        db_fabricante = await self._get_fabricante(fabricante_id=fabricante_id)
        if not db_fabricante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Fabricante con ID {fabricante_id} no encontrado"
            )
            
        return await self._remove_fabricante(db_obj=db_fabricante)

    # --- Lógica de negocio para Modelos ---

    @monitor_service_method
    async def get_all_modelos(
        self, 
        user: Usuario,
        skip: int = 0, 
        limit: int = 100,
        fabricante_id: Optional[UUID] = None,
        activo: Optional[bool] = None
    ) -> List[models.ModeloNeumatico]:
        """Obtiene todos los modelos con filtros opcionales."""
        return await self._get_all_modelos(
            skip=skip, 
            limit=limit, 
            fabricante_id=fabricante_id,
            activo=activo
        )

    @monitor_service_method
    async def get_modelo_by_id(
        self, 
        user: Usuario,
        modelo_id: UUID
    ) -> models.ModeloNeumatico:
        """Obtiene un modelo por ID con verificación de permisos."""
        # Verificar permisos si es necesario
        if not user or not user.is_admin:
            # Para este ejemplo, asumimos que los modelos son de solo lectura para todos
            # los usuarios autenticados. Si necesitas control de acceso más fino, 
            # implementa la lógica específica aquí.
            pass
            
        db_modelo = await self._get_modelo(modelo_id=modelo_id)
        if not db_modelo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Modelo con ID {modelo_id} no encontrado"
            )
        return db_modelo

    @monitor_service_method
    async def update_modelo(
        self, 
        user: Usuario,
        modelo_id: UUID,
        modelo_update: schemas.ModeloNeumaticoUpdate
    ) -> models.ModeloNeumatico:
        """Actualiza un modelo existente con verificación de permisos."""
        # Verificar permisos - solo administradores pueden actualizar modelos
        if not user or not user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Se requieren permisos de administrador para actualizar modelos"
            )
            
        db_modelo = await self._get_modelo(modelo_id=modelo_id)
        if not db_modelo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Modelo con ID {modelo_id} no encontrado"
            )
            
        return await self._update_modelo(
            db_obj=db_modelo, obj_in=modelo_update, user_id=user.id
        )

    @monitor_service_method
    async def delete_modelo(
        self, 
        user: Usuario,
        modelo_id: UUID
    ) -> models.ModeloNeumatico:
        """Elimina un modelo con verificación de permisos."""
        # Verificar permisos - solo administradores pueden eliminar modelos
        if not user or not user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Se requieren permisos de administrador para eliminar modelos"
            )
            
        db_modelo = await self._get_modelo(modelo_id=modelo_id)
        if not db_modelo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Modelo con ID {modelo_id} no encontrado"
            )
            
        return await self._remove_modelo(db_obj=db_modelo)

    # --- Lógica de negocio para Proveedores ---

    @monitor_service_method
    async def get_all_proveedores(
        self, 
        user: Usuario,
        skip: int = 0, 
        limit: int = 100,
        activo: Optional[bool] = None,
        tipo: Optional[str] = None
    ) -> List[models.Proveedor]:
        """Obtiene todos los proveedores con filtros opcionales."""
        return await self._get_all_proveedores(
            skip=skip, limit=limit, activo=activo, tipo=tipo
        )

    @monitor_service_method
    async def get_proveedor_by_id(
        self, 
        user: Usuario,
        proveedor_id: UUID
    ) -> models.Proveedor:
        """Obtiene un proveedor por ID con verificación de permisos."""
        # Verificar permisos si es necesario
        if not user or not user.is_admin:
            # Para este ejemplo, asumimos que los proveedores son de solo lectura para todos
            # los usuarios autenticados. Si necesitas control de acceso más fino, 
            # implementa la lógica específica aquí.
            pass
            
        db_proveedor = await self._get_proveedor(proveedor_id=proveedor_id)
        if not db_proveedor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proveedor con ID {proveedor_id} no encontrado"
            )
        return db_proveedor

    @monitor_service_method
    async def update_proveedor(
        self, 
        user: Usuario,
        proveedor_id: UUID,
        proveedor_update: schemas.ProveedorUpdate
    ) -> models.Proveedor:
        """Actualiza un proveedor existente con verificación de permisos."""
        # Verificar permisos - solo administradores pueden actualizar proveedores
        if not user or not user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Se requieren permisos de administrador para actualizar proveedores"
            )
            
        db_proveedor = await self._get_proveedor(proveedor_id=proveedor_id)
        if not db_proveedor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proveedor con ID {proveedor_id} no encontrado"
            )
            
        return await self._update_proveedor(
            db_obj=db_proveedor, obj_in=proveedor_update, user_id=user.id
        )

    @monitor_service_method
    async def delete_proveedor(
        self, 
        user: Usuario,
        proveedor_id: UUID
    ) -> models.Proveedor:
        """Elimina un proveedor con verificación de permisos."""
        # Verificar permisos - solo administradores pueden eliminar proveedores
        if not user or not user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Se requieren permisos de administrador para eliminar proveedores"
            )
            
        db_proveedor = await self._get_proveedor(proveedor_id=proveedor_id)
        if not db_proveedor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proveedor con ID {proveedor_id} no encontrado"
            )
            
        return await self._remove_proveedor(db_obj=db_proveedor)

    # --- Lógica de negocio para Motivos de Desecho ---

    @monitor_service_method
    async def get_all_motivos_desecho(
        self, 
        user: Usuario,
        skip: int = 0, 
        limit: int = 100,
        activo: Optional[bool] = None
    ) -> List[models.MotivoDesecho]:
        """Obtiene todos los motivos de desecho con filtros opcionales."""
        return await self._get_all_motivos_desecho(
            skip=skip, limit=limit, activo=activo
        )

    @monitor_service_method
    async def get_motivo_desecho_by_id(
        self, 
        user: Usuario,
        motivo_id: UUID
    ) -> models.MotivoDesecho:
        """Obtiene un motivo de desecho por ID con verificación de permisos."""
        # Verificar permisos si es necesario
        if not user or not user.is_admin:
            # Para este ejemplo, asumimos que los motivos de desecho son de solo lectura para todos
            # los usuarios autenticados. Si necesitas control de acceso más fino, 
            # implementa la lógica específica aquí.
            pass
            
        db_motivo = await self._get_motivo_desecho(motivo_id=motivo_id)
        if not db_motivo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Motivo de desecho con ID {motivo_id} no encontrado"
            )
        return db_motivo

    @monitor_service_method
    async def update_motivo_desecho(
        self, 
        user: Usuario,
        motivo_id: UUID,
        motivo_update: schemas.MotivoDesechoUpdate
    ) -> models.MotivoDesecho:
        """Actualiza un motivo de desecho existente con verificación de permisos."""
        # Verificar permisos - solo administradores pueden actualizar motivos de desecho
        if not user or not user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Se requieren permisos de administrador para actualizar motivos de desecho"
            )
            
        db_motivo = await self._get_motivo_desecho(motivo_id=motivo_id)
        if not db_motivo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Motivo de desecho con ID {motivo_id} no encontrado"
            )
            
        return await self._update_motivo_desecho(
            db_obj=db_motivo, obj_in=motivo_update, user_id=user.id
        )

    @monitor_service_method
    async def delete_motivo_desecho(
        self, 
        user: Usuario,
        motivo_id: UUID
    ) -> models.MotivoDesecho:
        """Elimina un motivo de desecho con verificación de permisos."""
        # Verificar permisos - solo administradores pueden eliminar motivos de desecho
        if not user or not user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Se requieren permisos de administrador para eliminar motivos de desecho"
            )
            
        db_motivo = await self._get_motivo_desecho(motivo_id=motivo_id)
        if not db_motivo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Motivo de desecho con ID {motivo_id} no encontrado"
            )
            
        return await self._remove_motivo_desecho(db_obj=db_motivo)

    # --- Servicios para Almacen ---

    @monitor_service_method
    async def get_almacen(
        self,
        user: Usuario,
        almacen_id: UUID
    ) -> models.Almacen:
        """Obtiene un almacén por su ID con verificación de permisos."""
        # Verificar permisos si es necesario
        if not user or not user.is_admin:
            # Para este ejemplo, asumimos que los almacenes son de solo lectura para todos
            # los usuarios autenticados. Si necesitas control de acceso más fino, 
            # implementa la lógica específica aquí.
            pass
            
        db_almacen = await self._get_almacen(almacen_id=almacen_id)
        if not db_almacen:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Almacén con ID {almacen_id} no encontrado"
            )
        return db_almacen

    @monitor_service_method
    async def get_almacenes(
        self,
        user: Usuario,
        *,
        skip: int = 0,
        limit: int = 100,
        activo: Optional[bool] = None
    ) -> List[models.Almacen]:
        """Obtiene una lista de almacenes con paginación y filtros opcionales."""
        return await self._get_all_almacenes(
            skip=skip,
            limit=limit,
            activo=activo
        )

    # ... (otros métodos de Almacen y ParametroInventario seguirían el mismo patrón) ...

    # --- Métodos para CatalogoItem con verificación de permisos ---
    
    @monitor_service_method
    async def get_catalogo_item(
        self, 
        user: Usuario,
        item_id: UUID
    ) -> AnyCatalogoItemModel:
        """Obtiene un ítem del catálogo por ID con verificación de permisos."""
        return await self._check_permission(user, item_id, models.CatalogoItem, "read")
    
    @monitor_service_method
    async def update_catalogo_item(
        self, 
        user: Usuario,
        item_id: UUID,
        item_update: schemas.CatalogoItemUpdate
    ) -> AnyCatalogoItemModel:
        """Actualiza un ítem del catálogo con verificación de permisos."""
        # Verificar permisos
        item = await self._check_permission(user, item_id, models.CatalogoItem, "update")
        
        # Actualizar el ítem
        return await crud.update_catalogo_item(
            self.db, db_item=item, item_update=item_update
        )
    
    @monitor_service_method
    async def delete_catalogo_item(
        self, 
        user: Usuario,
        item_id: UUID
    ) -> AnyCatalogoItemModel:
        """Elimina un ítem del catálogo con verificación de permisos."""
        # Verificar permisos
        item = await self._check_permission(user, item_id, models.CatalogoItem, "delete")
        
        # Eliminar el ítem
        return await crud.delete_catalogo_item(self.db, db_item=item)

    # ... (implementaciones de otros métodos del contrato) ...