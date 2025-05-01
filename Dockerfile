# Usa uma imagem base do Python
FROM python:3.12

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos para o container
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "run.py"]
