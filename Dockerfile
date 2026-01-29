FROM python:3.11-slim

# Устанавливаем браузер
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Python библиотеки
RUN pip install --no-cache-dir \
    selenium \
    python-docx

# Рабочая папка
WORKDIR /app

# Копируем наш скрипт
COPY script.py .

# Папка для результатов
RUN mkdir /app/output

# Запускаем скрипт
CMD ["python", "script.py"]