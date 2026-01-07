# Export Feature Documentation

## 📥 Overview

The dashboard now includes full export functionality to save your monitoring data as PDF or PNG images, or print directly from the browser.

## ✨ Features

### Export Options

**Available from the Export dropdown menu in the top-right corner:**

1. **📄 Export as PDF**
   - High-quality PDF document
   - Multiple pages for long content
   - A4 format (210mm width)
   - 2x scale for crisp text
   - Automatic file naming with date

2. **🖼️ Export as PNG**
   - High-resolution PNG image
   - 2x scale for retina displays
   - Captures entire dashboard
   - Transparent or white background
   - Perfect for presentations

3. **🖨️ Print Dashboard**
   - Browser native print dialog
   - Print-optimized layout
   - Removes interactive elements
   - Page break control
   - Works with any printer or "Save as PDF"

## 🎯 How to Use

### Export as PDF

1. Open dashboard at `http://localhost:3000`
2. Apply any filters you want (date range, period)
3. Click **Export** button (top-right)
4. Select **📄 Export as PDF**
5. Wait for processing (2-5 seconds)
6. PDF automatically downloads

**File naming:** `internet-monitor-2026-01-07.pdf`

**Features:**
- Multi-page support for long dashboards
- High resolution (2x scale)
- White background
- All charts included
- Statistics preserved

### Export as PNG

1. Open dashboard at `http://localhost:3000`
2. Configure view (filters, charts, etc.)
3. Click **Export** button
4. Select **🖼️ Export as PNG**
5. Wait for processing (2-5 seconds)
6. PNG image downloads

**File naming:** `internet-monitor-2026-01-07.png`

**Features:**
- Single image capture
- High resolution (2x scale)
- Full dashboard screenshot
- Perfect for sharing
- Optimized file size

### Print Dashboard

1. Open dashboard
2. Click **Export** button
3. Select **🖨️ Print Dashboard**
4. Browser print dialog opens
5. Choose printer or "Save as PDF"
6. Adjust settings if needed
7. Print or save

**Print features:**
- Hides header/navigation
- Optimized for paper
- No shadows/gradients
- Page break control
- Works with all browsers

## 🔧 Technical Implementation

### Libraries Used

**html2canvas**
- Captures DOM as canvas
- Version: Latest stable
- Converts HTML/CSS to image
- Supports CORS
- High-quality rendering

**jsPDF**
- Generates PDF documents
- A4 format support
- Multi-page handling
- Image embedding
- Client-side generation

### Code Architecture

**Export Functions** (`app/page.tsx`):

```typescript
// PDF Export
const handleExportPDF = async () => {
  // 1. Get dashboard element
  const element = document.getElementById('dashboard-content');
  
  // 2. Pause auto-refresh
  setAutoRefresh(false);
  
  // 3. Capture with html2canvas
  const canvas = await html2canvas(element, {
    scale: 2,
    useCORS: true,
    backgroundColor: '#ffffff'
  });
  
  // 4. Create PDF with jsPDF
  const pdf = new jsPDF('p', 'mm', 'a4');
  pdf.addImage(canvas.toDataURL('image/png'), 'PNG', 0, 0, 210, height);
  
  // 5. Handle multi-page
  // Add pages if content exceeds A4 height
  
  // 6. Save file
  pdf.save(`internet-monitor-${date}.pdf`);
  
  // 7. Restore auto-refresh
  setAutoRefresh(true);
};

// PNG Export
const handleExportPNG = async () => {
  // Similar to PDF but saves as PNG blob
  canvas.toBlob((blob) => {
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.download = `internet-monitor-${date}.png`;
    link.click();
  });
};
```

### Export Styling

**CSS Rules** (`globals.css`):

```css
/* Hide header during export */
.no-export {
  display: none !important;
}

/* Print media queries */
@media print {
  header {
    display: none !important;
  }
  
  .card {
    page-break-inside: avoid;
  }
  
  body {
    background: white !important;
  }
  
  * {
    box-shadow: none !important;
  }
}
```

### What Gets Exported

