# 🌐 Internet Connection Monitor

Sistema completo de monitoramento de conexão de internet com armazenamento em banco de dados PostgreSQL e geração automática de relatórios para documentar problemas com provedores de internet.

## ✨ Features

- ✅ **Continuous Monitoring**: Checks internet connection at configurable intervals
- 📊 **Multiple Tests**: Ping, HTTP/HTTPS, DNS resolution, and speed tests
- 🚀 **Speed Tests**: Download/upload speed with multiple providers (Speedtest.net, Cloudflare, OVH)
- 💾 **PostgreSQL Database**: All data stored in relational database for advanced analytics
- 📝 **Detailed Logs**: JSONL files with timestamps and results
- 📄 **Automatic Reports**: Generates reports automatically every minute
- 📈 **Dashboards**: Connect Grafana, Metabase, or Superset for real-time visualization
- ⚙️ **Configurable**: Easy customization through JSON config file
- 🐳 **Docker Ready**: Fully containerized with PostgreSQL included

---

## 🚀 Quick Start

### Prerequisites

- **Docker** and **Docker Compose**
  - macOS/Windows: [Docker Desktop](https://www.docker.com/get-started)
  - Linux: [Docker Engine](https://docs.docker.com/engine/install/)

### 1. Start the System

```bash
# Start all services (PostgreSQL + Monitor)
docker compose up -d

# Check logs
docker compose logs -f monitor
```

That's it! The system is now:
- ✅ Monitoring your connection every 10 seconds (configurable)
- ✅ Saving data to PostgreSQL database
- ✅ Generating automatic reports
- ✅ Running 24/7 in the background

### 2. View Reports

Reports are automatically generated in the `relatorios/` directory:

```bash
# View latest partial report
cat relatorios/relatorio_parcial_$(date +%Y-%m-%d).txt

# View detailed report
cat relatorios/relatorio_detalhado_$(date +%Y-%m-%d).txt
```

### 3. Access Database

```bash
# Connect to PostgreSQL
docker compose exec postgres psql -U monitor -d internet_monitor

# Example query: Check today's uptime
SELECT 
    COUNT(*) as total_checks,
    ROUND(AVG(success_rate), 2) as avg_success_rate
FROM connection_checks
WHERE date = CURRENT_DATE;
```

---

## ⚙️ Configuration

Edit `config.json` to customize behavior:

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
  
  "db_host": "postgres",              // Database host
  "db_port": 5432,
  "db_name": "internet_monitor",
  "db_user": "monitor",
  "db_password": "monitor123"
}
```

### Recommended Settings

**For Testing:**
- `check_interval`: 10-30 seconds
- `report_interval`: 60 seconds
- `enable_speed_tests`: true

**For Production:**
- `check_interval`: 60-300 seconds
- `report_interval`: 300-600 seconds
- `enable_speed_tests`: true (or false to save bandwidth)

**After changing config:**
```bash
docker compose restart monitor
```

---

## 💾 Database

### Structure

The system creates 5 tables in PostgreSQL:

1. **`connection_checks`** - Main verification results
2. **`ping_tests`** - Ping test results (8.8.8.8, 1.1.1.1, etc.)
3. **`http_tests`** - HTTP/HTTPS test results
4. **`dns_tests`** - DNS resolution tests
5. **`speed_tests`** - Speed test results (download/upload)

### Useful SQL Queries

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

#### Average Speed (Last 24 hours)

```sql
SELECT 
    provider,
    COUNT(*) as total_tests,
    ROUND(AVG(download_mbps), 2) as avg_download,
    ROUND(AVG(upload_mbps), 2) as avg_upload,
    ROUND(MIN(download_mbps), 2) as min_download,
    ROUND(MAX(download_mbps), 2) as max_download
FROM speed_tests
WHERE 
    success = true
    AND created_at >= NOW() - INTERVAL '24 hours'
GROUP BY provider;
```

#### Connection Issues

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

### Database Backup

```bash
# Create backup
docker compose exec postgres pg_dump -U monitor internet_monitor > backup_$(date +%Y%m%d).sql

# Restore backup
cat backup_20251231.sql | docker compose exec -i postgres psql -U monitor -d internet_monitor
```

---

## 📊 Reports

### Automatic Reports

The monitor generates reports automatically:

- **`relatorio_parcial_YYYY-MM-DD.txt`** - Main report (updated every interval)
- **`relatorio_snapshot_YYYY-MM-DD_HHMM.txt`** - Point-in-time snapshots
- **`relatorio_detalhado_YYYY-MM-DD.txt`** - Detailed report with all checks
- **`relatorio_parcial_YYYY-MM-DD.json`** - JSON format for APIs

### Report Contents

All reports include:

- 📅 Date and time period
- 📈 Total checks performed
- ✅ Uptime percentage
- ❌ Downtime periods with duration
- ⏱️ Average response times
- 🚀 Speed test results (if enabled)
- 📉 Failed hosts/tests
- 🎯 Quality assessment (Excellent/Good/Fair/Poor)

---

## 📈 Dashboards & Integrations

### Grafana

1. Add PostgreSQL data source:
   - Host: `localhost:5432`
   - Database: `internet_monitor`
   - User: `monitor`
   - Password: `monitor123`

2. Import dashboard or create custom panels

Example query for uptime gauge:
```sql
SELECT 
    (SUM(CASE WHEN connection_status = 'online' THEN 1 ELSE 0 END)::DECIMAL / COUNT(*)) * 100 as uptime
FROM connection_checks
WHERE date = CURRENT_DATE;
```

### Python API

```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="internet_monitor",
    user="monitor",
    password="monitor123"
)

