# Используем официальный образ nginx
FROM nginx:alpine

# Копируем файлы фронтенда в директорию nginx
COPY index.html /usr/share/nginx/html/
COPY script.js /usr/share/nginx/html/
COPY styles.css /usr/share/nginx/html/

# Копируем конфигурационный файл nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Создаем файл для переменных окружения
RUN echo "window.env = {};" > /usr/share/nginx/html/env.js

# Добавляем скрипт для установки переменных окружения
COPY env.sh /docker-entrypoint.d/
RUN chmod +x /docker-entrypoint.d/env.sh

# Открываем порт 80
EXPOSE 80

# Запускаем nginx
CMD ["nginx", "-g", "daemon off;"]