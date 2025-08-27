# Guía de Contribución

¡Gracias por tu interés en contribuir a GES_NEU API! Este documento te guiará a través del proceso de contribución.

## 📋 Tabla de Contenidos

- [Código de Conducta](#código-de-conducta)
- [¿Cómo Contribuir?](#cómo-contribuir)
- [Configuración del Entorno](#configuración-del-entorno)
- [Convenciones de Código](#convenciones-de-código)
- [Flujo de Trabajo](#flujo-de-trabajo)
- [Enviando Cambios](#enviando-cambios)
- [Reportando Errores](#reportando-errores)
- [Solicitando Características](#solicitando-características)

## Código de Conducta

Al participar en este proyecto, aceptas cumplir con nuestro [Código de Conducta](CODE_OF_CONDUCT.md).

## ¿Cómo Contribuir?

1. Haz un fork del repositorio
2. Crea una rama para tu característica (`git checkout -b feature/amazing-feature`)
3. Haz commit de tus cambios (`git commit -m 'Add some amazing feature'`)
4. Haz push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## Configuración del Entorno

Sigue estos pasos para configurar tu entorno de desarrollo:

1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/ges_neu_api.git
   cd ges_neu_api
   ```

2. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: .\venv\Scripts\activate
   ```

3. Instala las dependencias de desarrollo:
   ```bash
   pip install -e ".[dev]"
   ```

4. Configura el archivo de entorno:
   ```bash
   cp .env.example .env
   # Edita el archivo .env con tus configuraciones
   ```

5. Ejecuta las migraciones de la base de datos:
   ```bash
   alembic upgrade head
   ```

## Convenciones de Código

### Estilo de Código

- Seguimos [PEP 8](https://www.python.org/dev/peps/pep-0008/) para el estilo de código Python.
- Usamos [Black](https://github.com/psf/black) para el formateo automático.
- Usamos [isort](https://pycqa.github.io/isort/) para ordenar los imports.
- Usamos [Flake8](https://flake8.pycqa.org/) para el análisis estático.

### Estructura de Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

- `feat`: Nueva característica
- `fix`: Corrección de errores
- `docs`: Cambios en la documentación
- `style`: Cambios de formato (puntos y comas, espacios, etc.)
- `refactor`: Cambios en el código que no corrigen errores ni agregan características
- `perf`: Mejoras de rendimiento
- `test`: Agregar o corregir pruebas
- `chore`: Cambios en el proceso de compilación o herramientas auxiliares

Ejemplo:
```
feat(auth): agregar autenticación con JWT
fix(api): corregir error en el endpoint de usuarios
docs: actualizar README con instrucciones de instalación
```

## Flujo de Trabajo

1. Actualiza tu rama principal:
   ```bash
   git checkout main
   git pull origin main
   ```

2. Crea una nueva rama para tu característica:
   ```bash
   git checkout -b feature/descripcion-breve
   ```

3. Realiza tus cambios y haz commits siguiendo las convenciones.

4. Ejecuta las pruebas y verifica la calidad del código:
   ```bash
   # Formatear código
   black .
   isort .
   
   # Verificar estilo y tipos
   flake8
   mypy .
   
   # Ejecutar pruebas
   pytest
   ```

5. Sube tus cambios y crea un Pull Request:
   ```bash
   git push -u origin feature/descripcion-breve
   ```

## Enviando Cambios

1. Asegúrate de que todas las pruebas pasen.
2. Actualiza la documentación si es necesario.
3. Asegúrate de que tu código cumpla con las guías de estilo.
4. Envía un Pull Request a la rama `main`.

## Reportando Errores

Por favor, usa el [seguimiento de problemas](https://github.com/tu-usuario/ges_neu_api/issues) para informar sobre errores. Incluye:

- Descripción clara del problema
- Pasos para reproducir
- Comportamiento esperado vs. comportamiento real
- Capturas de pantalla si es relevante
- Versión del software y entorno

## Solicitando Características

Abre un nuevo issue con la etiqueta "feature request" y describe:

- La característica que te gustaría ver
- Por qué es útil
- Cómo debería funcionar
- Cualquier otra información relevante

¡Gracias por contribuir a GES_NEU API! 🚀
