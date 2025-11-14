# Pull Request Checklist (Database-First)

Gracias por tu contribución. Antes de solicitar revisión, marca cada punto:

- [ ] Alineación Database-First respetada: no se han propuesto cambios al esquema existente de PostgreSQL.
- [ ] Modelos SQLModel revisados contra `ESQUEMA_COMPLETO_BD.md`.
- [ ] Verificación ejecutada localmente: `poetry run python scripts/run_verify_alignment.py`.
- [ ] Tests pasan localmente: `pytest -q`.
- [ ] Calidad: `ruff` y `mypy` ejecutados sin errores relevantes.
- [ ] Si se agregan nuevos módulos/modelos, se documentan en README y docs.

Notas adicionales:
- Fuente de verdad del esquema: `ESQUEMA_COMPLETO_BD.md` (37 tablas + enums)
- En caso de desalineación, ajustar los modelos/servicios para adaptarse a la BD (no al revés).

## Contexto del cambio

- Descripción breve del cambio:
- Módulos afectados:
- Riesgos y mitigaciones:

## Checklist de pruebas

- [ ] Probado manualmente los endpoints afectados en `/docs`
- [ ] Se agregaron/actualizaron tests
- [ ] Logs revisados para errores/advertencias relevantes
