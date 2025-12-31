FROM python:3.11-slim

# Define metadata
LABEL maintainer="Internet Monitor"
LABEL description="Sistema de Monitoramento de Conexão de Internet"

# Define diretório de trabalho
WORKDIR /app

# Instala dependências do sistema necessárias para ping
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Copia arquivos de dependências
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia os scripts da aplicação
COPY monitor_internet.py .
COPY generate_report.py .
COPY database.py .
COPY dashboard.py .
COPY config.json .

# Copia templates para dashboard
COPY templates/ ./templates/

# Cria diretórios para logs e relatórios
RUN mkdir -p /app/logs /app/relatorios

# Define volumes para persistência de dados
VOLUME ["/app/logs", "/app/relatorios"]

# Desabilita buffering do Python para ver logs em tempo real
ENV PYTHONUNBUFFERED=1

# Comando padrão: executar o monitor (com -u para unbuffered output)
CMD ["python", "-u", "monitor_internet.py"]
