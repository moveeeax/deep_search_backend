#!/bin/sh

# Создаем JavaScript объект с переменными окружения
echo "window.env = {" > /usr/share/nginx/html/env.js
echo "  API_URL: '${API_URL:-http://localhost:8080}'," >> /usr/share/nginx/html/env.js
echo "};" >> /usr/share/nginx/html/env.js