**Included:**
- ✅ Period filter information
- ✅ Current status card
- ✅ Statistics cards (uptime, outages)
- ✅ Timeline chart
- ✅ Recent speed tests
- ✅ Speed history chart
- ✅ Speed statistics table
- ✅ Ping statistics table

**Excluded:**
- ❌ Header/navigation bar
- ❌ Export button
- ❌ Auto-refresh toggle
- ❌ Interactive hover states

## 📊 Export Quality

### Resolution

**PDF:**
- Width: 210mm (A4 standard)
- Scale: 2x (high DPI)
- Format: Portrait
- Quality: Print-ready

**PNG:**
- Scale: 2x for retina
- Format: PNG with transparency support
- Compression: Optimized
- Quality: Presentation-ready

### File Sizes

**Typical sizes:**
- PDF: 500KB - 2MB (depends on content)
- PNG: 1MB - 5MB (depends on charts)

**Optimization:**
- Charts rendered at optimal quality
- Text remains sharp
- Colors preserved
- No quality loss

## 🎨 Use Cases

### 1. Monthly Reports

**Scenario:** Generate monthly performance reports

```
1. Set filter to "Last 30 Days"
2. Wait for data to load
3. Export as PDF
4. Attach to email or documentation
```

### 2. Incident Documentation

**Scenario:** Document a specific outage

```
1. Use custom filter for incident time
2. Review timeline and statistics
3. Export as PDF for incident report
4. Include in post-mortem documentation
```

### 3. Presentations

**Scenario:** Show internet quality in meeting

```
1. Filter to relevant period
2. Export as PNG
3. Insert in PowerPoint/Keynote
4. Present to stakeholders
```

### 4. Historical Archives

**Scenario:** Keep weekly snapshots

```
1. Every Sunday, open dashboard
2. Set filter to "Last 7 Days"
3. Export as PDF
4. Save to archive folder
5. Automated with script if needed
```

### 5. ISP Complaints

**Scenario:** Prove poor internet quality to ISP

```
1. Export multiple days showing issues
2. Highlight outages and slow speeds
3. Attach PDFs to support ticket
4. Reference specific dates/times
```

## 🔄 Export Process

### Step-by-Step Process

**What happens when you export:**

1. **Preparation**
   - Auto-refresh pauses
   - UI animations complete
   - Dashboard stabilizes

2. **Capture**
   - html2canvas scans DOM
   - Converts to high-res canvas
   - Processes CSS/styles
   - Renders charts as images

3. **Processing**
   - For PDF: Converts to PDF pages
   - For PNG: Creates image blob
   - Calculates dimensions
   - Optimizes output

4. **Download**
   - Generates unique filename
   - Triggers browser download
   - File saved to Downloads folder

5. **Cleanup**
   - Restores auto-refresh
   - Releases memory
   - Clears temporary data

**Duration:** 2-5 seconds (depends on content)

## 🛠️ Troubleshooting

### Export not working

**Check browser console for errors:**
```javascript
// Open DevTools (F12)
// Look for errors during export
```

**Common issues:**
1. **CORS errors:** Charts from external sources
   - Solution: All charts use local data
   - Verify API is same origin

2. **Memory errors:** Very long dashboards
   - Solution: Filter to smaller date range
   - Export in sections

3. **Download blocked:** Browser security
   - Solution: Allow downloads in settings
   - Check pop-up blocker

### Poor quality exports

**If export looks blurry:**
1. Check scale setting (should be 2x)
2. Ensure browser zoom is 100%
3. Verify modern browser (Chrome, Firefox, Edge)

**If charts missing:**
1. Wait for all charts to load before export
2. Disable auto-refresh during export
3. Check console for rendering errors

### File too large

**If PDF/PNG is very large:**
1. Filter to shorter time period
2. Reduce window size before export
3. Close unnecessary browser tabs
4. Use PNG instead of PDF for single page

### Print preview issues

**If print looks wrong:**
1. Check print settings (scale, margins)
2. Try "Print to PDF" first
3. Adjust browser print margins
4. Use portrait orientation

## 💡 Best Practices

### Before Exporting

1. **Apply Filters First**
   - Set desired date range
   - Wait for data to load completely

