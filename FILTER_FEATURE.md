# Period Filter Feature Documentation

## 🎯 Overview

The dashboard now includes a comprehensive period filter that allows you to view data for any custom date and hour range.

## ✨ Features

### Quick Period Selection

Pre-configured time periods for instant filtering:

- **Last Hour** - Data from the past 60 minutes
- **Last 6 Hours** - Past 6 hours of monitoring
- **Last 24 Hours** - Past day (default)
- **Today** - From midnight to now
- **Yesterday** - Previous day (full 24 hours)
- **Last 7 Days** - Past week
- **Last 30 Days** - Past month

### Custom Date & Hour Range

Advanced filtering with precise control:

- **From Date**: Select any start date using calendar picker
- **From Hour**: Choose start hour (00:00 to 23:00)
- **To Date**: Select any end date using calendar picker
- **To Hour**: Choose end hour (00:59 to 23:59)

## 🎨 User Interface

### Filter Panel

Located at the top of the dashboard with:
- Visual badge showing current period type
- Grid of quick-select buttons
- Expandable custom date/time selector
- Current range display showing exact timestamps

### Dynamic Chart Titles

All charts automatically update their titles to reflect the selected period:
- "Connection Timeline (Last 24 Hours)"
- "Speed Test History by Provider (Today)"
- "Ping Statistics by Host (Custom)"
- etc.

## 🔧 Technical Implementation

### Frontend Components

**DateTimeFilter Component** (`components/DateTimeFilter.tsx`)
- Shadcn UI Calendar for date selection
- Select dropdowns for hour selection
- Date-fns for date calculations
- Period type management

**Updated Components:**
- `app/page.tsx` - Main dashboard with filter state
- `components/TimelineChart.tsx` - Chart with date range support
- `components/SpeedHistoryChart.tsx` - Chart with date range support

### API Client Updates

**Date Range Conversion** (`lib/api-client.ts`)
- Converts date ranges to hours for API compatibility
- `DateRangeParams` interface for type safety
- Helper function `getHoursFromDateRange()`

### Backend API Updates

**Updated Endpoints:**
- `/api/outages/recent?hours=X` - Now accepts hours parameter
- `/api/speed/stats?hours=X` - Filter speed tests by period
- `/api/speed/history?hours=X` - Filter speed history
- `/api/ping/hosts?hours=X` - Filter ping statistics
- `/api/history/timeline?hours=X` - Filter connection timeline

## 📊 Data Flow

```
User selects period
       ↓
DateTimeFilter calculates date range
       ↓
Converts to hours parameter
       ↓
API client adds hours to requests
       ↓
Flask API filters PostgreSQL queries
       ↓
Charts update with filtered data
```

## 💻 Usage Examples

### Quick Period Selection

1. Open dashboard at `http://localhost:3000`
2. Click any quick period button (e.g., "Last 6 Hours")
3. All data automatically updates

### Custom Date Range

1. Click "Custom" button
2. Select start date from calendar
3. Choose start hour (e.g., 08:00)
4. Select end date from calendar
5. Choose end hour (e.g., 17:59)
6. Click "Apply Custom Filter"
7. View data for exactly that period

## 🎯 Use Cases

### Monitor Specific Incidents

Want to see what happened yesterday between 2 PM and 6 PM?
1. Click "Custom"
2. Select yesterday's date for both from/to
3. Set from hour: 14:00
4. Set to hour: 17:59
5. Apply filter

### Compare Business Hours

View today's business hours (9 AM to 5 PM):
1. Click "Custom"
2. Select today's date
3. Set from hour: 09:00
4. Set to hour: 16:59
5. Apply filter

### Weekly Performance Review

Review last week's performance:
1. Click "Last 7 Days"
2. Instantly see all metrics for the past week

## 🔄 Auto-Refresh Behavior

- Auto-refresh continues to work with filtered data
- Charts update every 5 seconds using the selected period
- Custom filters remain active during refresh
- Filter state persists across refreshes

