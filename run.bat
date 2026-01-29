@echo off
echo Создаем папку для результатов...
mkdir output 2>nul

echo Собираем Docker образ...
docker build -t web-to-doc .

echo Запускаем автоматизацию...
docker run -v "%cd%\output:/app/output" web-to-doc

echo Готово! Проверьте папку output
pause