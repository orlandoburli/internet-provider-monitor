# 🌐 Internet Connection Monitor

Modern, professional internet connection monitoring system with real-time dashboard, PostgreSQL database storage, and comprehensive analytics. Built with React, Next.js, and amCharts for beautiful data visualization.

## ✨ Features

### Core Monitoring
- ✅ **Continuous Monitoring**: Checks internet connection at configurable intervals (default: 10s)
- 📊 **Multiple Tests**: Ping, HTTP/HTTPS, DNS resolution, and speed tests
- 🚀 **Speed Tests**: Download/upload speed with multiple providers (Speedtest.net, Cloudflare, OVH)
- 💾 **PostgreSQL Database**: All data stored for advanced analytics and historical analysis
- 📝 **Detailed Logs**: JSONL files with timestamps and complete test results
- 📄 **Automatic Reports**: Text and JSON reports generated every minute

### Modern Dashboard
- 🎨 **React + Next.js**: Modern, fast, component-based UI
- 📊 **amCharts 5**: Professional interactive charts with zoom/pan
- 🎯 **Shadcn UI**: Beautiful, accessible component library
- 🔄 **Real-Time Updates**: Auto-refresh every 5 seconds (toggle-able)
- 📅 **Period Filter**: Custom date and hour range selection
- 📱 **Responsive Design**: Works perfectly on mobile, tablet, and desktop
- 🌙 **Dark Mode Ready**: Shadcn UI with built-in dark mode support
- 📈 **REST API**: Full-featured API for custom integrations

### Analytics & Visualization
- 📈 **Timeline Chart**: Interactive success rate over time with zoom
- 🚀 **Speed History**: Multi-provider speed comparison charts
- 📊 **Statistics Cards**: Real-time uptime, success rate, outages
- 🎯 **Ping Analysis**: Per-host performance statistics
- ⚡ **Speed Statistics**: Min/max/average with provider breakdown
- 📉 **Outage Tracking**: Automatic detection and counting

### Configuration & Deployment
- ⚙️ **Fully Configurable**: JSON configuration file
- 🐳 **Docker Ready**: Fully containerized with PostgreSQL
- 🔒 **Secure**: All data stored locally, no external services
- 📦 **Production Ready**: Multi-stage builds, optimized images

---

## 🚀 Quick Start

### Prerequisites

