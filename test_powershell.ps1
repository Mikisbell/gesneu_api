# Test PowerShell para endpoints
$token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1Njc1MTExM30._N4mycyYTHbpI5s2tTozOTlIW0y2aI7vrYX7kwF40hg"
$headers = @{"Authorization" = "Bearer $token"}

Write-Host "🔍 PRUEBAS ENDPOINTS CORREGIDOS" -ForegroundColor Cyan
Write-Host ""

# Test endpoints
$endpoints = @(
    @{url="http://localhost:8001/api/v1/vehiculos/"; name="Vehículos"},
    @{url="http://localhost:8001/api/v1/neumaticos/modelos/"; name="Modelos neumáticos"},
    @{url="http://localhost:8001/api/v1/bitacoras/operaciones/"; name="Bitácoras operaciones"},
    @{url="http://localhost:8001/api/v1/sistema/rutas/"; name="Sistema rutas"},
    @{url="http://localhost:8001/api/v1/sistema/tipos-ruta/"; name="Sistema tipos-ruta"}
)

foreach ($endpoint in $endpoints) {
    try {
        $response = Invoke-WebRequest -Uri $endpoint.url -Headers $headers -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ $($endpoint.name): $($response.StatusCode)" -ForegroundColor Green
        } else {
            Write-Host "❌ $($endpoint.name): $($response.StatusCode)" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "❌ $($endpoint.name): ERROR - $($_.Exception.Message)" -ForegroundColor Red
    }
}
