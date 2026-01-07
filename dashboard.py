#!/usr/bin/env python3
"""
Real-Time Dashboard Service
Web-based dashboard for monitoring internet connection metrics
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

class DashboardDatabase:
    """Database connection manager for dashboard"""
    
    def __init__(self):
        self.config = {
            'host': os.getenv('POSTGRES_HOST', 'postgres'),
            'port': os.getenv('POSTGRES_PORT', '5432'),
            'database': os.getenv('POSTGRES_DB', 'internet_monitor'),
            'user': os.getenv('POSTGRES_USER', 'monitor'),
            'password': os.getenv('POSTGRES_PASSWORD', 'monitor123')
        }
    
    def get_connection(self):
        """Create database connection"""
        return psycopg2.connect(**self.config)
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Execute query and return results as list of dicts"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params)
            results = cursor.fetchall()
            return [dict(row) for row in results]
        finally:
            conn.close()


db = DashboardDatabase()


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/')
def index():
    """API information"""
    return jsonify({
        'name': 'Internet Monitor API',
        'version': '2.0',
        'endpoints': {
            'status': '/api/status/current',
            'stats_today': '/api/stats/today',
            'stats_24h': '/api/stats/last24h',
            'timeline': '/api/history/timeline',
            'speed_current': '/api/speed/current',
            'speed_stats': '/api/speed/stats',
            'speed_history': '/api/speed/history',
            'outages': '/api/outages/recent',
            'ping_hosts': '/api/ping/hosts',
            'health': '/health'
        }
    })


@app.route('/api/status/current')
def current_status():
    """Get current connection status"""
    query = """
        SELECT 
            timestamp,
            connection_status,
            success_rate,
            date,
            time
        FROM connection_checks
        ORDER BY timestamp DESC
        LIMIT 1
    """
    
    result = db.execute_query(query)
    
    if result:
        row = result[0]
        return jsonify({
            'timestamp': row['timestamp'].isoformat(),
            'status': row['connection_status'],
            'success_rate': float(row['success_rate']),
            'date': row['date'].isoformat(),
            'time': str(row['time'])
        })
    
    return jsonify({'error': 'No data available'}), 404


@app.route('/api/stats/today')
def stats_today():
    """Get today's statistics"""
    query = """
        SELECT 
            COUNT(*) as total_checks,
            SUM(CASE WHEN connection_status = 'online' THEN 1 ELSE 0 END) as online_checks,
            SUM(CASE WHEN connection_status = 'offline' THEN 1 ELSE 0 END) as offline_checks,
            ROUND(AVG(success_rate), 2) as avg_success_rate,
            ROUND(
                (SUM(CASE WHEN connection_status = 'online' THEN 1 ELSE 0 END)::DECIMAL / COUNT(*)) * 100,
                2
            ) as uptime_percentage,
            MIN(timestamp) as first_check,
            MAX(timestamp) as last_check
        FROM connection_checks
        WHERE date = CURRENT_DATE
    """
    
    result = db.execute_query(query)
    
    if result:
        row = result[0]
        return jsonify({
            'total_checks': row['total_checks'],
            'online_checks': row['online_checks'],
            'offline_checks': row['offline_checks'],
            'avg_success_rate': float(row['avg_success_rate']) if row['avg_success_rate'] else 0,
            'uptime_percentage': float(row['uptime_percentage']) if row['uptime_percentage'] else 0,
            'first_check': row['first_check'].isoformat() if row['first_check'] else None,
            'last_check': row['last_check'].isoformat() if row['last_check'] else None
        })
    
    return jsonify({'error': 'No data available'}), 404