2. **Disable Auto-Refresh**
   - Prevents capture during refresh
   - Ensures stable snapshot

3. **Expand Sections**
   - All cards should be visible
   - Charts fully rendered

4. **Check Data**
   - Verify correct information shown
   - Confirm charts display properly

### File Management

**Recommended naming convention:**
```
internet-monitor-YYYY-MM-DD-description.pdf

Examples:
- internet-monitor-2026-01-07-monthly.pdf
- internet-monitor-2026-01-06-outage.pdf
- internet-monitor-2026-01-week1.pdf
```

**Organization:**
```
reports/
├── 2026/
│   ├── 01-January/
│   │   ├── weekly/
│   │   │   ├── internet-monitor-2026-01-07.pdf
│   │   │   └── internet-monitor-2026-01-14.pdf
│   │   └── monthly/
│   │       └── internet-monitor-2026-01-monthly.pdf
```

### Automation Ideas

**Script to save weekly reports:**
```bash
#!/bin/bash
# weekly-export.sh

# Open dashboard with filter
# Headless browser (Puppeteer/Playwright)
# Trigger export
# Save to archive
# Send email notification
```

**Cron job for automated exports:**
```bash
# Export every Sunday at midnight
0 0 * * 0 /path/to/export-script.sh
```

## 🚀 Advanced Usage

### Programmatic Export

**Using Puppeteer (Node.js):**
```javascript
const puppeteer = require('puppeteer');

async function exportDashboard() {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  
  // Navigate to dashboard
  await page.goto('http://localhost:3000');
  
  // Wait for data to load
  await page.waitForSelector('#dashboard-content');
  
  // Click export button
  await page.click('[aria-label="Export"]');
  await page.click('text=Export as PDF');
  
  // Wait for download
  await page.waitForTimeout(5000);
  
  await browser.close();
}
```

### Custom Styling for Export

**Add custom CSS for exports:**
```css
/* Custom export styles */
@media print {
  .custom-card {
    border: 2px solid #000;
    padding: 20px;
  }
  
  .hide-on-export {
    display: none;
  }
}
```

### Batch Exports

**Export multiple periods:**
```typescript
const periods = ['today', 'yesterday', 'last-7-days'];

for (const period of periods) {
  // Set filter
  setPeriodType(period);
  
  // Wait for data
  await new Promise(r => setTimeout(r, 2000));
  
  // Export
  await handleExportPDF();
  
  // Wait for download
  await new Promise(r => setTimeout(r, 3000));
}
```

## 📈 Performance

### Optimization Tips

1. **Reduce Export Time:**
   - Close other browser tabs
   - Disable animations
   - Use smaller date ranges

2. **Improve Quality:**
   - Export at 100% zoom
   - Use modern browser
   - Ensure good network connection

3. **Reduce File Size:**
   - Filter unnecessary data
   - Export PNG for single page
   - Compress PDFs after export

### Browser Compatibility

**Fully Supported:**
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Edge 90+
- ✅ Safari 14+

**Partially Supported:**
- ⚠️ Older browsers may have quality issues
- ⚠️ Mobile browsers work but may be slower

## 🔐 Privacy & Security

**All processing is client-side:**
- ✅ No data sent to external servers
- ✅ Export happens in browser
- ✅ Files saved locally only
- ✅ No cloud storage used
- ✅ Complete privacy

**Data handling:**
- Dashboard data from local API
- Canvas rendering in browser
- File generation in browser
- Download to local disk

## 📝 Future Enhancements

### Planned Features

1. **Custom Templates**
   - Multiple export layouts
   - Company branding
   - Custom headers/footers

2. **Scheduled Exports**
   - Automatic daily/weekly exports
   - Email delivery
   - Cloud storage integration

3. **Export Options**
   - CSV data export
   - Excel spreadsheets
   - JSON data dumps

4. **Enhanced Quality**
   - Vector PDF (SVG charts)
   - Higher resolution options
   - Custom DPI settings

5. **Batch Operations**
   - Export multiple periods
   - Comparison reports
   - Diff highlighting

---

**Export feature fully implemented!** 📥

Access dashboard at `http://localhost:3000` and use the Export dropdown to save your monitoring data.