## 🎨 UI Components

### Shadcn UI Components Used

- **Calendar** - Beautiful date picker
- **Select** - Hour dropdown selector
- **Button** - Quick period buttons
- **Badge** - Period type indicator
- **Popover** - Calendar popup
- **Card** - Filter container

### Styling

- Responsive grid layout
- Dark mode support ready
- Gradient backgrounds
- Hover effects on buttons
- Visual feedback for active filters

## 📝 Code Examples

### Filtering Timeline Data

```typescript
// Frontend - TimelineChart.tsx
const dateParams: DateRangeParams = {
  from: new Date('2026-01-06T08:00:00'),
  to: new Date('2026-01-06T17:59:59')
};

api.getTimeline(dateParams); // Fetches 10 hours of data
```

### Backend Query

```python
# Python - dashboard.py
@app.route('/api/history/timeline')
def history_timeline():
    hours = int(request.args.get('hours', 24))
    
    query = """
        SELECT * FROM connection_checks
        WHERE timestamp >= NOW() - INTERVAL '%s hours'
        ORDER BY timestamp ASC
    """
    
    results = db.execute_query(query, (hours,))
```

## 🚀 Performance

### Optimizations

- Date calculations done client-side
- Only hours parameter sent to API
- PostgreSQL interval queries (indexed)
- Efficient chart re-rendering
- Minimal network requests

### Database Indexes

Used for fast filtering:
- `idx_timestamp` on `connection_checks`
- `idx_date` on `connection_checks`
- `idx_status` on `connection_checks`

## 🔮 Future Enhancements

Potential improvements:

1. **Date Range Presets**
   - This week
   - This month
   - Last quarter

2. **Time Zone Selection**
   - User-selectable time zones
   - UTC display option

3. **Comparison Mode**
   - Compare two date ranges
   - Side-by-side charts

4. **Saved Filters**
   - Save custom periods
   - Quick access to favorites

5. **Export Filtered Data**
   - CSV export for selected period
   - PDF report for date range

6. **Hour Range Slider**
   - Visual slider for hours
   - Drag to select range

## 🐛 Troubleshooting

### Filter not working?

1. **Check browser console** for errors
2. **Verify API** is responding: `curl http://localhost:8080/api/history/timeline?hours=6`
3. **Clear browser cache** and refresh
4. **Check date range** - ensure 'from' is before 'to'

### No data showing?

- Selected period might not have data yet
- Try "Last 24 Hours" to see recent data
- Check monitor service is running: `docker compose ps`

### Charts not updating?

- Auto-refresh might be off - toggle it on
- Rebuild frontend: `docker compose build dashboard-frontend`
- Restart services: `docker compose restart`

## 📚 Related Files

### Frontend
- `frontend/components/DateTimeFilter.tsx` - Filter component
- `frontend/lib/api-client.ts` - API client with date support
- `frontend/app/page.tsx` - Dashboard integration

### Backend
- `dashboard.py` - Updated API endpoints

### Dependencies
- `date-fns` - Date calculations
- `react-day-picker` - Calendar component
- `shadcn/ui` - UI components

## ✅ Testing

### Manual Testing

1. **Quick Filters**: Click each quick period button
2. **Custom Filter**: Set various date/hour ranges
3. **Edge Cases**: 
   - Same day, different hours
   - Multi-day ranges
   - Last hour with auto-refresh
4. **Charts**: Verify all charts update
5. **API**: Test endpoints with curl

### API Endpoints to Test

```bash
# Timeline with 6 hours
curl "http://localhost:8080/api/history/timeline?hours=6"

# Speed stats with 12 hours
curl "http://localhost:8080/api/speed/stats?hours=12"

# Outages with 1 hour
curl "http://localhost:8080/api/outages/recent?hours=1"

# Ping stats with 48 hours
curl "http://localhost:8080/api/ping/hosts?hours=48"
```

---

**Period filter successfully implemented!** 🎉

Access your dashboard at `http://localhost:3000` and start filtering your data.
