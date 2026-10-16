# Launch all backend services in separate PowerShell windows.

$root = "C:\Project\doc-intel-agent"

if (-not (Test-Path $root)) {
    Write-Host "ERROR: Project root not found at $root" -ForegroundColor Red
    exit 1
}

Set-Location $root

$services = @(
    @{ name = "API Gateway";     port = 8000; module = "services.api.app.main:app" },
    @{ name = "CV Service";      port = 8001; module = "services.cv_service.app.main:app" },
    @{ name = "NLP Service";     port = 8002; module = "services.nlp_service.app.main:app" },
    @{ name = "RAG Service";     port = 8003; module = "services.rag_service.app.main:app" },
    @{ name = "Summary Service"; port = 8005; module = "services.summary_service.app.main:app" },
    @{ name = "Prompt Service";  port = 8006; module = "services.prompt_service.app.main:app" }
)

Write-Host "Launching $($services.Count) services..." -ForegroundColor Cyan

foreach ($svc in $services) {
    $cmd = "cd '$root'; Write-Host '=== $($svc.name) :$($svc.port) ===' -ForegroundColor Green; uvicorn $($svc.module) --port $($svc.port)"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd
    Write-Host "  Started $($svc.name) on port $($svc.port)"
    Start-Sleep -Seconds 1
}

Write-Host ""
Write-Host "All services launched. Wait 15 seconds, then test:" -ForegroundColor Green
Write-Host "  curl.exe http://localhost:8000/health"