# Script de diagnóstico completo para API GesNeu
# Usando PowerShell para evitar problemas de dependencias Python

$BASE_URL = "http://127.0.0.1:8001"
$TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1Njc2NDM5OH0.1SC5ejRMgRyQE8HP26gLODxBsBKuhEznGfQR45BQez8"

$headers = @{
    'Authorization' = "Bearer $TOKEN"
    'Content-Type' = 'application/json'
}

function Test-Endpoint {
    param(
        [string]$Endpoint,
        [string]$Description
    )
    
    $url = "$BASE_URL$Endpoint"
    
    try {
        $response = Invoke-WebRequest -Uri $url -Method GET -Headers $headers -TimeoutSec 10 -ErrorAction Stop
        $status = "✅"
        $statusCode = $response.StatusCode
        
        # Intentar parsear JSON para obtener información
        try {
            $json = $response.Content | ConvertFrom-Json
            if ($json -is [array]) {
                $info = "$($json.Count) registros"
            } elseif ($json -is [object]) {
                $info = "$($json.PSObject.Properties.Count) campos"
            } else {
                $info = "OK"
            }
        } catch {
            $info = "OK (no JSON)"
        }
        
        Write-Host "$status $Endpoint - $statusCode - $Description" -ForegroundColor Green
        Write-Host "   Datos: $info" -ForegroundColor Gray
        
    } catch {
        $status = "❌"
        $statusCode = $_.Exception.Response.StatusCode.value__
        $errorMessage = $_.Exception.Message
        
        Write-Host "$status $Endpoint - $statusCode - $Description" -ForegroundColor Red
        
        # Intentar obtener el cuerpo del error
        try {
            $errorBody = $_.Exception.Response.GetResponseStream()
            $reader = New-Object System.IO.StreamReader($errorBody)
            $errorContent = $reader.ReadToEnd()
            Write-Host "   Error: $($errorContent.Substring(0, [Math]::Min(150, $errorContent.Length)))" -ForegroundColor Red
        } catch {
            Write-Host "   Error: $errorMessage" -ForegroundColor Red
        }
    }
}

function Test-DatabaseConnection {
    Write-Host "`n🔍 VERIFICANDO CONEXIÓN A BASE DE DATOS" -ForegroundColor Yellow
    Write-Host "=" * 50 -ForegroundColor Yellow
    
    # Verificar si PostgreSQL está ejecutándose
    try {
        $pgService = Get-Service -Name "*postgresql*" -ErrorAction SilentlyContinue
        if ($pgService) {
            Write-Host "✅ Servicio PostgreSQL encontrado: $($pgService.Name) - $($pgService.Status)" -ForegroundColor Green
        } else {
            Write-Host "❌ Servicio PostgreSQL no encontrado" -ForegroundColor Red
        }
    } catch {
        Write-Host "⚠️ No se pudo verificar el servicio PostgreSQL" -ForegroundColor Yellow
    }
    
    # Verificar puerto 5432
    try {
        $connection = Test-NetConnection -ComputerName localhost -Port 5432 -WarningAction SilentlyContinue
        if ($connection.TcpTestSucceeded) {
            Write-Host "✅ Puerto 5432 está abierto (PostgreSQL escuchando)" -ForegroundColor Green
        } else {
            Write-Host "❌ Puerto 5432 no está disponible" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Error verificando puerto 5432" -ForegroundColor Red
    }
}

function Main {
    Write-Host "🚀 DIAGNÓSTICO COMPLETO API GESNEU" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host "🔑 Token: $($TOKEN.Substring(0,50))..." -ForegroundColor Yellow
    Write-Host "🌐 Base URL: $BASE_URL" -ForegroundColor Yellow
    
    # 1. Verificar conectividad básica
    Write-Host "`n1. TEST DE CONECTIVIDAD BÁSICA" -ForegroundColor Magenta
    Test-Endpoint "/" "Ruta raíz"
    Test-Endpoint "/health" "Health check"
    Test-Endpoint "/docs" "Documentación OpenAPI"
    
    # 2. Verificar autenticación
    Write-Host "`n2. TEST DE AUTENTICACIÓN" -ForegroundColor Magenta
    Test-Endpoint "/api/v1/auth/me" "Información del usuario"
    
    # 3. Verificar módulos principales
    Write-Host "`n3. MÓDULOS PRINCIPALES" -ForegroundColor Magenta
    Test-Endpoint "/api/v1/catalogos/proveedores" "Catálogos - Proveedores"
    Test-Endpoint "/api/v1/vehiculos" "Vehículos"
    Test-Endpoint "/api/v1/neumaticos" "Neumáticos"
    
    # 4. Verificar base de datos
    Test-DatabaseConnection
    
    # 5. Verificar logs del servidor
    Write-Host "`n🔍 VERIFICANDO LOGS DEL SERVIDOR" -ForegroundColor Yellow
    Write-Host "=" * 50 -ForegroundColor Yellow
    Write-Host "💡 Revisa la consola donde está ejecutándose uvicorn para ver errores detallados" -ForegroundColor Yellow
    Write-Host "💡 Los errores 500 generalmente indican problemas de BD o modelos" -ForegroundColor Yellow
    
    Write-Host "`n" + "=" * 60 -ForegroundColor Cyan
    Write-Host "🎯 DIAGNÓSTICO COMPLETADO" -ForegroundColor Cyan
    Write-Host "💡 Revisa los resultados arriba para identificar problemas específicos" -ForegroundColor Yellow
}

# Ejecutar diagnóstico
Main
