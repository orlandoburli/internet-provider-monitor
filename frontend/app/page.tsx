'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { api, CurrentStatus, StatsData, SpeedTest, SpeedStats, PingHost, DateRangeParams } from '@/lib/api-client';
import TimelineChart from '@/components/TimelineChart';
import SpeedHistoryChart from '@/components/SpeedHistoryChart';
import DateTimeFilter, { DateRange, PeriodType } from '@/components/DateTimeFilter';
import { Download, Loader2, RefreshCw } from 'lucide-react';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

export default function Dashboard() {
  const [currentStatus, setCurrentStatus] = useState<CurrentStatus | null>(null);
  const [todayStats, setTodayStats] = useState<StatsData | null>(null);
  const [last24hStats, setLast24hStats] = useState<StatsData | null>(null);
  const [recentSpeedTests, setRecentSpeedTests] = useState<SpeedTest[]>([]);
  const [speedStats, setSpeedStats] = useState<SpeedStats[]>([]);
  const [pingHosts, setPingHosts] = useState<PingHost[]>([]);
  const [outagesCount, setOutagesCount] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [dateRange, setDateRange] = useState<DateRange | null>(null);
  const [periodType, setPeriodType] = useState<PeriodType>('last-24-hours');

  const loadAllData = async () => {
    try {
      const dateParams: DateRangeParams | undefined = dateRange
        ? { from: dateRange.from, to: dateRange.to }
        : undefined;

      const [status, today, last24h, speedTests, speedStatsData, pingData, outages] = await Promise.all([
        api.getCurrentStatus(),
        api.getStatsToday(),
        api.getStatsLast24h(),
        api.getCurrentSpeedTests(),
        api.getSpeedStats(dateParams),
        api.getPingHosts(dateParams),
        api.getOutages(dateParams),
      ]);

      setCurrentStatus(status);
      setTodayStats(today);
      setLast24hStats(last24h);
      setRecentSpeedTests(speedTests.slice(0, 5));
      setSpeedStats(speedStatsData);
      setPingHosts(pingData);
      setOutagesCount(outages.length);
      setLastUpdate(new Date());
      setLoading(false);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      setLoading(false);
    }
  };

  const handleFilterChange = (range: DateRange, type: PeriodType) => {
    setDateRange(range);
    setPeriodType(type);
  };

  useEffect(() => {
    loadAllData();
  }, [dateRange]);

  useEffect(() => {
    if (!autoRefresh) return;
    
    const interval = setInterval(() => {
      loadAllData();
    }, 5000);

    return () => clearInterval(interval);
  }, [autoRefresh]);

  const handleExportPDF = async () => {
    const wasAutoRefresh = autoRefresh;
    
    try {
      const element = document.getElementById('dashboard-content');
      if (!element) return;

      // Temporarily hide export button and toggle auto-refresh off
      setAutoRefresh(false);

      // Wait a bit for any animations to complete
      await new Promise(resolve => setTimeout(resolve, 100));

      // Add export class to convert colors
      document.body.classList.add('export-mode');

      // Capture the dashboard
      const canvas = await html2canvas(element, {
        scale: 2,
        useCORS: true,
        logging: false,
        backgroundColor: '#ffffff',
        ignoreElements: (element) => {
          return element.classList?.contains('no-export');
        },
        onclone: (clonedDoc) => {
          // Convert modern color formats to RGB
          const clonedBody = clonedDoc.body;
          clonedBody.style.setProperty('--background', '#ffffff');
          clonedBody.style.setProperty('--foreground', '#09090b');
          clonedBody.style.setProperty('--card', '#ffffff');
          clonedBody.style.setProperty('--card-foreground', '#09090b');
          clonedBody.style.setProperty('--primary', '#18181b');
          clonedBody.style.setProperty('--primary-foreground', '#fafafa');
          clonedBody.style.setProperty('--secondary', '#f4f4f5');
          clonedBody.style.setProperty('--muted', '#f4f4f5');
          clonedBody.style.setProperty('--muted-foreground', '#71717a');
          clonedBody.style.setProperty('--border', '#e4e4e7');
        }
      });

      // Calculate PDF dimensions
      const imgWidth = 210; // A4 width in mm
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      
      // Create PDF
      const pdf = new jsPDF('p', 'mm', 'a4');
      const imgData = canvas.toDataURL('image/png');
      
      // Add multiple pages if content is too long
      let heightLeft = imgHeight;
      let position = 0;
      
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
      heightLeft -= 297; // A4 height
      
      while (heightLeft > 0) {
        position = heightLeft - imgHeight;
        pdf.addPage();
        pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
        heightLeft -= 297;
      }
      
      // Save PDF
      const fileName = `internet-monitor-${new Date().toISOString().slice(0, 10)}.pdf`;
      pdf.save(fileName);

      // Remove export class
      document.body.classList.remove('export-mode');

      // Restore auto-refresh
      setAutoRefresh(wasAutoRefresh);
    } catch (error) {
      console.error('Error exporting PDF:', error);
      alert('Failed to export PDF. Please try again.');
      
      // Cleanup on error
      document.body.classList.remove('export-mode');
      setAutoRefresh(wasAutoRefresh);
    }
  };

  const handleExportPNG = async () => {
    const wasAutoRefresh = autoRefresh;
    
    try {
      const element = document.getElementById('dashboard-content');
      if (!element) return;

      // Temporarily toggle auto-refresh off
      setAutoRefresh(false);

      // Wait a bit for any animations to complete
      await new Promise(resolve => setTimeout(resolve, 100));

      // Add export class to convert colors
      document.body.classList.add('export-mode');

      // Capture the dashboard
      const canvas = await html2canvas(element, {
        scale: 2,
        useCORS: true,
        logging: false,
        backgroundColor: '#ffffff',
        ignoreElements: (element) => {
          return element.classList?.contains('no-export');
        },
        onclone: (clonedDoc) => {
          // Convert modern color formats to RGB
          const clonedBody = clonedDoc.body;
          clonedBody.style.setProperty('--background', '#ffffff');
          clonedBody.style.setProperty('--foreground', '#09090b');
          clonedBody.style.setProperty('--card', '#ffffff');
          clonedBody.style.setProperty('--card-foreground', '#09090b');
          clonedBody.style.setProperty('--primary', '#18181b');
          clonedBody.style.setProperty('--primary-foreground', '#fafafa');
          clonedBody.style.setProperty('--secondary', '#f4f4f5');
          clonedBody.style.setProperty('--muted', '#f4f4f5');
          clonedBody.style.setProperty('--muted-foreground', '#71717a');
          clonedBody.style.setProperty('--border', '#e4e4e7');
        }
      });

      // Convert to blob and download
      canvas.toBlob((blob) => {
        if (!blob) return;
        
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        const fileName = `internet-monitor-${new Date().toISOString().slice(0, 10)}.png`;
        
        link.href = url;
        link.download = fileName;
        link.click();
        
        URL.revokeObjectURL(url);
        
        // Remove export class
        document.body.classList.remove('export-mode');
        
        // Restore auto-refresh
        setAutoRefresh(wasAutoRefresh);
      });
    } catch (error) {
      console.error('Error exporting PNG:', error);
      alert('Failed to export PNG. Please try again.');
      
      // Cleanup on error
      document.body.classList.remove('export-mode');
      setAutoRefresh(wasAutoRefresh);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-zinc-50 to-zinc-100 dark:from-zinc-900 dark:to-zinc-950">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin mx-auto mb-4 text-primary" />
          <p className="text-lg text-muted-foreground">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-zinc-50 to-zinc-100 dark:from-zinc-900 dark:to-zinc-950">
      {/* Header */}
      <header className="bg-white dark:bg-zinc-900 border-b border-zinc-200 dark:border-zinc-800 sticky top-0 z-50 shadow-sm no-export print:hidden">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                🌐 Internet Monitor
              </h1>
              <p className="text-sm text-muted-foreground">Real-Time Connection Analytics</p>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <RefreshCw className={`h-4 w-4 ${autoRefresh ? 'animate-spin' : ''}`} />
                <span>Auto-refresh: {autoRefresh ? 'ON' : 'OFF'}</span>
                <button
                  onClick={() => setAutoRefresh(!autoRefresh)}
                  className="text-xs underline hover:text-foreground"
                >
                  {autoRefresh ? 'Disable' : 'Enable'}
                </button>
              </div>

              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="default" size="sm">
                    <Download className="h-4 w-4 mr-2" />
                    Export
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-48">
                  <DropdownMenuLabel>Export Options</DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleExportPDF}>
                    📄 Export as PDF
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={handleExportPNG}>
                    🖼️ Export as PNG
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handlePrint}>
                    🖨️ Print Dashboard
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
          <p className="text-xs text-muted-foreground mt-2">
            Last updated: {lastUpdate.toLocaleTimeString()}
          </p>
        </div>
      </header>

      <main id="dashboard-content" className="container mx-auto px-4 py-6 space-y-6">
        {/* Period Filter */}
        <DateTimeFilter onFilterChange={handleFilterChange} />

        {/* Current Status */}
        <Card className="border-2">
          <CardHeader className="pb-3">
            <CardTitle>Current Status</CardTitle>
          </CardHeader>
          <CardContent>
            {currentStatus && (
              <div className="text-center py-4">
                <Badge
                  variant={currentStatus.status === 'online' ? 'default' : 'destructive'}
                  className="text-lg px-4 py-2 mb-2"
                >
                  {currentStatus.status === 'online' ? '✅ ONLINE' : '❌ OFFLINE'}
                </Badge>
                <p className="text-sm text-muted-foreground mt-2">
                  Success Rate: {currentStatus.success_rate}%
                </p>
                <p className="text-xs text-muted-foreground">
                  {new Date(currentStatus.timestamp).toLocaleString()}
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader>
              <CardDescription>Today's Uptime</CardDescription>
              <CardTitle className="text-3xl text-blue-600">
                {todayStats?.uptime_percentage.toFixed(2)}%
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                {todayStats?.total_checks} checks ({todayStats?.online_checks} online, {todayStats?.offline_checks} offline)
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardDescription>Last 24h Uptime</CardDescription>
              <CardTitle className="text-3xl text-green-600">
                {last24hStats?.uptime_percentage.toFixed(2)}%
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                {last24hStats?.total_checks} checks
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardDescription>Outages ({periodType.replace(/-/g, ' ')})</CardDescription>
              <CardTitle className="text-3xl text-red-600">
                {outagesCount}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                connection failures
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Connection Timeline ({periodType.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())})</CardTitle>
            </CardHeader>
            <CardContent>
              <TimelineChart dateRange={dateRange} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Recent Speed Tests</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recentSpeedTests.map((test, idx) => (
                  <div key={idx} className="p-3 bg-zinc-50 dark:bg-zinc-800 rounded-lg">
                    <p className="font-medium text-sm">{test.provider}</p>
                    <p className="text-xs text-muted-foreground mb-1">
                      {new Date(test.timestamp).toLocaleString()}
                    </p>
                    <div className="flex justify-between text-xs">
                      <span>↓ {test.download_mbps?.toFixed(2) || '--'} Mbps</span>
                      {test.upload_mbps && (
                        <span>↑ {test.upload_mbps.toFixed(2)} Mbps</span>
                      )}
                    </div>
                    {test.ping_ms && (
                      <p className="text-xs text-muted-foreground mt-1">
                        Ping: {test.ping_ms.toFixed(2)} ms
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Speed History Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Speed Test History by Provider ({periodType.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())})</CardTitle>
          </CardHeader>
          <CardContent>
            <SpeedHistoryChart dateRange={dateRange} />
          </CardContent>
        </Card>

        {/* Speed Stats and Ping Stats */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Card>
            <CardHeader>
              <CardTitle>Speed Test Statistics ({periodType.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())})</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {speedStats.map((stat, idx) => (
                  <div key={idx} className="p-4 bg-zinc-50 dark:bg-zinc-800 rounded-lg">
                    <h4 className="font-medium mb-2">{stat.provider}</h4>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Download</p>
                        <p className="font-medium">{stat.avg_download?.toFixed(2) || '--'} Mbps</p>
                        <p className="text-xs text-muted-foreground">
                          Min: {stat.min_download?.toFixed(2) || '--'} / Max: {stat.max_download?.toFixed(2) || '--'}
                        </p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Upload</p>
                        <p className="font-medium">{stat.avg_upload?.toFixed(2) || '--'} Mbps</p>
                        <p className="text-xs text-muted-foreground">
                          Min: {stat.min_upload?.toFixed(2) || '--'} / Max: {stat.max_upload?.toFixed(2) || '--'}
                        </p>
                      </div>
                    </div>
                    {stat.avg_ping && (
                      <p className="text-xs text-muted-foreground mt-2">
                        Avg Ping: {stat.avg_ping.toFixed(2)} ms
                      </p>
                    )}
                    <p className="text-xs text-muted-foreground mt-1">
                      {stat.total_tests} tests
                    </p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Ping Statistics by Host ({periodType.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())})</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {pingHosts.map((host, idx) => (
                  <div key={idx} className="p-3 bg-zinc-50 dark:bg-zinc-800 rounded-lg">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-medium">{host.host}</span>
                      <Badge variant={host.success_rate >= 95 ? 'default' : host.success_rate >= 80 ? 'secondary' : 'destructive'}>
                        {host.success_rate.toFixed(1)}%
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Avg: {host.avg_response_time?.toFixed(2) || '--'} ms | 
                      Min: {host.min_response_time?.toFixed(2) || '--'} ms | 
                      Max: {host.max_response_time?.toFixed(2) || '--'} ms
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {host.successful_tests}/{host.total_tests} successful
                    </p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
