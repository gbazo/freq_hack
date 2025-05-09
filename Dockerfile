FROM python:3.11-slim

WORKDIR /app

# Copiar os requirements e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar os arquivos principais
COPY *.py ./
COPY static ./static
COPY templates ./templates
COPY .dockerignore ./

# Criar pasta de dados se não existir
RUN mkdir -p data

# Comando para executar o aplicativo
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]