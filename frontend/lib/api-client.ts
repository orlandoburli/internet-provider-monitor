// API Client for Internet Monitor Dashboard

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

export interface CurrentStatus {
  timestamp: string;
  status: string;
  success_rate: number;
  date: string;
  time: string;
}

export interface StatsData {
  total_checks: number;
  online_checks: number;
  offline_checks: number;
  avg_success_rate: number;
  uptime_percentage: number;
  first_check?: string;
  last_check?: string;
}

export interface TimelineData {
  timestamp: string;
  status: string;
  success_rate: number;
}

export interface SpeedTest {
  provider: string;
  download_mbps: number | null;
  upload_mbps: number | null;
  ping_ms: number | null;
  server_name: string | null;
  server_location: string | null;
  timestamp: string;
}

export interface SpeedStats {
  provider: string;
  total_tests: number;
  avg_download: number | null;
  avg_upload: number | null;
  avg_ping: number | null;
  min_download: number | null;
  max_download: number | null;
  min_upload: number | null;
  max_upload: number | null;
}

export interface SpeedHistoryData {
  timestamp: string;
  provider: string;
  download_mbps: number | null;
  upload_mbps: number | null;
}

export interface PingHost {
  host: string;
  total_tests: number;
  successful_tests: number;
  failed_tests: number;
  avg_response_time: number | null;
  min_response_time: number | null;
  max_response_time: number | null;
  success_rate: number;
}

export interface OutageData {
  timestamp: string;
  success_rate: number;
}

async function fetchAPI<T>(endpoint: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`);
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }
  return response.json();
}

export const api = {
  getCurrentStatus: () => fetchAPI<CurrentStatus>('/api/status/current'),
  getStatsToday: () => fetchAPI<StatsData>('/api/stats/today'),
  getStatsLast24h: () => fetchAPI<StatsData>('/api/stats/last24h'),
  getTimeline: (hours = 24) => fetchAPI<TimelineData[]>(`/api/history/timeline?hours=${hours}`),
  getCurrentSpeedTests: () => fetchAPI<SpeedTest[]>('/api/speed/current'),
  getSpeedStats: (hours = 24) => fetchAPI<SpeedStats[]>(`/api/speed/stats?hours=${hours}`),
  getSpeedHistory: (hours = 24) => fetchAPI<SpeedHistoryData[]>(`/api/speed/history?hours=${hours}`),
  getOutages: () => fetchAPI<OutageData[]>('/api/outages/recent'),
  getPingHosts: (hours = 24) => fetchAPI<PingHost[]>(`/api/ping/hosts?hours=${hours}`),
};