- **Docker** and **Docker Compose**
  - macOS/Windows: [Docker Desktop](https://www.docker.com/get-started)
  - Linux: [Docker Engine](https://docs.docker.com/engine/install/)

### 1. Start the System

```bash
# Clone or navigate to project directory
cd project-telecom-anoing

# Start all services
docker compose up -d

# Check status
docker compose ps
```

**Services Started:**
- ✅ PostgreSQL database (port 5432)
- ✅ Internet monitor (background process)
- ✅ Dashboard API backend (port 8080)
- ✅ Dashboard frontend (port 3000)

### 2. Access the Dashboard

Open your browser and navigate to:

```
🌐 http://localhost:3000
```

**Dashboard Features:**
- 🟢 Real-time connection status
- 📊 Today's and 24h uptime statistics
- 📈 Interactive timeline chart
- 🚀 Speed test history with provider comparison
- 📍 Ping statistics by host
- 📅 Period filter (hour, day, week, month, custom)
- 🔄 Auto-refresh (5-second intervals)
- 📥 Export options (PDF, PNG, Print)

### 3. View Logs

```bash
# Monitor logs (real-time)
docker compose logs -f monitor

# Dashboard API logs
docker compose logs -f dashboard-api

# Frontend logs
docker compose logs -f dashboard-frontend

# All logs
docker compose logs -f
```

### 4. Generate Reports

Reports are automatically generated in `relatorios/` directory:

```bash
# View latest report
cat relatorios/relatorio_parcial_$(date +%Y-%m-%d).txt

# View detailed report
cat relatorios/relatorio_detalhado_$(date +%Y-%m-%d).txt

# View JSON report (API-friendly)
cat relatorios/relatorio_parcial_$(date +%Y-%m-%d).json
```

---

## 🎨 Dashboard

### Frontend (React + Next.js)

**Access:** `http://localhost:3000`

**Technology Stack:**
- ⚛️ **React 19** - Modern component-based UI
- ▲ **Next.js 16** - Server-side rendering and optimization
- 📊 **amCharts 5** - Professional interactive charts
- 🎨 **Shadcn UI** - Beautiful, accessible components
- 🎯 **Tailwind CSS** - Utility-first styling
- 📘 **TypeScript** - Type-safe development

**Dashboard Sections:**

1. **Period Filter Panel**
   - Quick select: Last Hour, Last 6h, Last 24h, Today, Yesterday, Last 7d, Last 30d
   - Custom date/hour range picker
   - Visual current range display

2. **Status Card**
   - Current online/offline status
   - Success rate percentage
   - Last check timestamp

3. **Statistics Cards**
   - Today's uptime percentage
   - Last 24h uptime
   - Outages count

4. **Timeline Chart** (amCharts)
   - Interactive line chart
   - Success rate over time
   - Zoom and pan functionality
   - Tooltip with details

5. **Recent Speed Tests**
   - Last 5 speed test results
   - Download/upload speeds
   - Provider and server info

6. **Speed History Chart** (amCharts)
   - Multi-line chart
   - All providers on same graph
   - Download (solid) and Upload (dashed) lines
   - Color-coded by provider
   - Interactive legend

7. **Speed Statistics**
   - Per-provider breakdown
   - Min/max/average speeds
   - Total test count
   - Ping statistics

8. **Ping Statistics**
   - Per-host performance
   - Success rate badges
   - Response time (min/avg/max)
   - Failed test tracking

### API Backend (Flask)

**Access:** `http://localhost:8080`

**REST API Endpoints:**

```bash
# Current Status
GET /api/status/current

# Statistics
GET /api/stats/today
GET /api/stats/last24h

# Timeline Data
GET /api/history/timeline?hours=24

# Speed Tests
GET /api/speed/current
GET /api/speed/stats?hours=24
GET /api/speed/history?hours=24

# Outages
GET /api/outages/recent?hours=24

# Ping Statistics
GET /api/ping/hosts?hours=24

# Health Check
GET /health
```

**Example API Call:**

```bash
# Get current status
curl http://localhost:8080/api/status/current

# Response
{
  "timestamp": "2026-01-07T15:30:00",
  "status": "online",
  "success_rate": 100.0,
  "date": "2026-01-07",
  "time": "15:30:00"
}
```

**CORS Enabled:** All endpoints support cross-origin requests.

---

## 📅 Period Filter

### Overview

Filter all dashboard data by custom date and hour ranges.

### Quick Period Options

- ⏱️ **Last Hour** - Past 60 minutes
- ⏱️ **Last 6 Hours** - Past 6 hours  
- ⏱️ **Last 24 Hours** - Past day (default)
- 📆 **Today** - From midnight to now
- 📆 **Yesterday** - Previous full day
- 📆 **Last 7 Days** - Past week
- 📆 **Last 30 Days** - Past month
- 🎯 **Custom** - Select exact date/hour range

### Custom Date/Hour Selection

**Precision Control:**
- 📅 Calendar picker for start/end dates
- 🕐 Hour selector (00:00 to 23:59)
- Visual range display

**Use Cases:**
- Investigate specific outage: "Yesterday 14:00 to 16:00"
- Business hours analysis: "Today 09:00 to 17:59"
- Weekend comparison: "Last Saturday vs Last Sunday"
- Monthly trends: "Last 30 Days"

**What Gets Filtered:**
- ✅ Timeline chart
- ✅ Speed history chart
- ✅ Speed statistics
- ✅ Ping statistics
- ✅ Outages count
- ✅ Chart titles (dynamic)

---

## ⚙️ Configuration

### config.json

```json
{
  "check_interval": 10,              // Seconds between checks
  "report_interval": 60,              // Seconds between report updates
  "enable_speed_tests": true,         // Enable/disable speed tests
  "enable_database": true,            // Enable/disable database storage
  
  "ping_hosts": [                     // Hosts for ping tests
    "8.8.8.8",
    "1.1.1.1",
    "google.com"
  ],
  
  "http_test_urls": [                 // URLs for HTTP tests
    "https://www.google.com",
    "https://www.cloudflare.com"
  ],
  
  "speed_test_providers": [           // Speed test providers
    "speedtest",
    "http_download"
  ],
  
  "http_download_urls": [             // URLs for download tests
    "https://speed.cloudflare.com/__down?bytes=10000000",
    "https://proof.ovh.net/files/10Mb.dat"
  ],
  
  "db_host": "postgres",
  "db_port": 5432,
  "db_name": "internet_monitor",
  "db_user": "monitor",
  "db_password": "monitor123"
}
```

### Recommended Settings

**Testing/Development:**
```json
{
  "check_interval": 10,
  "report_interval": 60,
  "enable_speed_tests": true
}
```

**Production:**
```json
{
  "check_interval": 60,
  "report_interval": 300,
  "enable_speed_tests": true
}
```

**Apply Configuration Changes:**
```bash
docker compose restart monitor
```

---

## 💾 Database

### PostgreSQL Schema

**Tables:**

1. **`connection_checks`** - Main verification results
   - timestamp, date, time
   - connection_status (online/offline)
   - success_rate

2. **`ping_tests`** - Ping test results
   - host, success
   - response_time_ms

3. **`http_tests`** - HTTP/HTTPS tests
   - url, success
   - response_code, response_time_ms

4. **`dns_tests`** - DNS resolution tests
   - domain, success
   - resolved_ips

5. **`speed_tests`** - Speed test results
   - provider, success
   - download_mbps, upload_mbps, ping_ms
   - server_name, server_location

### Useful Queries

#### Today's Uptime

```sql
SELECT 
    COUNT(*) as total_checks,
    SUM(CASE WHEN connection_status = 'online' THEN 1 ELSE 0 END) as online_checks,
    ROUND(
        (SUM(CASE WHEN connection_status = 'online' THEN 1 ELSE 0 END)::DECIMAL / COUNT(*)) * 100,
        2
    ) as uptime_percentage
FROM connection_checks
WHERE date = CURRENT_DATE;
```

#### Average Speed (Last 24h)

```sql
SELECT 
    provider,
    COUNT(*) as total_tests,
    ROUND(AVG(download_mbps), 2) as avg_download,
    ROUND(AVG(upload_mbps), 2) as avg_upload,
    ROUND(MIN(download_mbps), 2) as min_download,
    ROUND(MAX(download_mbps), 2) as max_download
FROM speed_tests st
JOIN connection_checks cc ON st.check_id = cc.id
WHERE 
    st.success = true
    AND cc.timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY provider;
```

#### Connection Issues Today

```sql
SELECT 
    timestamp,
    connection_status,
    success_rate
FROM connection_checks
WHERE 
    connection_status = 'offline'
    AND date = CURRENT_DATE
ORDER BY timestamp DESC;
```

#### Hourly Success Rate

```sql
SELECT 
    DATE_TRUNC('hour', timestamp) as hour,
    ROUND(AVG(success_rate), 2) as avg_success_rate,
    COUNT(*) as checks
FROM connection_checks
WHERE date = CURRENT_DATE
GROUP BY hour
ORDER BY hour;
```

### Database Access

```bash
# Connect to PostgreSQL
docker compose exec postgres psql -U monitor -d internet_monitor

# Run query
docker compose exec postgres psql -U monitor -d internet_monitor -c "SELECT COUNT(*) FROM connection_checks;"

# View tables
docker compose exec postgres psql -U monitor -d internet_monitor -c "\dt"
```

### Backup & Restore

```bash
# Create backup
docker compose exec postgres pg_dump -U monitor internet_monitor > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
cat backup_20260107_153000.sql | docker compose exec -i postgres psql -U monitor -d internet_monitor

# Backup with compression
docker compose exec postgres pg_dump -U monitor internet_monitor | gzip > backup_$(date +%Y%m%d).sql.gz
```

---

## 📁 Project Structure

```
project-telecom-anoing/
│
├── Backend (Python)
│   ├── monitor_internet.py       # Main monitoring script
│   ├── generate_report.py        # Report generator
│   ├── database.py               # Database manager
│   ├── dashboard.py              # Flask API server
│   ├── config.json               # Configuration
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile                # Backend container
│   └── init-db.sql              # Database schema
│
├── Frontend (React/Next.js)
│   ├── app/
│   │   ├── page.tsx             # Main dashboard page
│   │   ├── layout.tsx           # Root layout
│   │   └── globals.css          # Global styles
│   ├── components/
│   │   ├── ui/                  # Shadcn UI components
│   │   ├── TimelineChart.tsx   # Timeline visualization
│   │   ├── SpeedHistoryChart.tsx # Speed chart
│   │   └── DateTimeFilter.tsx  # Period filter
│   ├── lib/
│   │   ├── api-client.ts       # API client + types
│   │   └── utils.ts            # Utilities
│   ├── Dockerfile              # Frontend container
│   ├── package.json            # Dependencies
│   └── next.config.ts          # Next.js config
│
├── Docker
│   └── docker-compose.yml       # Service orchestration
│
├── Data (auto-generated)
│   ├── logs/                    # JSONL log files
│   │   └── log_YYYY-MM-DD.jsonl
│   └── relatorios/              # Generated reports
│       ├── relatorio_parcial_*.txt
│       ├── relatorio_detalhado_*.txt
│       └── relatorio_parcial_*.json
│
└── Documentation
    ├── README.md                # This file
    ├── FRONTEND_MIGRATION.md   # Migration details
    └── FILTER_FEATURE.md       # Filter documentation
```

---

## 🐳 Docker Commands

### Service Management

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# Restart specific service
docker compose restart monitor
docker compose restart dashboard-api
docker compose restart dashboard-frontend

# View logs
docker compose logs -f monitor
docker compose logs -f dashboard-api
docker compose logs -f dashboard-frontend

# Check status
docker compose ps

# View resource usage
docker compose stats
```

### Rebuild After Changes

```bash
# Rebuild backend
docker compose build dashboard-api monitor

# Rebuild frontend
docker compose build dashboard-frontend

# Rebuild everything
docker compose build

# Restart with new images
docker compose down
docker compose up -d
```

### Database Operations

```bash
# Connect to database
docker compose exec postgres psql -U monitor -d internet_monitor

# Backup database
docker compose exec postgres pg_dump -U monitor internet_monitor > backup.sql

# View tables
docker compose exec postgres psql -U monitor -d internet_monitor -c "\dt"

# Check database size
docker compose exec postgres psql -U monitor -d internet_monitor -c "SELECT pg_size_pretty(pg_database_size('internet_monitor'));"
```

### Cleanup

```bash
# Remove old logs (keep last 30 days)
find logs/ -name "*.jsonl" -mtime +30 -delete

# Clean old database data
docker compose exec postgres psql -U monitor -d internet_monitor -c "DELETE FROM connection_checks WHERE date < CURRENT_DATE - INTERVAL '90 days';"

# Remove unused Docker resources
docker system prune -a
```

---

## 🛠️ Development

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server (port 3000)
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Type checking
npm run type-check

# Linting
npm run lint
```

### Backend Development

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run monitor (local development)
python monitor_internet.py

# Run dashboard API
python dashboard.py

# Generate report manually
python generate_report.py
```

### Environment Variables

**Frontend** (`.env.local`):
```bash
NEXT_PUBLIC_API_URL=http://localhost:8080
```

**Backend** (Docker environment):
```yaml
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=internet_monitor
POSTGRES_USER=monitor
POSTGRES_PASSWORD=monitor123
PYTHONUNBUFFERED=1
```

---

## 📊 Monitoring & Analytics

### Grafana Integration

**Data Source Setup:**
- Type: PostgreSQL
- Host: `localhost:5432`
- Database: `internet_monitor`
- User: `monitor`
- Password: `monitor123`
- SSL Mode: disable

**Example Panels:**

1. **Uptime Gauge:**
```sql
SELECT 
    (SUM(CASE WHEN connection_status = 'online' THEN 1 ELSE 0 END)::DECIMAL / COUNT(*)) * 100 as uptime
FROM connection_checks
WHERE timestamp >= NOW() - INTERVAL '24 hours';
```

2. **Speed Over Time:**
```sql
SELECT 
    cc.timestamp as time,
    st.provider,
    st.download_mbps
FROM speed_tests st
JOIN connection_checks cc ON st.check_id = cc.id
WHERE 
    st.success = true
    AND cc.timestamp >= NOW() - INTERVAL '7 days'
ORDER BY cc.timestamp;
```

### Python API Integration

```python
import requests

# Get current status
response = requests.get('http://localhost:8080/api/status/current')
status = response.json()
print(f"Status: {status['status']}, Success Rate: {status['success_rate']}%")

# Get speed statistics
response = requests.get('http://localhost:8080/api/speed/stats?hours=24')
speeds = response.json()
for provider in speeds:
    print(f"{provider['provider']}: {provider['avg_download']} Mbps")
```

### Custom Alerts

```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="internet_monitor",
    user="monitor",
    password="monitor123"
)

cursor = conn.cursor()
cursor.execute("""
    SELECT COUNT(*) FROM connection_checks
    WHERE 
        connection_status = 'offline'
        AND timestamp >= NOW() - INTERVAL '1 hour'
""")

outages = cursor.fetchone()[0]
if outages > 5:
    print(f"ALERT: {outages} outages in last hour!")
    # Send notification (email, SMS, webhook, etc.)

conn.close()
```

---

## 🚨 Troubleshooting

### Frontend Issues

**Dashboard not loading:**
```bash
# Check frontend logs
docker compose logs dashboard-frontend

# Rebuild frontend
docker compose build dashboard-frontend
docker compose restart dashboard-frontend

# Check if port 3000 is available
lsof -ti:3000
```

**API connection errors:**
```bash
# Check API health
curl http://localhost:8080/health

# Check CORS headers
curl -I http://localhost:8080/api/status/current

# Verify API is running
docker compose ps dashboard-api
```

### Backend Issues

**Monitor not collecting data:**
```bash
# Check monitor logs
docker compose logs --tail=50 monitor

# Test manually
docker compose run --rm monitor python monitor_internet.py

# Verify config.json
cat config.json | python -m json.tool
```

**Database connection errors:**
```bash
# Check PostgreSQL status
docker compose ps postgres

# Check PostgreSQL logs
docker compose logs postgres

# Test connection
docker compose exec postgres psql -U monitor -d internet_monitor -c "SELECT 1;"
```

**Speed tests not running:**
```bash
# Verify config
cat config.json | grep enable_speed_tests

# Check monitor logs for speed test messages
docker compose logs monitor | grep -i speed

# Test speed test manually
docker compose exec monitor python -c "from monitor_internet import *; test_download_speed('https://speed.cloudflare.com/__down?bytes=10000000')"
```

### Performance Issues

**Dashboard slow:**
```bash
# Check auto-refresh setting (reduce interval if needed)
# Clear browser cache
# Check API response times:
time curl http://localhost:8080/api/status/current
```

**Database slow:**
```bash
# Check database size
docker compose exec postgres psql -U monitor -d internet_monitor -c "
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"

# Vacuum database
docker compose exec postgres psql -U monitor -d internet_monitor -c "VACUUM ANALYZE;"

# Clean old data (keep last 90 days)
docker compose exec postgres psql -U monitor -d internet_monitor -c "
DELETE FROM connection_checks WHERE date < CURRENT_DATE - INTERVAL '90 days';
"
```

### Container Issues

**Container keeps restarting:**
```bash
# Check exit code and errors
docker compose logs --tail=100 monitor

# Check system resources
docker compose stats

# Verify Docker has enough memory/disk
docker system df
```

**Port already in use:**
```bash
# Find process using port
lsof -ti:3000  # Frontend
lsof -ti:8080  # API
lsof -ti:5432  # PostgreSQL

# Kill process
lsof -ti:8080 | xargs kill -9

# Or change port in docker-compose.yml
```

---

## 📈 Performance Optimization

### Database

- **Indexes:** Already optimized with indexes on timestamp, date, and status
- **Partitioning:** Consider partitioning `connection_checks` by date for very large datasets
- **Retention:** Delete data older than 90-180 days to maintain performance

### Frontend

- **Production Build:** Uses Next.js standalone mode for minimal image size
- **Static Generation:** Pre-renders pages for fast initial load
- **Code Splitting:** Automatic code splitting per route
- **Image Optimization:** Automatic image optimization with Next.js

### Monitoring

- **Check Interval:** Increase to 60-300 seconds for production
- **Speed Tests:** Disable or reduce frequency if bandwidth is limited
- **Auto-Refresh:** Can be disabled in dashboard if not needed

---

## 📝 Notes

### Important Information

- ⚠️ **Speed tests consume bandwidth** (~10-30MB per test)
- 📱 **Works with any connection type** (cable, fiber, 4G/5G, satellite)
- 🔒 **All data stored locally** - no external services required
- 🌍 **Uses trusted servers** (Google, Cloudflare, Speedtest.net)
- 💾 **Database grows over time** - monitor disk usage
- 🔄 **Auto-restart enabled** - services restart on failure

### Best Practices

1. **Regular Backups:** Backup database weekly
2. **Monitor Disk Space:** Keep at least 10GB free
3. **Update Dependencies:** Rebuild images monthly for security updates
4. **Review Logs:** Check logs weekly for errors
5. **Clean Old Data:** Delete data older than 90 days

---

## 📋 Changelog

### Version 3.0 (Current) - January 2026
- ✅ **Complete frontend rebuild** with React + Next.js + amCharts
- ✅ **Modern UI** with Shadcn UI component library
- ✅ **Period filter** with date and hour range selection
- ✅ **Professional charts** with amCharts 5 (zoom, pan, interactive)
- ✅ **TypeScript** for type-safe development
- ✅ **REST API** with CORS support
- ✅ **Two-service architecture** (API + Frontend)
- ✅ **Responsive design** for mobile/tablet/desktop
- ✅ **Dark mode ready** with Shadcn UI

### Version 2.1 - December 2025
- ✅ PostgreSQL database integration
- ✅ Speed tests on every check
- ✅ Automatic report generation
- ✅ Real-time web dashboard (Flask + Bootstrap)
- ✅ Fixed Python buffering in Docker
- ✅ Improved logging output

### Version 2.0 - 2025
- ✅ Automatic reports every 5 minutes
- ✅ Speed tests with multiple providers
- ✅ Docker support

### Version 1.0 - 2024
- ✅ Initial release
- ✅ Basic monitoring (ping, HTTP, DNS)
- ✅ Manual report generation

---

## 🎯 Roadmap

### Planned Features

- [ ] **Notifications:** Email/SMS/webhook alerts for outages
- [ ] **Mobile App:** React Native mobile app
- [ ] **Comparison Mode:** Compare two time periods side-by-side
- [ ] **Export Enhanced:** Export filtered data as CSV
- [ ] **Time Zones:** User-selectable timezone display
- [ ] **Saved Filters:** Save and recall favorite date ranges
- [ ] **Advanced Analytics:** ML-based anomaly detection
- [ ] **Multi-location:** Monitor from multiple locations
- [ ] **SLA Tracking:** Automatic SLA compliance reports

---

## 🤝 Contributing

Contributions, suggestions, and improvements are welcome!

### How to Contribute

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Areas for Contribution

- Additional chart types
- New dashboard features
- Performance optimizations
- Documentation improvements
- Bug fixes
- New test providers
- Notification integrations

---

## 📄 License

Open source - free to use and modify.

---

## 🙏 Acknowledgments

- **React Team** - For the amazing framework
- **Vercel** - For Next.js
- **amCharts** - For professional charting library
- **Shadcn** - For beautiful UI components
- **PostgreSQL** - For robust database
- **Docker** - For containerization

---

## 📞 Support

### Documentation

- Main README: This file
- Frontend Migration: `FRONTEND_MIGRATION.md`
- Filter Feature: `FILTER_FEATURE.md`

### Quick Links

- Frontend: http://localhost:3000
- API: http://localhost:8080
- API Health: http://localhost:8080/health
- Database: localhost:5432

---

**Developed to help document and analyze internet connection quality** 🚀

**Built with ❤️ using React, Next.js, amCharts, and PostgreSQL**
