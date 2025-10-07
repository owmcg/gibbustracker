# Gibraltar Bus Tracker - PowerShell Investigation Script
# This script uses built-in Windows PowerShell to investigate the bus tracking system

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
        
        # Look for potential coordinates in the content
        $coordPattern = '(-?\d+\.\d{4,})\s*,\s*(-?\d+\.\d{4,})'
        $coordinates = [regex]::Matches($response.Content, $coordPattern)
        
        if ($coordinates.Count -gt 0) {
            Write-Host "Found $($coordinates.Count) potential coordinate pairs:" -ForegroundColor Yellow
            foreach ($coord in $coordinates | Select-Object -First 5) {
                Write-Host "  $($coord.Value)" -ForegroundColor White
            }
        }
        
        # Look for JavaScript variables
        $jsVarPattern = 'var\s+\w+\s*=\s*[\[\{].*?[\]\}];'
        $jsVars = [regex]::Matches($response.Content, $jsVarPattern, [System.Text.RegularExpressions.RegexOptions]::Singleline)
        
        if ($jsVars.Count -gt 0) {
            Write-Host "Found $($jsVars.Count) JavaScript variables" -ForegroundColor Yellow
        }
        
        # Look for potential API endpoints
        $apiPattern = 'https?://[^\s''\"<>]+\.php[^\s''\"<>]*'
        $apis = [regex]::Matches($response.Content, $apiPattern)
        
        if ($apis.Count -gt 0) {
            Write-Host "Found $($apis.Count) potential API endpoints:" -ForegroundColor Yellow
            foreach ($api in $apis | Select-Object -First 3) {
                Write-Host "  $($api.Value)" -ForegroundColor White
            }
        }
        
        # Look for bus-related images
        $imgPattern = 'src=[''"`]([^''"`]*(?:bus|marker|icon)[^''"`]*)[''"`]'
        $images = [regex]::Matches($response.Content, $imgPattern, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
        
        if ($images.Count -gt 0) {
            Write-Host "Found $($images.Count) bus-related images" -ForegroundColor Yellow
        }
        
        # Create a summary for this route
        $summary = @{
            Route = $route
            URL = $url
            Status = $response.StatusCode
            ContentLength = $response.Content.Length
            Coordinates = $coordinates.Count
            JSVariables = $jsVars.Count
            APIEndpoints = $apis.Count
            BusImages = $images.Count
            Timestamp = (Get-Date).ToString()
        }
        
        $summary | ConvertTo-Json | Out-File -FilePath "$resultsDir\route_$route`_summary.json" -Encoding UTF8
        
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
Write-Host "Next steps:"
Write-Host "1. Check the HTML files in the results directory"
Write-Host "2. Look for patterns in the coordinate data"
Write-Host "3. Examine any JavaScript variables for bus data"
Write-Host "4. Test any discovered API endpoints"

# Try to open the results directory
try {
    Invoke-Item $resultsDir
    Write-Host "Results directory opened in File Explorer" -ForegroundColor Yellow
}
catch {
    Write-Host "Results directory: $(Get-Location)\$resultsDir" -ForegroundColor Yellow
}