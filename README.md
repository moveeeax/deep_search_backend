# Research Pro Mode - Расширенный Поисковый Ассистент

Research Pro Mode — это продвинутый поисковый ассистент, который не просто ищет ответы, а понимает контекст, сравнивает источники и проверяет факты.

## Особенности

### Два основных режима:

1. **Simple Mode (Быстрый поиск)** - как у ChatGPT или Perplexity Lite
   - Минимальные накладные расходы на обработку
   - Идеально подходит для простых одноадресных запросов
   - Быстрое время отклика

2. **Research Pro Mode (Глубокий анализ)** - умный "исследователь"
   - Многошаговое рассуждение
   - Сбор данных с разных сайтов
   - Проверка достоверности
   - Финальный вывод с ссылками

### Расширенные режимы:

- **Auto-Routing** — интеллектуальный выбор режима поиска
- **Pro: Social** — анализ мнений (Reddit, X, VK, Habr)
- **Pro: Academic** — поиск в arXiv / Semantic Scholar
- **Pro: Finance** — данные из Yahoo Finance / TradingView

## Архитектура

```
┌─────────────────┐    ┌──────────────────┐
│   Frontend      │    │   Backend        │
│   (React/HTML)  │◄──►│   (Python/Flask) │
└─────────────────┘    └──────────────────┘
                              │
                              ▼
                      ┌──────────────────┐
                      │  Tavily API      │
                      │  (Поиск/Скрапинг)│
                      └──────────────────┘
                              │
                              ▼
                   ┌───────────────────────┐
                   │  OpenAI/Anthropic     │
                   │  (Обработка языка)    │
                   └───────────────────────┘
```

## Технологии

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python, Flask, LangChain, LangGraph
- **Поиск**: Tavily API
- **Обработка языка**: OpenAI GPT или Anthropic Claude
- **Контейнеризация**: Docker, Docker Compose

## Установка и запуск

### Требования

- Docker и Docker Compose
- Tavily API ключ
- OpenAI или Anthropic API ключ

### Настройка переменных окружения

Создайте файл `.env` в директории `deep_search_poc` на основе `.env.sample`:

```bash
cp deep_search_poc/.env.sample deep_search_poc/.env
```

Заполните необходимые значения:

```env
# Tavily API Key для поиска в интернете
TAVILY_API_KEY=your_tavily_api_key_here

# OpenAI API Key для обработки естественного языка
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API Key (альтернатива OpenAI)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Базовый URL для OpenAI API (по умолчанию OpenAI)
OPENAI_BASE_URL=https://api.openai.com/v1

# Модель для быстрых запросов
NANO_MODEL=gpt-3.5-turbo

# Модель для глубоких запросов
KIMIK2_MODEL=gpt-4
```

### Запуск приложения

```bash
cd deep_search_poc
docker-compose up --build
```

После запуска приложение будет доступно по адресу: http://localhost

## API Endpoints

### Быстрый поиск
```
POST /search/fast
{
  "query": "Ваш вопрос"
}
```

### Глубокий анализ
```
POST /search/deep
{
  "query": "Ваш сложный вопрос"
}
```

### Социальный анализ
```
POST /search/social
{
  "query": "Тема для анализа соцсетей"
}
```

### Академический поиск
```
POST /search/academic
{
  "query": "Научный вопрос"
}
```

### Финансовый анализ
```
POST /search/finance
{
  "query": "Финансовый вопрос"
}
```

### Авто-маршрутизация
```
POST /search/auto
{
  "query": "Ваш вопрос"
}
```

Автоматически определяет наиболее подходящий режим поиска на основе анализа запроса.

## Оценка качества

### SimpleQA Bench
Проверяет базовую точность ответов на простые одношаговые вопросы (single-hop factual QA).
- Метрика: Accuracy (%)

### FRAMES Bench
Оценивает сложные запросы, требующие многошагового рассуждения и работы с несколькими источниками (multi-hop reasoning & retrieval).
- Метрики: Factuality, Reasoning Depth, Source Diversity

## Разработка

### Структура проекта

```
deep_search_poc/
├── app.py              # Основной сервер Flask
├── docker-compose.yml  # Конфигурация Docker Compose
├── Dockerfile          # Dockerfile для бэкенда
├── requirements.txt    # Зависимости Python
├── .env                # Переменные окружения
├── backend/
│   ├── agent.py        # Реализация агентов поиска
│   ├── prompts.py      # Системные промпты
│   └── utils.py        # Вспомогательные функции
└── frontend/
    ├── index.html      # Главная страница
    ├── script.js       # Логика фронтенда
    ├── styles.css      # Стили
    ├── Dockerfile      # Dockerfile для фронтенда
    ├── nginx.conf      # Конфигурация Nginx
    └── env.sh          # Скрипт для переменных окружения
```

### Добавление новых режимов

1. Создайте новый промпт в `backend/prompts.py`
2. Добавьте новый граф в `backend/agent.py`
3. Создайте новый endpoint в `app.py`
4. Добавьте кнопку режима в `frontend/index.html`
5. Обновите стили в `frontend/styles.css`
6. Добавьте обработчик в `frontend/script.js`

## Лицензия

MIT License

## Авторы

Deep Search PoC Team 6