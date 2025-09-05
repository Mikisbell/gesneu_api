#!/usr/bin/env python3
"""
Script para verificar todos los endpoints de la API GesNeu
"""
import sys
sys.path.append('.')
from ges_neu_api.main import app
from fastapi.routing import APIRoute

print('=== VERIFICACIÓN DE ENDPOINTS DE LA API GESNEU ===')
print()

# Obtener todas las rutas registradas
routes = []
for route in app.routes:
    if isinstance(route, APIRoute):
        routes.append({
            'path': route.path,
            'methods': list(route.methods),
            'name': route.name,
            'tags': route.tags
        })

# Agrupar por módulos (tags)
modules = {}
for route in routes:
    for tag in route['tags']:
        if tag not in modules:
            modules[tag] = []
        modules[tag].append(route)

# Mostrar resumen por módulo
for module, module_routes in sorted(modules.items()):
    print(f'📁 MÓDULO: {module.upper()}')
    print(f'   Endpoints: {len(module_routes)}')
    for route in sorted(module_routes, key=lambda x: x['path']):
        methods = ', '.join(sorted(route['methods'] - {'HEAD', 'OPTIONS'}))
        print(f'   {methods:12} {route["path"]}')
    print()

print(f'TOTAL DE ENDPOINTS: {len(routes)}')
print(f'TOTAL DE MÓDULOS: {len(modules)}')
