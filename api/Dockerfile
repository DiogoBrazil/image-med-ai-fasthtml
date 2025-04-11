FROM rocker/ml-verse:latest

# Configurar variáveis de ambiente para evitar interatividade durante a instalação
ENV DEBIAN_FRONTEND=noninteractive

# Atualizar e instalar dependências adicionais para Python e o ambiente
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    libpq-dev \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configurar diretório de trabalho
WORKDIR /app

# Copiar apenas o arquivo de requisitos primeiro
COPY requirements.txt .

# Instalar dependências Python
RUN pip3 install --no-cache-dir -r requirements.txt

# Copiar o restante do código-fonte
COPY . .

# Verificação de saúde da API
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8000/api/status || exit 1

# Expor a porta da API
EXPOSE 8000

# Iniciar o servidor
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]