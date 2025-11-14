// Текущий выбранный режим
let currentMode = 'fast';

// DOM элементы
const modeButtons = document.querySelectorAll('.mode-btn');
const searchForm = document.getElementById('search-form');
const queryInput = document.getElementById('query-input');
const loadingElement = document.getElementById('loading');
const resultsContainer = document.getElementById('results-container');
const responseContent = document.getElementById('response-content');
const sourcesSection = document.getElementById('sources-section');
const sourcesList = document.getElementById('sources-list');
const factCheckSection = document.getElementById('fact-check-section');
const factCheckNotes = document.getElementById('fact-check-notes');
const modeIndicator = document.getElementById('mode-indicator');
const currentModeSpan = document.getElementById('current-mode');

// Получить URL API из переменных окружения или использовать значение по умолчанию
const API_URL = window.env ? window.env.API_URL : 'http://localhost:8000';

// Обработчики событий для кнопок режимов
modeButtons.forEach(button => {
    button.addEventListener('click', () => {
        // Удалить активный класс у всех кнопок
        modeButtons.forEach(btn => btn.classList.remove('active'));
        
        // Добавить активный класс к выбранной кнопке
        button.classList.add('active');
        
        // Обновить текущий режим
        currentMode = button.dataset.mode;
        
        // Обновить текст индикатора режима
        updateModeIndicator();
    });
});

// Обработчик отправки формы
searchForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const query = queryInput.value.trim();
    if (!query) return;
    
    // Показать загрузку
    showLoading();
    
    try {
        // Выполнить поиск в зависимости от режима
        const result = await performSearch(query, currentMode);
        
        // Отобразить результаты
        displayResults(result);
    } catch (error) {
        console.error('Ошибка поиска:', error);
        displayError(error.message || 'Произошла ошибка при выполнении поиска');
    } finally {
        // Скрыть загрузку
        hideLoading();
    }
});

// Функция для выполнения поиска
async function performSearch(query, mode) {
    // Определить endpoint в зависимости от режима
    let endpoint;
    switch (mode) {
        case 'fast':
            endpoint = '/search/fast';
            break;
        case 'deep':
            endpoint = '/search/deep';
            break;
        case 'social':
            endpoint = '/search/social';
            break;
        case 'academic':
            endpoint = '/search/academic';
            break;
        case 'finance':
            endpoint = '/search/finance';
            break;
        case 'auto':
            endpoint = '/search/auto';
            break;
        default:
            endpoint = '/search/fast';
    }
    
    // Выполнить запрос
    const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query })
    });
    
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
}

// Функция для отображения результатов
function displayResults(result) {
    // Показать контейнер результатов
    resultsContainer.style.display = 'block';
    
    // Отобразить ответ
    responseContent.innerHTML = formatResponse(result.response);
    
    // Отобразить источники, если есть
    if (result.sources && result.sources.length > 0) {
        sourcesList.innerHTML = '';
        result.sources.forEach(source => {
            const li = document.createElement('li');
            const link = document.createElement('a');
            link.href = source.url;
            link.target = '_blank';
            link.textContent = source.title || source.url;
            li.appendChild(link);
            sourcesList.appendChild(li);
        });
        sourcesSection.style.display = 'block';
    } else {
        sourcesSection.style.display = 'none';
    }
    
    // Отобразить заметки проверки фактов, если есть
    if (result.fact_check_notes) {
        factCheckNotes.innerHTML = formatResponse(result.fact_check_notes);
        factCheckSection.style.display = 'block';
    } else if (result.analysis_type) {
        // Для специализированных режимов показываем тип анализа
        factCheckNotes.innerHTML = `<p>Тип анализа: ${result.analysis_type}</p>`;
        factCheckSection.style.display = 'block';
    } else {
        factCheckSection.style.display = 'none';
    }
    
    // Если в результате указан выбранный режим (для авто-маршрутизации), показываем его
    if (result.mode_selected) {
        const modeNames = {
            'fast': 'Быстрый поиск',
            'deep': 'Глубокий анализ',
            'social': 'Социальный анализ',
            'academic': 'Академический поиск',
            'finance': 'Финансовый анализ'
        };
        
        const selectedModeName = modeNames[result.mode_selected] || result.mode_selected;
        factCheckNotes.innerHTML = `<p>Автоматически выбран режим: ${selectedModeName}</p>`;
        factCheckSection.style.display = 'block';
    }
}

// Функция для форматирования ответа
function formatResponse(response) {
    if (typeof response === 'string') {
        // Преобразовать markdown в HTML
        return response
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // Жирный текст
            .replace(/\*(.*?)\*/g, '<em>$1</em>')              // Курсив
            .replace(/^- (.*?)(?=\n|$)/gm, '<li>$1</li>')      // Список
            .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')         // Обернуть список
            .replace(/\n\n/g, '</p><p>')                       // Абзацы
            .replace(/\n/g, '<br>');                           // Переносы строк
    }
    return JSON.stringify(response, null, 2);
}

// Функция для отображения ошибки
function displayError(message) {
    resultsContainer.style.display = 'block';
    responseContent.innerHTML = `<p class="error">Ошибка: ${message}</p>`;
    sourcesSection.style.display = 'none';
    factCheckSection.style.display = 'none';
}

// Функция для показа загрузки
function showLoading() {
    loadingElement.style.display = 'block';
    resultsContainer.style.display = 'none';
}

// Функция для скрытия загрузки
function hideLoading() {
    loadingElement.style.display = 'none';
}

// Функция для обновления индикатора режима
function updateModeIndicator() {
    // Обновить текст
    const modeNames = {
        'fast': 'Быстрый поиск',
        'deep': 'Глубокий анализ',
        'social': 'Социальный анализ',
        'academic': 'Академический поиск',
        'finance': 'Финансовый анализ',
        'auto': 'Авто-маршрутизация'
    };
    
    currentModeSpan.textContent = modeNames[currentMode] || 'Быстрый поиск';
    
    // Обновить класс для цветовой индикации
    modeIndicator.className = 'mode-indicator';
    if (currentMode !== 'fast') {
        modeIndicator.classList.add(currentMode);
    }
}

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    updateModeIndicator();
});