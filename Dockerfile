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

# Expose the port the app runs on
EXPOSE 8000

# Environment variable for the port
ENV PORT=8000

# Command to run the application
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
