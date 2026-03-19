FROM python:3.13-slim

# Variáveis de ambiente para otimizar o comportamento do Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Definir locale
ENV LANG=pt_BR.UTF-8
ENV LANGUAGE=pt_BR:pt
ENV LC_ALL=pt_BR.UTF-8

# Atualiza pacotes do sistema e instala o cliente do PostgreSQL e curl
RUN apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends postgresql-client curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Baixar Tailwind CSS CLI v4 para Linux
RUN curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/download/v4.1.18/tailwindcss-linux-x64 && \
    mv tailwindcss-linux-x64 /usr/local/bin/tailwindcss && \
    chmod +x /usr/local/bin/tailwindcss

# Definir diretório de trabalho
WORKDIR /code

# Copiar e instalar dependências do projeto
COPY requirements.txt /code/
RUN pip install -U pip
RUN pip install -r requirements.txt

# Copiar o resto do código da aplicação
COPY . /code/

# Build Tailwind CSS no container
RUN tailwindcss -i /code/core/static/core/css/input.css -o /code/core/static/core/css/output.css --minify