cursor = conn.cursor()
cursor.execute("""
    SELECT timestamp, connection_status, success_rate
    FROM connection_checks
    WHERE date = CURRENT_DATE
    ORDER BY timestamp DESC
    LIMIT 10
""")

for row in cursor.fetchall():
    print(row)

conn.close()
```

---

## 🐳 Docker Commands

### Basic Operations

```bash
# Start system
docker compose up -d

# Stop system
docker compose down

# Restart monitor
docker compose restart monitor

# View logs (real-time)
docker compose logs -f monitor

# View logs (last 50 lines)
docker compose logs --tail=50 monitor

# Check status
docker compose ps

# Rebuild after code changes
docker compose down
docker compose build
docker compose up -d
```

### Database Access

```bash
# Connect to database
docker compose exec postgres psql -U monitor -d internet_monitor

# Run SQL query
docker compose exec postgres psql -U monitor -d internet_monitor -c "SELECT COUNT(*) FROM connection_checks;"

# View tables
docker compose exec postgres psql -U monitor -d internet_monitor -c "\dt"
```

---

## 📁 Project Structure

```
project-telecom-anoing/
├── monitor_internet.py      # Main monitoring script
├── generate_report.py        # Report generator
├── database.py               # Database manager
├── config.json               # Configuration file
├── requirements.txt          # Python dependencies
│
├── Dockerfile                # Docker image definition
├── docker-compose.yml        # Docker orchestration
├── init-db.sql              # Database initialization
│
├── logs/                     # Log files (auto-generated)
│   └── log_YYYY-MM-DD.jsonl
│
└── relatorios/               # Reports (auto-generated)
    ├── relatorio_parcial_YYYY-MM-DD.txt
    ├── relatorio_detalhado_YYYY-MM-DD.txt
    └── relatorio_snapshot_YYYY-MM-DD_HHMM.txt
```

---

## 🛠️ Troubleshooting

### No logs showing in Docker

**Solution:** The fix has been applied - Python output is now unbuffered.

If you still have issues:
```bash
docker compose down
docker compose build
docker compose up -d
```

### Database connection errors

```bash
# Check if PostgreSQL is running
docker compose ps

# Check PostgreSQL logs
docker compose logs postgres

# Restart database
docker compose restart postgres
```

### Speed tests not running

- Check `enable_speed_tests: true` in config.json
- Speed tests run with every check (can take 30-40 seconds each)
- Check logs: `docker compose logs monitor | grep -i speed`

### Logs occupying too much space

```bash
# Keep only last 30 days of logs
find logs/ -name "*.jsonl" -mtime +30 -delete

# Or clean old database data
docker compose exec postgres psql -U monitor -d internet_monitor -c "DELETE FROM connection_checks WHERE date < CURRENT_DATE - INTERVAL '90 days';"
```

### Container keeps restarting

```bash
# Check error logs
docker compose logs --tail=100 monitor

# Test manually
docker compose run --rm monitor python monitor_internet.py

# Verify config.json is valid JSON
cat config.json | python -m json.tool
```

---

## 📝 Notes

- ⚠️ Speed tests consume bandwidth (~30MB per test)
- 📱 Works with any connection type (cable, fiber, 4G/5G)
- 🔒 All data stored locally
- 🌍 Uses trusted public servers (Google, Cloudflare, Speedtest.net)
- 💾 Database stores all historical data for analytics

---

## 📋 Changelog

### Version 2.1 (Current)
- ✅ PostgreSQL database integration
- ✅ Speed tests on every check
- ✅ Automatic report generation
- ✅ Snapshot reports with timestamps
- ✅ Fixed Python buffering in Docker
- ✅ Improved logging output

### Version 2.0
- ✅ Automatic partial reports every 5 minutes
- ✅ Speed tests with multiple providers
- ✅ Docker support

### Version 1.0
- ✅ Initial release
- ✅ Basic monitoring (ping, HTTP, DNS)
- ✅ Manual report generation

---

## 🤝 Contributing

Suggestions and improvements are welcome!

## 📄 License

Open source - free to use.

---

**Developed to help document internet connection issues** 🇧🇷
