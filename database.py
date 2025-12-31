#!/usr/bin/env python3
"""
Módulo de banco de dados PostgreSQL
Gerencia conexão e armazenamento de dados de monitoramento
"""

import os
import psycopg2
from psycopg2.extras import Json, execute_values
from datetime import datetime
from typing import Dict, List, Optional
import json


class DatabaseManager:
    """Gerencia conexão e operações com PostgreSQL"""
    
    def __init__(self, config: Dict = None):
        """Inicializa gerenciador de banco de dados"""
        self.config = config or {}
        self.connection = None
        self.enabled = self.config.get("enable_database", False)
        
        if self.enabled:
            self.connect()
    
    def get_connection_params(self) -> Dict:
        """Retorna parâmetros de conexão do banco"""
        return {
            "host": os.getenv("POSTGRES_HOST", self.config.get("db_host", "postgres")),
            "port": os.getenv("POSTGRES_PORT", self.config.get("db_port", 5432)),
            "database": os.getenv("POSTGRES_DB", self.config.get("db_name", "internet_monitor")),
            "user": os.getenv("POSTGRES_USER", self.config.get("db_user", "monitor")),
            "password": os.getenv("POSTGRES_PASSWORD", self.config.get("db_password", "monitor123"))
        }
    
    def connect(self):
        """Estabelece conexão com o banco de dados"""
        if not self.enabled:
            return
        
        try:
            params = self.get_connection_params()
            self.connection = psycopg2.connect(**params)
            print(f"✅ Conectado ao PostgreSQL: {params['host']}:{params['port']}/{params['database']}")
            self.init_schema()
        except psycopg2.OperationalError as e:
            print(f"⚠️  Não foi possível conectar ao PostgreSQL: {e}")
            print(f"   Continuando sem banco de dados (apenas arquivos)")
            self.enabled = False
            self.connection = None
        except Exception as e:
            print(f"⚠️  Erro ao conectar ao banco: {e}")
            self.enabled = False
            self.connection = None
    
    def init_schema(self):
        """Inicializa schema do banco de dados"""
        if not self.connection:
            return
        
        try:
            cursor = self.connection.cursor()
            
            # Tabela principal de verificações
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS connection_checks (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    date DATE NOT NULL,
                    time TIME NOT NULL,
                    connection_status VARCHAR(20) NOT NULL,
                    success_rate DECIMAL(5,2) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON connection_checks(timestamp)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_date ON connection_checks(date)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_status ON connection_checks(connection_status)
            """)
            
            # Tabela de testes de ping
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ping_tests (
                    id SERIAL PRIMARY KEY,
                    check_id INTEGER REFERENCES connection_checks(id) ON DELETE CASCADE,
                    host VARCHAR(255) NOT NULL,
                    success BOOLEAN NOT NULL,
                    response_time_ms DECIMAL(10,2),
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_ping_check_id ON ping_tests(check_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_ping_host ON ping_tests(host)
            """)
            
            # Tabela de testes HTTP
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS http_tests (
                    id SERIAL PRIMARY KEY,
                    check_id INTEGER REFERENCES connection_checks(id) ON DELETE CASCADE,
                    url VARCHAR(500) NOT NULL,
                    success BOOLEAN NOT NULL,
                    response_time_ms DECIMAL(10,2),
                    status_code INTEGER,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_http_check_id ON http_tests(check_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_http_url ON http_tests(url)
            """)
            
            # Tabela de testes DNS
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dns_tests (
                    id SERIAL PRIMARY KEY,
                    check_id INTEGER REFERENCES connection_checks(id) ON DELETE CASCADE,
                    hostname VARCHAR(255) NOT NULL,
                    success BOOLEAN NOT NULL,
                    ip_address VARCHAR(45),
                    response_time_ms DECIMAL(10,2),
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_dns_check_id ON dns_tests(check_id)
            """)
            
            # Tabela de testes de velocidade
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS speed_tests (
                    id SERIAL PRIMARY KEY,
                    check_id INTEGER REFERENCES connection_checks(id) ON DELETE CASCADE,
                    provider VARCHAR(100) NOT NULL,
                    success BOOLEAN NOT NULL,
                    download_mbps DECIMAL(10,2),
                    upload_mbps DECIMAL(10,2),
                    ping_ms DECIMAL(10,2),
                    server_name VARCHAR(255),
                    server_location VARCHAR(255),
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_speed_check_id ON speed_tests(check_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_speed_provider ON speed_tests(provider)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_speed_timestamp ON speed_tests(created_at)
            """)
            
            self.connection.commit()
            cursor.close()
            print("✅ Schema do banco de dados inicializado")
            
        except Exception as e:
            print(f"⚠️  Erro ao inicializar schema: {e}")
            if self.connection:
                self.connection.rollback()
    
    def save_check(self, check_data: Dict) -> Optional[int]:
        """Salva uma verificação completa no banco de dados"""
        if not self.enabled or not self.connection:
            return None
        
        try:
            cursor = self.connection.cursor()
            
            # Inserir verificação principal
            cursor.execute("""
                INSERT INTO connection_checks 
                (timestamp, date, time, connection_status, success_rate)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (
                check_data["timestamp"],
                check_data["date"],
                check_data["time"],
                check_data["connection_status"],
                check_data["success_rate"]
            ))
            
            check_id = cursor.fetchone()[0]
            
            # Inserir testes de ping
            if check_data.get("ping_tests"):
                ping_values = [
                    (
                        check_id,
                        test.get("host"),
                        test.get("success", False),
                        test.get("response_time_ms"),
                        test.get("error")
                    )
                    for test in check_data["ping_tests"]
                ]
                
                execute_values(
                    cursor,
                    """
                    INSERT INTO ping_tests 
                    (check_id, host, success, response_time_ms, error_message)
                    VALUES %s
                    """,
                    ping_values
                )
            
            # Inserir testes HTTP
            if check_data.get("http_tests"):
                http_values = [
                    (
                        check_id,
                        test.get("url"),
                        test.get("success", False),
                        test.get("response_time_ms"),
                        test.get("status_code"),
                        test.get("error")
                    )
                    for test in check_data["http_tests"]
                ]
                
                execute_values(
                    cursor,
                    """
                    INSERT INTO http_tests 
                    (check_id, url, success, response_time_ms, status_code, error_message)
                    VALUES %s
                    """,
                    http_values
                )
            
            # Inserir testes DNS
            if check_data.get("dns_tests"):
                dns_values = [
                    (
                        check_id,
                        test.get("hostname"),
                        test.get("success", False),
                        test.get("ip_address"),
                        test.get("response_time_ms"),
                        test.get("error")
                    )
                    for test in check_data["dns_tests"]
                ]
                
                execute_values(
                    cursor,
                    """
                    INSERT INTO dns_tests 
                    (check_id, hostname, success, ip_address, response_time_ms, error_message)
                    VALUES %s
                    """,
                    dns_values
                )
            
            # Inserir testes de velocidade
            if check_data.get("speed_tests"):
                speed_values = [
                    (
                        check_id,
                        test.get("provider"),
                        test.get("success", False),
                        test.get("download_mbps"),
                        test.get("upload_mbps"),
                        test.get("ping_ms"),
                        test.get("server"),
                        test.get("location"),
                        test.get("error")
                    )
                    for test in check_data["speed_tests"]
                ]
                
                execute_values(
                    cursor,
                    """
                    INSERT INTO speed_tests 
                    (check_id, provider, success, download_mbps, upload_mbps, 
                     ping_ms, server_name, server_location, error_message)
                    VALUES %s
                    """,
                    speed_values
                )
            
            self.connection.commit()
            cursor.close()
            return check_id
            
        except Exception as e:
            print(f"⚠️  Erro ao salvar no banco: {e}")
            if self.connection:
                self.connection.rollback()
            return None
    
    def close(self):
        """Fecha conexão com o banco de dados"""
        if self.connection:
            self.connection.close()
            print("✅ Conexão com PostgreSQL fechada")
    
    def __del__(self):
        """Destrutor - fecha conexão"""
        self.close()
