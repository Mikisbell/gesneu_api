# Pruebas de endpoints de la API GesNeu con token JWT válido
# Usando PowerShell para probar los endpoints según el esquema de BD

$BASE_URL = "http://127.0.0.1:8001"
$TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1Njc2NDM5OH0.1SC5ejRMgRyQE8HP26gLODxBsBKuhEznGfQR45BQez8"

$headers = @{
    'Authorization' = "Bearer $TOKEN"
    'Content-Type' = 'application/json'
}

function Test-Endpoint {
    param(
        [string]$Method,
        [string]$Endpoint,
        [string]$Description
    )
    
    $url = "$BASE_URL$Endpoint"
    Write-Host "`n============================================================" -ForegroundColor Yellow
    Write-Host "🔍 $Description" -ForegroundColor Cyan
    Write-Host "📍 $Method $Endpoint" -ForegroundColor White
    
    try {
        $response = Invoke-WebRequest -Uri $url -Method $Method -Headers $headers -TimeoutSec 10
        Write-Host "📊 Status: $($response.StatusCode)" -ForegroundColor Green
        
        if ($response.StatusCode -lt 400) {
            $content = $response.Content
            if ($content.Length -gt 500) {
                $content = $content.Substring(0, 500) + "... (truncado)"
            }
            Write-Host "✅ Respuesta exitosa:" -ForegroundColor Green
            Write-Host $content -ForegroundColor White
        }
    }
    catch {
        Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.Exception.Response) {
            Write-Host "Status Code: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
        }
    }
}

Write-Host "🚀 INICIANDO PRUEBAS DE API GESNEU CON TOKEN VÁLIDO" -ForegroundColor Green
Write-Host "🔑 Token: $($TOKEN.Substring(0,50))..." -ForegroundColor Yellow
Write-Host "🌐 Base URL: $BASE_URL" -ForegroundColor Yellow

# 1. Verificar estado del servidor
Test-Endpoint -Method "GET" -Endpoint "/" -Description "Verificar estado del servidor"

# 2. Verificar información del usuario actual
Test-Endpoint -Method "GET" -Endpoint "/api/v1/auth/me" -Description "Obtener información del usuario actual"

# 3. Probar endpoints de catálogos (según esquema BD)
Write-Host "`n=================================================================================" -ForegroundColor Magenta
Write-Host "📋 PROBANDO MÓDULO DE CATÁLOGOS" -ForegroundColor Magenta

Test-Endpoint -Method "GET" -Endpoint "/api/v1/catalogos/proveedores" -Description "Listar proveedores"
Test-Endpoint -Method "GET" -Endpoint "/api/v1/catalogos/almacenes" -Description "Listar almacenes"
Test-Endpoint -Method "GET" -Endpoint "/api/v1/catalogos/motivos-desecho" -Description "Listar motivos de desecho"
Test-Endpoint -Method "GET" -Endpoint "/api/v1/catalogos/parametros-inventario" -Description "Listar parámetros de inventario"

# 4. Probar endpoints de vehículos (según esquema BD)
Write-Host "`n=================================================================================" -ForegroundColor Magenta
Write-Host "🚗 PROBANDO MÓDULO DE VEHÍCULOS" -ForegroundColor Magenta

Test-Endpoint -Method "GET" -Endpoint "/api/v1/vehiculos" -Description "Listar vehículos"
Test-Endpoint -Method "GET" -Endpoint "/api/v1/vehiculos/tipos" -Description "Listar tipos de vehículo"

# 5. Probar endpoints de neumáticos (según esquema BD)
Write-Host "`n=================================================================================" -ForegroundColor Magenta
Write-Host "🛞 PROBANDO MÓDULO DE NEUMÁTICOS" -ForegroundColor Magenta

Test-Endpoint -Method "GET" -Endpoint "/api/v1/neumaticos" -Description "Listar neumáticos"
Test-Endpoint -Method "GET" -Endpoint "/api/v1/neumaticos/fabricantes" -Description "Listar fabricantes"
Test-Endpoint -Method "GET" -Endpoint "/api/v1/neumaticos/modelos" -Description "Listar modelos"

# 6. Probar endpoints de inventario (según esquema BD)
Write-Host "`n=================================================================================" -ForegroundColor Magenta
Write-Host "📦 PROBANDO MÓDULO DE INVENTARIO" -ForegroundColor Magenta

Test-Endpoint -Method "GET" -Endpoint "/api/v1/inventario/neumaticos" -Description "Consultar inventario"
Test-Endpoint -Method "GET" -Endpoint "/api/v1/inventario/movimientos" -Description "Consultar movimientos"

# 7. Probar endpoints de eventos (según esquema BD)
Write-Host "`n=================================================================================" -ForegroundColor Magenta
Write-Host "📅 PROBANDO MÓDULO DE EVENTOS" -ForegroundColor Magenta

Test-Endpoint -Method "GET" -Endpoint "/api/v1/eventos/neumaticos" -Description "Consultar eventos"
Test-Endpoint -Method "GET" -Endpoint "/api/v1/eventos/historial-estados" -Description "Consultar historial"

# 8. Probar endpoints de garantías (según esquema BD)
Write-Host "`n=================================================================================" -ForegroundColor Magenta
Write-Host "🛡️ PROBANDO MÓDULO DE GARANTÍAS" -ForegroundColor Magenta

Test-Endpoint -Method "GET" -Endpoint "/api/v1/garantias" -Description "Consultar garantías"

# 9. Probar endpoints de alertas (según esquema BD)
Write-Host "`n=================================================================================" -ForegroundColor Magenta
Write-Host "🚨 PROBANDO MÓDULO DE ALERTAS" -ForegroundColor Magenta

Test-Endpoint -Method "GET" -Endpoint "/api/v1/alertas" -Description "Consultar alertas"

Write-Host "`n=================================================================================" -ForegroundColor Green
Write-Host "🎯 PRUEBAS COMPLETADAS" -ForegroundColor Green
Write-Host "Revisa los resultados para identificar endpoints funcionales y problemas" -ForegroundColor Yellow
