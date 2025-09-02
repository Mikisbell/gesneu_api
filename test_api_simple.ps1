# Simple API test script
$baseUrl = "http://127.0.0.1:8001"
$token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcyNTIzNzYwMH0.4lQvzJhKOaUJVhqGCJBYQHxJNGJhZGE2ZGE2ZGE2ZGE2"
$headers = @{
    'Authorization' = "Bearer $token"
    'Content-Type' = 'application/json'
}

Write-Host "🚀 Testing GesNeu API Endpoints" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Test basic connectivity
Write-Host "`n📡 Testing Basic Connectivity:" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/" -Method GET -TimeoutSec 10
    Write-Host "✅ API Root: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ API Root: $($_.Exception.Message)" -ForegroundColor Red
}

# Test catalog endpoints
Write-Host "`n📦 Testing Catalog Endpoints:" -ForegroundColor Yellow

$endpoints = @(
    @{Name="Proveedores"; Url="/api/v1/catalogos/proveedores"},
    @{Name="Almacenes"; Url="/api/v1/catalogos/almacenes"},
    @{Name="Motivos Desecho"; Url="/api/v1/catalogos/motivos-desecho"},
    @{Name="Parametros Inventario"; Url="/api/v1/catalogos/parametros-inventario"}
)

foreach ($endpoint in $endpoints) {
    try {
        $response = Invoke-WebRequest -Uri "$baseUrl$($endpoint.Url)" -Headers $headers -Method GET -TimeoutSec 10
        Write-Host "✅ $($endpoint.Name): $($response.StatusCode)" -ForegroundColor Green
        
        # Try to parse JSON response
        try {
            $json = $response.Content | ConvertFrom-Json
            if ($json -is [array]) {
                Write-Host "   📊 Returned $($json.Count) items" -ForegroundColor Cyan
            } else {
                Write-Host "   📋 Response type: $($json.GetType().Name)" -ForegroundColor Cyan
            }
        } catch {
            Write-Host "   📄 Response length: $($response.Content.Length) chars" -ForegroundColor Cyan
        }
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "❌ $($endpoint.Name): $statusCode - $($_.Exception.Message)" -ForegroundColor Red
        
        if ($_.Exception.Response) {
            try {
                $errorContent = $_.Exception.Response.GetResponseStream()
                $reader = New-Object System.IO.StreamReader($errorContent)
                $errorText = $reader.ReadToEnd()
                Write-Host "   📄 Error details: $($errorText.Substring(0, [Math]::Min(200, $errorText.Length)))" -ForegroundColor Red
            } catch {
                Write-Host "   📄 Could not read error details" -ForegroundColor Red
            }
        }
    }
}

Write-Host "`n=================================" -ForegroundColor Green
Write-Host "✅ Test completed!" -ForegroundColor Green
