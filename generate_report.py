#!/usr/bin/env python3
"""
Gerador de Relatórios de Conexão de Internet
Analisa logs e gera relatórios detalhados em português
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
from collections import defaultdict


class ReportGenerator:
    """Classe para gerar relatórios de conexão"""
    
    def __init__(self, logs_dir: str = "logs", reports_dir: str = "relatorios"):
        self.logs_dir = Path(logs_dir)
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
    
    def read_log_file(self, date: str) -> List[Dict]:
        """Lê arquivo de log de uma data específica"""
        log_file = self.logs_dir / f"log_{date}.jsonl"
        
        if not log_file.exists():
            return []
        
        logs = []
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    logs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        
        return logs
    
    def analyze_logs(self, logs: List[Dict]) -> Dict:
        """Analisa logs e gera estatísticas"""
        if not logs:
            return {
                "total_checks": 0,
                "online_checks": 0,
                "offline_checks": 0,
                "uptime_percentage": 0,
                "downtime_periods": [],
                "average_response_time": 0,
                "failed_hosts": {}
            }
        
        total_checks = len(logs)
        online_checks = sum(1 for log in logs if log["connection_status"] == "online")
        offline_checks = total_checks - online_checks
        uptime_percentage = (online_checks / total_checks * 100) if total_checks > 0 else 0
        
        # Identifica períodos de inatividade
        downtime_periods = []
        current_downtime = None
        
        for log in logs:
            timestamp = datetime.fromisoformat(log["timestamp"])
            
            if log["connection_status"] == "offline":
                if current_downtime is None:
                    current_downtime = {
                        "start": timestamp,
                        "end": timestamp
                    }
                else:
                    current_downtime["end"] = timestamp
            else:
                if current_downtime is not None:
                    duration = (current_downtime["end"] - current_downtime["start"]).total_seconds()
                    downtime_periods.append({
                        "start": current_downtime["start"].strftime("%H:%M:%S"),
                        "end": current_downtime["end"].strftime("%H:%M:%S"),
                        "duration_seconds": duration,
                        "duration_formatted": self.format_duration(duration)
                    })
                    current_downtime = None
        
        # Se ainda houver um período de inatividade em aberto
        if current_downtime is not None:
            duration = (current_downtime["end"] - current_downtime["start"]).total_seconds()
            downtime_periods.append({
                "start": current_downtime["start"].strftime("%H:%M:%S"),
                "end": current_downtime["end"].strftime("%H:%M:%S"),
                "duration_seconds": duration,
                "duration_formatted": self.format_duration(duration)
            })
        
        # Calcula tempo médio de resposta
        response_times = []
        for log in logs:
            for test in log.get("ping_tests", []) + log.get("http_tests", []):
                if test.get("success") and test.get("response_time_ms"):
                    response_times.append(test["response_time_ms"])
        
        average_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Identifica hosts com falhas
        failed_hosts = defaultdict(int)
        for log in logs:
            for test in log.get("ping_tests", []) + log.get("http_tests", []):
                if not test.get("success"):
                    target = test.get("host") or test.get("url")
                    if target:
                        failed_hosts[target] += 1
        
        # Analisa testes de velocidade
        speed_tests = []
        speed_stats = {
            "total_tests": 0,
            "successful_tests": 0,
            "providers": {}
        }
        
        for log in logs:
            for speed_test in log.get("speed_tests", []):
                speed_tests.append(speed_test)
                speed_stats["total_tests"] += 1
                
                if speed_test.get("success"):
                    speed_stats["successful_tests"] += 1
                    provider = speed_test.get("provider", "unknown")
                    
                    if provider not in speed_stats["providers"]:
                        speed_stats["providers"][provider] = {
                            "download_speeds": [],
                            "upload_speeds": [],
                            "pings": []
                        }
                    
                    if speed_test.get("download_mbps"):
                        speed_stats["providers"][provider]["download_speeds"].append(
                            speed_test["download_mbps"]
                        )
                    
                    if speed_test.get("upload_mbps"):
                        speed_stats["providers"][provider]["upload_speeds"].append(
                            speed_test["upload_mbps"]
                        )
                    
                    if speed_test.get("ping_ms"):
                        speed_stats["providers"][provider]["pings"].append(
                            speed_test["ping_ms"]
                        )
        
        # Calcula médias por provedor
        for provider, data in speed_stats["providers"].items():
            if data["download_speeds"]:
                data["avg_download"] = round(
                    sum(data["download_speeds"]) / len(data["download_speeds"]), 2
                )
                data["min_download"] = round(min(data["download_speeds"]), 2)
                data["max_download"] = round(max(data["download_speeds"]), 2)
            
            if data["upload_speeds"]:
                data["avg_upload"] = round(
                    sum(data["upload_speeds"]) / len(data["upload_speeds"]), 2
                )
                data["min_upload"] = round(min(data["upload_speeds"]), 2)
                data["max_upload"] = round(max(data["upload_speeds"]), 2)
            
            if data["pings"]:
                data["avg_ping"] = round(
                    sum(data["pings"]) / len(data["pings"]), 2
                )
        
        return {
            "total_checks": total_checks,
            "online_checks": online_checks,
            "offline_checks": offline_checks,
            "uptime_percentage": round(uptime_percentage, 2),
            "downtime_periods": downtime_periods,
            "average_response_time": round(average_response_time, 2),
            "failed_hosts": dict(failed_hosts),
            "speed_stats": speed_stats
        }
    
    def format_duration(self, seconds: float) -> str:
        """Formata duração em formato legível"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}min")
        if secs > 0 or not parts:
            parts.append(f"{secs}s")
        
        return " ".join(parts)
    
    def generate_text_report(self, date: str, stats: Dict, is_partial: bool = False) -> str:
        """Gera relatório em formato texto"""
        # Tenta fazer parse da data, se falhar usa como string direta
        try:
            date_formatted = datetime.strptime(date, "%Y-%m-%d").strftime("%d/%m/%Y")
            report_title = "RELATÓRIO DE CONEXÃO DE INTERNET"
        except ValueError:
            date_formatted = date
            report_title = "RELATÓRIO DE CONEXÃO DE INTERNET"
        
        if is_partial:
            report_title += " (PARCIAL - EM ANDAMENTO)"
        
        report = f"""
{'=' * 70}
          {report_title}
{'=' * 70}

📅 Data: {date_formatted}
⏰ Gerado em: {datetime.now().strftime("%d/%m/%Y às %H:%M:%S")}

{'=' * 70}
                    RESUMO GERAL
{'=' * 70}

Total de Verificações: {stats['total_checks']}
Verificações Online:   {stats['online_checks']} ({stats['uptime_percentage']}%)
Verificações Offline:  {stats['offline_checks']} ({100 - stats['uptime_percentage']:.2f}%)
Tempo Médio de Resposta: {stats['average_response_time']} ms

{'=' * 70}
              DISPONIBILIDADE (UPTIME)
{'=' * 70}

🟢 Uptime: {stats['uptime_percentage']}%
🔴 Downtime: {100 - stats['uptime_percentage']:.2f}%

"""
        
        if stats['downtime_periods']:
            report += f"""{'=' * 70}
           PERÍODOS DE INDISPONIBILIDADE
{'=' * 70}

Total de Interrupções: {len(stats['downtime_periods'])}

"""
            for i, period in enumerate(stats['downtime_periods'], 1):
                report += f"""Interrupção #{i}:
  🕐 Início: {period['start']}
  🕐 Fim: {period['end']}
  ⏱️  Duração: {period['duration_formatted']}

"""
            
            total_downtime = sum(p['duration_seconds'] for p in stats['downtime_periods'])
            report += f"⏱️  Tempo Total de Inatividade: {self.format_duration(total_downtime)}\n"
        else:
            report += f"""{'=' * 70}
           PERÍODOS DE INDISPONIBILIDADE
{'=' * 70}

✅ Nenhuma interrupção detectada neste dia!

"""
        
        if stats['failed_hosts']:
            report += f"""{'=' * 70}
              HOSTS COM FALHAS
{'=' * 70}

"""
            for host, count in sorted(stats['failed_hosts'].items(), key=lambda x: x[1], reverse=True):
                report += f"  • {host}: {count} falhas\n"
        
        # Estatísticas de velocidade
        speed_stats = stats.get('speed_stats', {})
        if speed_stats.get('total_tests', 0) > 0:
            report += f"""
{'=' * 70}
           VELOCIDADE DA INTERNET
{'=' * 70}

Total de Testes de Velocidade: {speed_stats['total_tests']}
Testes Bem-Sucedidos: {speed_stats['successful_tests']}

"""
            # Relatório por provedor
            for provider, data in speed_stats.get('providers', {}).items():
                report += f"📊 {provider.upper()}\n"
                
                if data.get('avg_download'):
                    report += f"   Download: {data['avg_download']} Mbps (média)\n"
                    report += f"            {data['min_download']} Mbps (mín) - {data['max_download']} Mbps (máx)\n"
                
                if data.get('avg_upload'):
                    report += f"   Upload:   {data['avg_upload']} Mbps (média)\n"
                    report += f"            {data['min_upload']} Mbps (mín) - {data['max_upload']} Mbps (máx)\n"
                
                if data.get('avg_ping'):
                    report += f"   Ping:     {data['avg_ping']} ms (média)\n"
                
                report += "\n"
        
        report += f"""
{'=' * 70}
                  CONCLUSÃO
{'=' * 70}

"""
        
        if stats['uptime_percentage'] >= 99:
            report += "✅ Conexão EXCELENTE - Muito estável durante o período.\n"
        elif stats['uptime_percentage'] >= 95:
            report += "✔️  Conexão BOA - Algumas interrupções menores detectadas.\n"
        elif stats['uptime_percentage'] >= 90:
            report += "⚠️  Conexão REGULAR - Várias interrupções detectadas.\n"
        else:
            report += "❌ Conexão RUIM - Muitas interrupções e instabilidade.\n"
        
        if is_partial:
            report += "\n⚠️  NOTA: Este é um relatório PARCIAL gerado durante o monitoramento.\n"
            report += "   Os dados ainda estão sendo coletados e podem mudar.\n"
            report += "   Um relatório final será gerado ao final do dia.\n"
        
        report += f"""
{'=' * 70}

Este relatório foi gerado automaticamente pelo Monitor de Internet.
Para dúvidas ou suporte, entre em contato com seu provedor de internet
apresentando este documento.

{'=' * 70}
"""
        
        return report
    
    def generate_json_report(self, date: str, stats: Dict) -> Dict:
        """Gera relatório em formato JSON"""
        return {
            "date": date,
            "generated_at": datetime.now().isoformat(),
            "statistics": stats,
            "report_version": "1.0"
        }
    
    def generate_detailed_report(self, date: str, logs: List[Dict]) -> str:
        """Gera relatório detalhado com todos os checks individuais"""
        try:
            date_formatted = datetime.strptime(date, "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            date_formatted = date
        
        report = f"""
{'=' * 80}
               RELATÓRIO DETALHADO DE CONEXÃO DE INTERNET
{'=' * 80}

📅 Data: {date_formatted}
⏰ Gerado em: {datetime.now().strftime("%d/%m/%Y às %H:%M:%S")}
📋 Total de Verificações: {len(logs)}

{'=' * 80}
                    HISTÓRICO COMPLETO DE VERIFICAÇÕES
{'=' * 80}

"""
        
        for i, log in enumerate(logs, 1):
            timestamp = log.get("time", "N/A")
            status = log.get("connection_status", "unknown")
            success_rate = log.get("success_rate", 0)
            
            status_icon = "✅" if status == "online" else "❌"
            
            report += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Verificação #{i} - {timestamp}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Status: {status_icon} {status.upper()} (Taxa de sucesso: {success_rate}%)

"""
            
            # Testes de Ping
            if log.get("ping_tests"):
                report += "🔹 Testes de Ping:\n"
                for test in log["ping_tests"]:
                    host = test.get("host", "N/A")
                    success = "✅" if test.get("success") else "❌"
                    response_time = test.get("response_time_ms", "N/A")
                    error = test.get("error", "")
                    
                    if test.get("success"):
                        report += f"   {success} {host}: {response_time} ms\n"
                    else:
                        report += f"   {success} {host}: FALHOU - {error}\n"
                report += "\n"
            
            # Testes HTTP
            if log.get("http_tests"):
                report += "🔹 Testes HTTP:\n"
                for test in log["http_tests"]:
                    url = test.get("url", "N/A")
                    success = "✅" if test.get("success") else "❌"
                    response_time = test.get("response_time_ms", "N/A")
                    status_code = test.get("status_code", "N/A")
                    error = test.get("error", "")
                    
                    if test.get("success"):
                        report += f"   {success} {url}: {response_time} ms (Status: {status_code})\n"
                    else:
                        report += f"   {success} {url}: FALHOU - {error}\n"
                report += "\n"
            
            # Testes DNS
            if log.get("dns_tests"):
                report += "🔹 Testes DNS:\n"
                for test in log["dns_tests"]:
                    hostname = test.get("hostname", "N/A")
                    success = "✅" if test.get("success") else "❌"
                    ip = test.get("ip_address", "N/A")
                    response_time = test.get("response_time_ms", "N/A")
                    error = test.get("error", "")
                    
                    if test.get("success"):
                        report += f"   {success} {hostname} → {ip} ({response_time} ms)\n"
                    else:
                        report += f"   {success} {hostname}: FALHOU - {error}\n"
                report += "\n"
            
            # Testes de Velocidade
            if log.get("speed_tests") and len(log["speed_tests"]) > 0:
                report += "🚀 Testes de Velocidade:\n"
                for test in log["speed_tests"]:
                    provider = test.get("provider", "N/A")
                    success = "✅" if test.get("success") else "❌"
                    
                    if test.get("success"):
                        download = test.get("download_mbps", "N/A")
                        upload = test.get("upload_mbps", "N/A")
                        ping = test.get("ping_ms", "N/A")
                        
                        report += f"   {success} {provider}:\n"
                        if download != "N/A" and download is not None:
                            report += f"      ↓ Download: {download} Mbps\n"
                        if upload != "N/A" and upload is not None:
                            report += f"      ↑ Upload: {upload} Mbps\n"
                        if ping != "N/A" and ping is not None:
                            report += f"      📶 Ping: {ping} ms\n"
                    else:
                        error = test.get("error", "Erro desconhecido")
                        report += f"   {success} {provider}: FALHOU - {error}\n"
                report += "\n"
        
        report += f"""
{'=' * 80}

Este relatório detalhado contém TODOS os {len(logs)} checks realizados durante o dia.
Para um resumo estatístico, veja o relatório parcial.

{'=' * 80}
"""
        
        return report
    
    def generate_report(self, date: str = None) -> str:
        """Gera relatório para uma data específica"""
        if date is None:
            date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        logs = self.read_log_file(date)
        
        if not logs:
            return f"⚠️  Nenhum log encontrado para a data {date}"
        
        stats = self.analyze_logs(logs)
        
        # Gera relatório em texto
        text_report = self.generate_text_report(date, stats)
        report_file = self.reports_dir / f"relatorio_{date}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(text_report)
        
        # Gera relatório em JSON
        json_report = self.generate_json_report(date, stats)
        json_file = self.reports_dir / f"relatorio_{date}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_report, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Relatório gerado com sucesso!")
        print(f"📄 Texto: {report_file.absolute()}")
        print(f"📊 JSON: {json_file.absolute()}")
        
        return text_report
    
    def generate_weekly_report(self) -> str:
        """Gera relatório semanal consolidado"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        all_logs = []
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            logs = self.read_log_file(date_str)
            all_logs.extend(logs)
            current_date += timedelta(days=1)
        
        if not all_logs:
            return "⚠️  Nenhum log encontrado para a última semana"
        
        stats = self.analyze_logs(all_logs)
        
        # Gera relatório semanal
        report_date = f"{start_date.strftime('%Y-%m-%d')}_to_{end_date.strftime('%Y-%m-%d')}"
        text_report = self.generate_text_report(f"Semana de {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}", stats)
        
        report_file = self.reports_dir / f"relatorio_semanal_{report_date}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(text_report)
        
        print(f"✅ Relatório semanal gerado!")
        print(f"📄 {report_file.absolute()}")
        
        return text_report


if __name__ == "__main__":
    import sys
    
    generator = ReportGenerator()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--weekly":
            print(generator.generate_weekly_report())
        else:
            date = sys.argv[1]
            print(generator.generate_report(date))
    else:
        # Gera relatório do dia anterior
        print(generator.generate_report())