@app.route('/api/stats/last24h')
def stats_last_24h():
    """Get last 24 hours statistics"""
    query = """
        SELECT 
            COUNT(*) as total_checks,
            SUM(CASE WHEN connection_status = 'online' THEN 1 ELSE 0 END) as online_checks,
            SUM(CASE WHEN connection_status = 'offline' THEN 1 ELSE 0 END) as offline_checks,
            ROUND(AVG(success_rate), 2) as avg_success_rate,
            ROUND(
                (SUM(CASE WHEN connection_status = 'online' THEN 1 ELSE 0 END)::DECIMAL / COUNT(*)) * 100,
                2
            ) as uptime_percentage
        FROM connection_checks
        WHERE timestamp >= NOW() - INTERVAL '24 hours'
    """
    
    result = db.execute_query(query)
    
    if result:
        row = result[0]
        return jsonify({
            'total_checks': row['total_checks'],
            'online_checks': row['online_checks'],
            'offline_checks': row['offline_checks'],
            'avg_success_rate': float(row['avg_success_rate']) if row['avg_success_rate'] else 0,
            'uptime_percentage': float(row['uptime_percentage']) if row['uptime_percentage'] else 0
        })
    
    return jsonify({'error': 'No data available'}), 404


@app.route('/api/history/timeline')
def history_timeline():
    """Get connection timeline for charts"""
    hours = int(request.args.get('hours', 24))
    
    query = """
        SELECT 
            timestamp,
            connection_status,
            success_rate
        FROM connection_checks
        WHERE timestamp >= NOW() - INTERVAL '%s hours'
        ORDER BY timestamp ASC
    """
    
    results = db.execute_query(query, (hours,))
    
    return jsonify([{
        'timestamp': row['timestamp'].isoformat(),
        'status': row['connection_status'],
        'success_rate': float(row['success_rate'])
    } for row in results])


@app.route('/api/speed/current')
def speed_current():
    """Get most recent speed test results"""
    query = """
        SELECT 
            st.provider,
            st.download_mbps,
            st.upload_mbps,
            st.ping_ms,
            st.server_name,
            st.server_location,
            cc.timestamp
        FROM speed_tests st
        JOIN connection_checks cc ON st.check_id = cc.id
        WHERE st.success = true
        ORDER BY cc.timestamp DESC
        LIMIT 10
    """
    
    results = db.execute_query(query)
    
    return jsonify([{
        'provider': row['provider'],
        'download_mbps': float(row['download_mbps']) if row['download_mbps'] else None,
        'upload_mbps': float(row['upload_mbps']) if row['upload_mbps'] else None,
        'ping_ms': float(row['ping_ms']) if row['ping_ms'] else None,
        'server_name': row['server_name'],
        'server_location': row['server_location'],
        'timestamp': row['timestamp'].isoformat()
    } for row in results])


@app.route('/api/speed/stats')
def speed_stats():
    """Get speed test statistics"""
    hours = int(request.args.get('hours', 24))
    
    query = """
        SELECT 
            st.provider,
            COUNT(*) as total_tests,
            ROUND(AVG(st.download_mbps), 2) as avg_download,
            ROUND(AVG(st.upload_mbps), 2) as avg_upload,
            ROUND(AVG(st.ping_ms), 2) as avg_ping,
            ROUND(MIN(st.download_mbps), 2) as min_download,
            ROUND(MAX(st.download_mbps), 2) as max_download,
            ROUND(MIN(st.upload_mbps), 2) as min_upload,
            ROUND(MAX(st.upload_mbps), 2) as max_upload
        FROM speed_tests st
        JOIN connection_checks cc ON st.check_id = cc.id
        WHERE 
            st.success = true
            AND cc.timestamp >= NOW() - INTERVAL '%s hours'
        GROUP BY st.provider
        ORDER BY st.provider
    """
    
    results = db.execute_query(query, (hours,))
    
    return jsonify([{
        'provider': row['provider'],
        'total_tests': row['total_tests'],
        'avg_download': float(row['avg_download']) if row['avg_download'] else None,
        'avg_upload': float(row['avg_upload']) if row['avg_upload'] else None,
        'avg_ping': float(row['avg_ping']) if row['avg_ping'] else None,
        'min_download': float(row['min_download']) if row['min_download'] else None,
        'max_download': float(row['max_download']) if row['max_download'] else None,
        'min_upload': float(row['min_upload']) if row['min_upload'] else None,
        'max_upload': float(row['max_upload']) if row['max_upload'] else None
    } for row in results])


