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
import { api, CurrentStatus, StatsData, SpeedTest, SpeedStats, PingHost } from '@/lib/api-client';
import TimelineChart from '@/components/TimelineChart';
import SpeedHistoryChart from '@/components/SpeedHistoryChart';
import { Download, Loader2, RefreshCw } from 'lucide-react';

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

  const loadAllData = async () => {
    try {
      const [status, today, last24h, speedTests, speedStatsData, pingData, outages] = await Promise.all([
        api.getCurrentStatus(),
        api.getStatsToday(),
        api.getStatsLast24h(),
        api.getCurrentSpeedTests(),
        api.getSpeedStats(24),
        api.getPingHosts(24),
        api.getOutages(),
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

  useEffect(() => {
    loadAllData();
  }, []);

  useEffect(() => {
    if (!autoRefresh) return;
    
    const interval = setInterval(() => {
      loadAllData();
    }, 5000);

    return () => clearInterval(interval);
  }, [autoRefresh]);

  const handleExportPDF = () => {
    alert('PDF export functionality - to be implemented');
  };

  const handleExportPNG = () => {
    alert('PNG export functionality - to be implemented');
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
      <header className="bg-white dark:bg-zinc-900 border-b border-zinc-200 dark:border-zinc-800 sticky top-0 z-50 shadow-sm">
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

      <main className="container mx-auto px-4 py-6 space-y-6">
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
              <CardDescription>Outages (24h)</CardDescription>
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
              <CardTitle>Connection Timeline (Last 24h)</CardTitle>
            </CardHeader>
            <CardContent>
              <TimelineChart />
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
            <CardTitle>Speed Test History by Provider (Last 24h)</CardTitle>
          </CardHeader>
          <CardContent>
            <SpeedHistoryChart />
          </CardContent>
        </Card>

        {/* Speed Stats and Ping Stats */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Card>
            <CardHeader>
              <CardTitle>Speed Test Statistics (Last 24h)</CardTitle>
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
              <CardTitle>Ping Statistics by Host (Last 24h)</CardTitle>
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
