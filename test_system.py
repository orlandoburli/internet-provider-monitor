#!/usr/bin/env python3
"""
Script de teste para verificar se o sistema está funcionando
"""

import sys
import subprocess
from pathlib import Path

def test_python_version():
    """Verifica versão do Python"""
    version = sys.version_info
    print(f"🐍 Python: {version.major}.{version.minor}.{version.micro}", end=" ")
    if version.major >= 3 and version.minor >= 7:
        print("✅")
        return True
    else:
        print("❌ (necessário Python 3.7+)")
        return False

def test_dependencies():
    """Verifica dependências instaladas"""
    print("📦 Dependências:")
    try:
        import requests
        print(f"   - requests: {requests.__version__} ✅")
        return True
    except ImportError:
        print("   - requests: ❌ NÃO INSTALADO")
        print("     Execute: pip3 install -r requirements.txt")
        return False

def test_config_file():
    """Verifica arquivo de configuração"""
    print("⚙️  Configuração:", end=" ")
    if Path("config.json").exists():
        print("✅")
        return True
    else:
        print("❌ (config.json não encontrado)")
        return False

def test_scripts():
    """Verifica scripts principais"""
    print("📜 Scripts:")
    all_ok = True
    
    scripts = {
        "monitor_internet.py": "Monitor principal",
        "generate_report.py": "Gerador de relatórios"
    }
    
    for script, desc in scripts.items():
        if Path(script).exists():
            print(f"   - {desc}: ✅")
        else:
            print(f"   - {desc}: ❌")
            all_ok = False
    
    return all_ok

def test_directories():
    """Cria diretórios necessários"""
    print("📁 Diretórios:", end=" ")
    try:
        Path("logs").mkdir(exist_ok=True)
        Path("relatorios").mkdir(exist_ok=True)
        print("✅")
        return True
    except Exception as e:
        print(f"❌ ({e})")
        return False

def test_connection():
    """Testa uma verificação rápida"""
    print("🌐 Teste de Conexão:", end=" ")
    try:
        import requests
        response = requests.get("https://www.google.com", timeout=5)
        if response.status_code == 200:
            print("✅ (Internet funcionando)")
            return True
        else:
            print(f"⚠️  (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ ({e})")
        return False

def main():
    print("=" * 60)
    print("        TESTE DO SISTEMA DE MONITORAMENTO")
    print("=" * 60)
    print()
    
    results = []
    
    results.append(test_python_version())
    results.append(test_dependencies())
    results.append(test_config_file())
    results.append(test_scripts())
    results.append(test_directories())
    results.append(test_connection())
    
    print()
    print("=" * 60)
    
    if all(results):
        print("✅ SISTEMA PRONTO PARA USO!")
        print()
        print("Para iniciar o monitoramento:")
        print("  ./start.sh")
        print()
        print("Ou diretamente:")
        print("  python3 monitor_internet.py")
    else:
        print("⚠️  SISTEMA COM PROBLEMAS")
        print()
        print("Corrija os erros acima antes de continuar.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