@app.route('/api/outages/recent')
def outages_recent():
    """Get recent outages"""
    hours = int(request.args.get('hours', 24))
    
    query = """
        SELECT 
            timestamp,
            connection_status,
            success_rate
        FROM connection_checks
        WHERE 
            connection_status = 'offline'
            AND timestamp >= NOW() - INTERVAL '%s hours'
        ORDER BY timestamp DESC
        LIMIT 50
    """
    
    results = db.execute_query(query, (hours,))
    
    return jsonify([{
        'timestamp': row['timestamp'].isoformat(),
        'success_rate': float(row['success_rate'])
    } for row in results])


@app.route('/api/ping/hosts')
def ping_hosts():
    """Get ping statistics by host"""
    hours = int(request.args.get('hours', 24))
    
    query = """
        SELECT 
            pt.host,
            COUNT(*) as total_tests,
            SUM(CASE WHEN pt.success = true THEN 1 ELSE 0 END) as successful_tests,
            SUM(CASE WHEN pt.success = false THEN 1 ELSE 0 END) as failed_tests,
            ROUND(AVG(pt.response_time_ms), 2) as avg_response_time,
            ROUND(MIN(pt.response_time_ms), 2) as min_response_time,
            ROUND(MAX(pt.response_time_ms), 2) as max_response_time,
            ROUND(
                (SUM(CASE WHEN pt.success = true THEN 1 ELSE 0 END)::DECIMAL / COUNT(*)) * 100,
                2
            ) as success_rate
        FROM ping_tests pt
        JOIN connection_checks cc ON pt.check_id = cc.id
        WHERE cc.timestamp >= NOW() - INTERVAL '%s hours'
        GROUP BY pt.host
        ORDER BY pt.host
    """
    
    results = db.execute_query(query, (hours,))
    
    return jsonify([{
        'host': row['host'],
        'total_tests': row['total_tests'],
        'successful_tests': row['successful_tests'],
        'failed_tests': row['failed_tests'],
        'avg_response_time': float(row['avg_response_time']) if row['avg_response_time'] else None,
        'min_response_time': float(row['min_response_time']) if row['min_response_time'] else None,
        'max_response_time': float(row['max_response_time']) if row['max_response_time'] else None,
        'success_rate': float(row['success_rate']) if row['success_rate'] else 0
    } for row in results])


@app.route('/api/speed/history')
def speed_history():
    """Get speed test history for charting"""
    hours = int(request.args.get('hours', 24))
    
    query = """
        SELECT 
            cc.timestamp,
            st.provider,
            st.download_mbps,
            st.upload_mbps
        FROM speed_tests st
        JOIN connection_checks cc ON st.check_id = cc.id
        WHERE 
            st.success = true
            AND cc.timestamp >= NOW() - INTERVAL '%s hours'
        ORDER BY cc.timestamp ASC
    """
    
    results = db.execute_query(query, (hours,))
    
    return jsonify([{
        'timestamp': row['timestamp'].isoformat(),
        'provider': row['provider'],
        'download_mbps': float(row['download_mbps']) if row['download_mbps'] else None,
        'upload_mbps': float(row['upload_mbps']) if row['upload_mbps'] else None
    } for row in results])


@app.route('/api/summary')
def summary():
    """Get complete summary for dashboard"""
    return jsonify({
        'current': current_status().json,
        'today': stats_today().json,
        'last24h': stats_last_24h().json
    })


@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        # Test database connection
        conn = db.get_connection()
        conn.close()
        return jsonify({'status': 'healthy', 'database': 'connected'})
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500


if __name__ == '__main__':
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)
