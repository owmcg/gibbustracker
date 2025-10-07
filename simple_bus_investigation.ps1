# Gibraltar Bus Tracker - Simple PowerShell Investigation
Write-Host "Gibraltar Bus Tracker Investigation" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

# Available routes
$routes = @('1', '2', '3', '7', '8', '9', 'N1', 'N8E', 'N8S')
$baseUrl = "https://track.bus.gi"

# Create results directory
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$resultsDir = "gibraltar_results_$timestamp"
New-Item -ItemType Directory -Path $resultsDir -Force | Out-Null

Write-Host "Created results directory: $resultsDir" -ForegroundColor Yellow

foreach ($route in $routes) {
    Write-Host "`nTesting Route $route..." -ForegroundColor Cyan
    
    $url = "$baseUrl/displayRoute.php?id=$route&sys=1"
    Write-Host "URL: $url"
    
    try {
        # Make the web request
        $response = Invoke-WebRequest -Uri $url -UserAgent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" -TimeoutSec 10
        
        Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
        Write-Host "Content Length: $($response.Content.Length) characters"
        
        # Save the response to a file
        $filename = "$resultsDir\route_$route.html"
        $response.Content | Out-File -FilePath $filename -Encoding UTF8
        
        # Simple content analysis
        $content = $response.Content
        
        # Look for decimal numbers that could be coordinates
        if ($content -match "\d+\.\d{4,}") {
            Write-Host "Found potential coordinate data" -ForegroundColor Yellow
        }
        
        # Look for common bus tracking terms
        $trackingTerms = @("latitude", "longitude", "lat", "lng", "GPS", "position", "location", "bus")
        $foundTerms = @()
        foreach ($term in $trackingTerms) {
            if ($content -match $term) {
                $foundTerms += $term
            }
        }
        
        if ($foundTerms.Count -gt 0) {
            Write-Host "Found tracking-related terms: $($foundTerms -join ', ')" -ForegroundColor Yellow
        }
        
        # Look for JavaScript content
        if ($content -match "<script") {
            Write-Host "Contains JavaScript code" -ForegroundColor Yellow
        }
        
        # Look for potential API calls
        if ($content -match "\.php") {
            Write-Host "Contains PHP endpoint references" -ForegroundColor Yellow
        }
        
        # Create a simple summary
        $summary = @{
            Route = $route
            URL = $url
            Status = $response.StatusCode
            ContentLength = $response.Content.Length
            HasCoordinates = ($content -match "\d+\.\d{4,}")
            HasJavaScript = ($content -match "<script")
            HasPHPEndpoints = ($content -match "\.php")
            TrackingTerms = ($foundTerms -join ', ')
            Timestamp = (Get-Date).ToString()
        }
        
        $summary | ConvertTo-Json | Out-File -FilePath "$resultsDir\route_$route`_summary.json" -Encoding UTF8
        
        Write-Host "Data saved for Route $route" -ForegroundColor Green
        
    }
    catch {
        Write-Host "Error accessing route $route`: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Be respectful to the server
    Start-Sleep -Seconds 1
}

Write-Host "`n" -NoNewline
Write-Host "Investigation Complete!" -ForegroundColor Green
Write-Host "========================" -ForegroundColor Green
Write-Host "Results saved in: $resultsDir"
Write-Host ""
Write-Host "To analyze the results:"
Write-Host "1. Check the HTML files in the results directory"
Write-Host "2. Look for coordinate patterns"
Write-Host "3. Examine JavaScript code for bus data"
Write-Host ""

# List the files created
Write-Host "Files created:" -ForegroundColor Cyan
Get-ChildItem $resultsDir | ForEach-Object { Write-Host "  $($_.Name)" }

# Try to open the results directory
try {
    Start-Process explorer.exe $resultsDir
    Write-Host "`nResults directory opened in File Explorer" -ForegroundColor Yellow
}
catch {
    Write-Host "`nResults directory: $(Get-Location)\$resultsDir" -ForegroundColor Yellow
}