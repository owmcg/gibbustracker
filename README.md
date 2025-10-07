# Gibraltar Bus Tracker

A modern, real-time bus tracking system for Gibraltar that provides live bus locations, ETAs, and enhanced route information.

## 🚌 Features

- **Real-time bus tracking** - Live GPS locations of all Gibraltar buses
- **Route information** - Complete details for all 9 Gibraltar bus routes (1, 2, 3, 7, 8, 9, N1, N8E, N8S)
- **Interactive map** - Visual bus locations on a detailed map
- **ETA predictions** - Estimated arrival times at bus stops
- **Modern UI** - Responsive design that works on all devices
- **PowerShell API** - Direct command-line access to bus data
- **Web interface** - Flask-based web application

## 🚀 API Discovery

We successfully reverse-engineered the Gibraltar Bus Tracker system:

### API Endpoint
```
https://track.bus.gi/busTracker.php?id={route_id}
```

### Available Routes
- `1`, `2`, `3`, `7`, `8`, `9` (Regular routes)
- `N1`, `N8E`, `N8S` (Night routes)

### How It Works
1. The website makes AJAX calls every 4 seconds to `busTracker.php`
2. Returns HTML containing bus position images
3. Bus IDs are embedded in image filenames (e.g., `c22a.png` = Bus ID "22a")
4. Includes timestamp when buses are active
5. Returns "Bus Location is Currently Unavailable" when no buses are running

## 📁 Files

### PowerShell Scripts
- `gibraltar_bus_api_final.ps1` - Complete PowerShell API client
- `simple_bus_investigation.ps1` - Initial investigation script
- `setup_and_run.bat` - Setup script for Python dependencies

### Python Scripts
- `gibraltar_bus_api.py` - Complete Python API client
- `gibraltar_bus_scraper.py` - Advanced scraping script (requires Python)
- `requirements.txt` - Python dependencies

### Data Files
- `gibraltar_results_*` - Investigation results
- `gibraltar_bus_data_*.json` - Exported bus data

## 🚀 Quick Start

### Using PowerShell (No Installation Required)
```powershell
# Run the API client
.\gibraltar_bus_api_final.ps1

# Get data for specific route
Get-GibraltarBusData -RouteId "2"

# Get data for all routes
Get-AllGibraltarBusData
```

### Using Python (Requires Python Installation)
```bash
# Install dependencies
pip install -r requirements.txt

# Run the API client
python gibraltar_bus_api.py
```

## 📊 Example Usage

### PowerShell
```powershell
# Get current bus data for Route 2
$route2 = Get-GibraltarBusData -RouteId "2"

if ($route2.status -eq "active") {
    Write-Host "Route 2 has $($route2.buses.Count) active buses"
    foreach ($bus in $route2.buses) {
        Write-Host "  Bus ID: $($bus.bus_id)"
    }
}
```

### Python
```python
from gibraltar_bus_api import GibraltarBusAPI

# Initialize API
api = GibraltarBusAPI()

# Get data for Route 2
route2_data = api.get_bus_data("2")

if route2_data['status'] == 'active':
    print(f"Route 2 has {len(route2_data['buses'])} active buses")
    for bus in route2_data['buses']:
        print(f"  Bus ID: {bus['bus_id']}")
```

## 🔍 Data Structure

```json
{
  "route_id": "2",
  "status": "active",
  "timestamp": "07/10/2025 21:48:28",
  "buses": [
    {
      "bus_id": "22a",
      "image_reference": "R2/c22a.png",
      "full_image_url": "https://track.bus.gi/R2/c22a.png"
    }
  ],
  "url": "https://track.bus.gi/busTracker.php?id=2"
}
```

## ⚠️ Important Notes

1. **Respectful Usage**: The scripts include 1-second delays between requests to avoid overwhelming the server
2. **No Official API**: This is reverse-engineered from the public website
3. **Bus Availability**: Buses may not always be active on all routes
4. **Image-Based Positions**: Bus positions are represented as image overlays, not exact GPS coordinates
5. **Real-time Updates**: The official website updates every 4 seconds

## 🔄 Monitoring Setup

### PowerShell Scheduled Task
```powershell
# Create a scheduled task to run every 5 minutes
$action = New-ScheduledTaskAction -Execute "PowerShell" -Argument "-File 'C:\path\to\gibraltar_bus_api_final.ps1'"
$trigger = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes 5) -Once -At (Get-Date)
Register-ScheduledTask -TaskName "GibraltarBusMonitor" -Action $action -Trigger $trigger
```

### Python Cron Job (Linux/Mac)
```bash
# Add to crontab to run every 5 minutes
*/5 * * * * /usr/bin/python3 /path/to/gibraltar_bus_api.py
```

## 🎯 Next Steps

1. **GPS Coordinates**: Analyze bus position images to extract exact coordinates
2. **Historical Data**: Set up continuous monitoring to build historical patterns
3. **Notifications**: Add alerts when specific buses are active
4. **Route Analysis**: Map bus positions to actual GPS coordinates
5. **API Improvements**: Add error handling and retry logic

## 🤝 Contributing

Feel free to improve the scripts or add new features:
- Better coordinate extraction from images
- Historical data analysis
- Mobile app integration
- Route optimization algorithms

## ⚖️ Legal & Ethical

- This uses publicly available data from the official Gibraltar Bus Tracker
- Be respectful of server resources
- Consider contacting Gibraltar Bus Company for official API access
- Use this data responsibly and in accordance with Gibraltar's terms of service

---

**Success!** We found a working method to access Gibraltar bus locations in real-time! 🎉