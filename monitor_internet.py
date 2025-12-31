#!/usr/bin/env python3
"""
Monitor de Conexão de Internet
Monitora continuamente a conexão de internet e registra logs detalhados
"""

import time
import json
import socket
import subprocess
import platform
from datetime import datetime
from pathlib import Path
import requests
from typing import Dict, List, Optional


class InternetMonitor:
    """Classe principal para monitoramento de internet"""
    
    def __init__(self, config_path: str = "config.json"):
        """Inicializa o monitor com configurações"""
        self.config = self.load_config(config_path)
        self.logs_dir = Path(self.config.get("logs_directory", "logs"))
        self.logs_dir.mkdir(exist_ok=True)
        self.reports_dir = Path(self.config.get("reports_directory", "relatorios"))
        self.reports_dir.mkdir(exist_ok=True)
        
        # Inicializa banco de dados
        self.db = None
        if self.config.get("enable_database", False):
            try:
                from database import DatabaseManager
                self.db = DatabaseManager(self.config)
            except ImportError:
                print("⚠️  Módulo database não encontrado. Continuando sem banco de dados.")
            except Exception as e:
                print(f"⚠️  Erro ao inicializar banco de dados: {e}")
        
    def load_config(self, config_path: str) -> Dict:
        """Carrega configurações do arquivo JSON"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Arquivo de configuração não encontrado. Usando configurações padrão.")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """Retorna configurações padrão"""
        return {
            "check_interval": 60,
            "report_interval": 300,
            "enable_speed_tests": True,
            "ping_hosts": [
                "8.8.8.8",
                "1.1.1.1",
                "google.com"
            ],
            "http_test_urls": [
                "https://www.google.com",
                "https://www.cloudflare.com"
            ],
            "speed_test_providers": [
                "speedtest",
                "http_download"
            ],
            "http_download_urls": [
                "https://speed.cloudflare.com/__down?bytes=10000000",
                "https://proof.ovh.net/files/10Mb.dat"
            ],
            "logs_directory": "logs",
            "reports_directory": "relatorios",
            "ping_timeout": 5,
            "http_timeout": 10
        }
    
    def check_ping(self, host: str, timeout: int = 5) -> Dict:
        """Verifica conectividade usando ping"""
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        timeout_param = '-w' if platform.system().lower() == 'windows' else '-W'
        
        command = ['ping', param, '1', timeout_param, str(timeout), host]
        
        try:
            start_time = time.time()
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout + 2
            )
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # em ms
            
            return {
                "host": host,
                "success": result.returncode == 0,
                "response_time_ms": round(response_time, 2),
                "method": "ping"
            }
        except subprocess.TimeoutExpired:
            return {
                "host": host,
                "success": False,
                "response_time_ms": None,
                "error": "Timeout",
                "method": "ping"
            }
        except Exception as e:
            return {
                "host": host,
                "success": False,
                "response_time_ms": None,
                "error": str(e),
                "method": "ping"
            }
    
    def check_http(self, url: str, timeout: int = 10) -> Dict:
        """Verifica conectividade HTTP/HTTPS"""
        try:
            start_time = time.time()
            response = requests.get(url, timeout=timeout)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # em ms
            
            return {
                "url": url,
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response_time_ms": round(response_time, 2),
                "method": "http"
            }
        except requests.Timeout:
            return {
                "url": url,
                "success": False,
                "error": "Timeout",
                "method": "http"
            }
        except Exception as e:
            return {
                "url": url,
                "success": False,
                "error": str(e),
                "method": "http"
            }
    
    def check_dns(self, hostname: str = "google.com") -> Dict:
        """Verifica resolução DNS"""
        try:
            start_time = time.time()
            ip_address = socket.gethostbyname(hostname)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # em ms
            
            return {
                "hostname": hostname,
                "success": True,
                "ip_address": ip_address,
                "response_time_ms": round(response_time, 2),
                "method": "dns"
            }
        except socket.gaierror as e:
            return {
                "hostname": hostname,
                "success": False,
                "error": str(e),
                "method": "dns"
            }
        except Exception as e:
            return {
                "hostname": hostname,
                "success": False,
                "error": str(e),
                "method": "dns"
            }
    
    def test_speed_speedtest(self) -> Dict:
        """Testa velocidade usando Speedtest.net (Ookla)"""
        try:
            import speedtest
            
            print("  🔄 Testando velocidade via Speedtest.net...")
            st = speedtest.Speedtest()
            st.get_best_server()
            
            download_speed = st.download() / 1_000_000  # Mbps
            upload_speed = st.upload() / 1_000_000  # Mbps
            ping = st.results.ping
            
            server = st.results.server
            
            return {
                "provider": "speedtest.net",
                "success": True,
                "download_mbps": round(download_speed, 2),
                "upload_mbps": round(upload_speed, 2),
                "ping_ms": round(ping, 2),
                "server": server.get("sponsor", "Unknown"),
                "location": f"{server.get('name', 'Unknown')}, {server.get('country', 'Unknown')}",
                "method": "speedtest"
            }
        except ImportError:
            return {
                "provider": "speedtest.net",
                "success": False,
                "error": "speedtest-cli não instalado",
                "method": "speedtest"
            }
        except Exception as e:
            return {
                "provider": "speedtest.net",
                "success": False,
                "error": str(e),
                "method": "speedtest"
            }
    
    def test_speed_http_download(self, url: str, test_size_mb: int = 10) -> Dict:
        """Testa velocidade de download via HTTP"""
        try:
            print(f"  🔄 Testando download de {url}...")
            
            start_time = time.time()
            response = requests.get(url, timeout=60, stream=True)
            
            if response.status_code != 200:
                return {
                    "provider": url,
                    "success": False,
                    "error": f"Status code: {response.status_code}",
                    "method": "http_download"
                }
            
            # Download em chunks
            total_bytes = 0
            chunk_size = 8192
            
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    total_bytes += len(chunk)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Calcula velocidade em Mbps
            download_speed = (total_bytes * 8) / (duration * 1_000_000)
            
            return {
                "provider": url.split('/')[2],  # Extract domain
                "success": True,
                "download_mbps": round(download_speed, 2),
                "upload_mbps": None,  # HTTP download não testa upload
                "duration_seconds": round(duration, 2),
                "bytes_downloaded": total_bytes,
                "method": "http_download"
            }
        except requests.Timeout:
            return {
                "provider": url.split('/')[2] if '/' in url else url,
                "success": False,
                "error": "Timeout",
                "method": "http_download"
            }
        except Exception as e:
            return {
                "provider": url.split('/')[2] if '/' in url else url,
                "success": False,
                "error": str(e),
                "method": "http_download"
            }
    
    def run_speed_tests(self) -> List[Dict]:
        """Executa todos os testes de velocidade configurados"""
        if not self.config.get("enable_speed_tests", True):
            return []
        
        print("📊 Executando testes de velocidade...")
        results = []
        
        providers = self.config.get("speed_test_providers", ["speedtest"])
        
        # Speedtest.net (Ookla)
        if "speedtest" in providers:
            speedtest_result = self.test_speed_speedtest()
            results.append(speedtest_result)
            if speedtest_result.get("success"):
                print(f"  ✅ Speedtest.net: ↓ {speedtest_result['download_mbps']} Mbps / ↑ {speedtest_result['upload_mbps']} Mbps")
        
        # HTTP Download tests
        if "http_download" in providers:
            download_urls = self.config.get("http_download_urls", [])
            for url in download_urls:
                download_result = self.test_speed_http_download(url)
                results.append(download_result)
                if download_result.get("success"):
                    print(f"  ✅ {download_result['provider']}: ↓ {download_result['download_mbps']} Mbps")
        
        return results
    
    def run_full_check(self, include_speed_test: bool = False) -> Dict:
        """Executa verificação completa da conexão"""
        timestamp = datetime.now()
        
        results = {
            "timestamp": timestamp.isoformat(),
            "date": timestamp.strftime("%Y-%m-%d"),
            "time": timestamp.strftime("%H:%M:%S"),
            "ping_tests": [],
            "http_tests": [],
            "dns_tests": [],
            "speed_tests": []
        }
        
        # Testes de ping
        for host in self.config["ping_hosts"]:
            ping_result = self.check_ping(host, self.config["ping_timeout"])
            results["ping_tests"].append(ping_result)
        
        # Testes HTTP
        for url in self.config["http_test_urls"]:
            http_result = self.check_http(url, self.config["http_timeout"])
            results["http_tests"].append(http_result)
        
        # Teste DNS
        dns_result = self.check_dns()
        results["dns_tests"].append(dns_result)
        
        # Testes de velocidade (se solicitado)
        if include_speed_test:
            speed_results = self.run_speed_tests()
            results["speed_tests"] = speed_results
        
        # Determina status geral
        all_tests = results["ping_tests"] + results["http_tests"] + results["dns_tests"]
        successful_tests = sum(1 for test in all_tests if test.get("success", False))
        total_tests = len(all_tests)
        
        results["connection_status"] = "online" if successful_tests > 0 else "offline"
        results["success_rate"] = round((successful_tests / total_tests) * 100, 2) if total_tests > 0 else 0
        
        return results
    
    def log_results(self, results: Dict):
        """Salva resultados em arquivo de log e banco de dados"""
        date = results["date"]
        log_file = self.logs_dir / f"log_{date}.jsonl"
        
        # Salva em arquivo (sempre)
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(results, ensure_ascii=False) + '\n')
        
        # Salva no banco de dados (se habilitado)
        if self.db and self.db.enabled:
            try:
                check_id = self.db.save_check(results)
                if check_id:
                    print(f"   💾 Salvo no banco de dados (ID: {check_id})")
            except Exception as e:
                print(f"   ⚠️  Erro ao salvar no banco: {e}")
    
    def print_status(self, results: Dict):
        """Imprime status no console"""
        timestamp = results["time"]
        status = results["connection_status"]
        success_rate = results["success_rate"]
        
        status_icon = "✅" if status == "online" else "❌"
        print(f"[{timestamp}] {status_icon} Status: {status.upper()} - Taxa de sucesso: {success_rate}%")
        
        # Mostra falhas se houver
        all_tests = results["ping_tests"] + results["http_tests"] + results["dns_tests"]
        failed_tests = [test for test in all_tests if not test.get("success", False)]
        
        if failed_tests:
            print("  ⚠️  Falhas detectadas:")
            for test in failed_tests:
                if "host" in test:
                    print(f"    - Ping para {test['host']}: {test.get('error', 'Falhou')}")
                elif "url" in test:
                    print(f"    - HTTP para {test['url']}: {test.get('error', 'Falhou')}")
                elif "hostname" in test:
                    print(f"    - DNS para {test['hostname']}: {test.get('error', 'Falhou')}")
    
    def generate_current_report(self):
        """Gera relatório do dia atual (incremental)"""
        try:
            from generate_report import ReportGenerator
            
            generator = ReportGenerator(
                logs_dir=str(self.logs_dir),
                reports_dir=str(self.reports_dir)
            )
            
            today = datetime.now().strftime("%Y-%m-%d")
            current_time = datetime.now().strftime("%H%M")
            logs = generator.read_log_file(today)
            
            if not logs:
                return
            
            stats = generator.analyze_logs(logs)
            
            # Gera relatório parcial PRINCIPAL (sobrescreve para ver sempre o mais recente)
            text_report = generator.generate_text_report(today, stats, is_partial=True)
            report_file = self.reports_dir / f"relatorio_parcial_{today}.txt"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(text_report)
            
            # Gera SNAPSHOT com timestamp (NÃO sobrescreve - mantém histórico)
            snapshot_file = self.reports_dir / f"relatorio_snapshot_{today}_{current_time}.txt"
            with open(snapshot_file, 'w', encoding='utf-8') as f:
                f.write(text_report)
            
            # Gera relatório DETALHADO com todos os checks (incremental)
            detailed_report = generator.generate_detailed_report(today, logs)
            detailed_file = self.reports_dir / f"relatorio_detalhado_{today}.txt"
            
            with open(detailed_file, 'w', encoding='utf-8') as f:
                f.write(detailed_report)
            
            # Gera também JSON
            json_report = generator.generate_json_report(today, stats)
            json_file = self.reports_dir / f"relatorio_parcial_{today}.json"
            
            with open(json_file, 'w', encoding='utf-8') as f:
                import json
                json.dump(json_report, f, ensure_ascii=False, indent=2)
            
            print(f"📊 Relatórios atualizados: parcial + snapshot {current_time} + detalhado")
            
        except Exception as e:
            print(f"⚠️  Erro ao gerar relatório: {e}")
    
    def run(self):
        """Inicia o monitoramento contínuo"""
        print("🌐 Monitor de Internet Iniciado")
        print(f"📊 Intervalo de verificação: {self.config['check_interval']} segundos")
        print(f"📄 Intervalo de relatórios: {self.config.get('report_interval', 300)} segundos")
        
        if self.config.get("enable_speed_tests", True):
            print(f"🚀 Testes de velocidade: Habilitados (a cada verificação)")
        else:
            print(f"🚀 Testes de velocidade: Desabilitados")
        
        print(f"📁 Logs salvos em: {self.logs_dir.absolute()}")
        print(f"📄 Relatórios salvos em: {self.reports_dir.absolute()}")
        print("-" * 60)
        
        check_count = 0
        report_interval_checks = self.config.get('report_interval', 300) // self.config['check_interval']
        
        try:
            while True:
                # Executa testes (incluindo speed test se habilitado)
                should_speed_test = self.config.get("enable_speed_tests", True)
                
                results = self.run_full_check(include_speed_test=should_speed_test)
                self.log_results(results)
                self.print_status(results)
                
                check_count += 1
                
                # Gera relatório a cada X verificações (baseado no report_interval)
                if check_count >= report_interval_checks:
                    self.generate_current_report()
                    check_count = 0
                
                time.sleep(self.config["check_interval"])
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Monitor interrompido pelo usuário")
            print("✅ Logs salvos com sucesso")
            print("📊 Gerando relatório final...")
            self.generate_current_report()
            print("✅ Relatório final gerado")
            
            # Fecha conexão com banco de dados
            if self.db:
                self.db.close()


if __name__ == "__main__":
    monitor = InternetMonitor()
    monitor.run()
