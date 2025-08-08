FROM python:3.9-slim

WORKDIR /app

# Создаем папку для БД
RUN mkdir -p /data && chmod 777 /data

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-u", "main.py"]