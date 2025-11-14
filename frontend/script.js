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
const API_URL = window.env ? window.env.API_URL : 'http://bootcamp2025.tarassov.me:8000';

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
        // Process tables first (most complex formatting)
        let formatted = response;
        
        // Handle Markdown tables
        const tableRegex = /(\|(?:[^\n]*\|)+\n\s*\|(?:\s*[-:]+\s*\|)+\n(?:\|(?:[^\n]*\|)+\n?)*)/g;
        formatted = formatted.replace(tableRegex, function(match) {
            // Split into lines
            const lines = match.trim().split('\n');
            
            // Process header
            const headers = lines[0].split('|').filter(cell => cell.trim() !== '').map(cell => cell.trim());
            
            // Process alignments from separator line
            const alignments = lines[1].split('|').filter(cell => cell.trim() !== '').map(cell => {
                const trimmed = cell.trim();
                if (trimmed.startsWith(':') && trimmed.endsWith(':')) return 'center';
                if (trimmed.endsWith(':')) return 'right';
                return 'left';
            });
            
            // Process data rows
            const dataRows = lines.slice(2).map(line =>
                line.split('|').filter(cell => cell.trim() !== '').map(cell => cell.trim())
            );
            
            // Generate HTML table
            let tableHtml = '<table class="markdown-table">';
            
            // Header
            tableHtml += '<thead><tr>';
            headers.forEach((header, index) => {
                const align = alignments[index] || 'left';
                tableHtml += `<th align="${align}">${header}</th>`;
            });
            tableHtml += '</tr></thead>';
            
            // Body
            tableHtml += '<tbody>';
            dataRows.forEach(row => {
                tableHtml += '<tr>';
                row.forEach((cell, index) => {
                    const align = alignments[index] || 'left';
                    // Process inline markdown in cells
                    let processedCell = cell
                        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                        .replace(/\*(.*?)\*/g, '<em>$1</em>')
                        .replace(/`(.*?)`/g, '<code>$1</code>')
                        .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>');
                    tableHtml += `<td align="${align}">${processedCell}</td>`;
                });
                tableHtml += '</tr>';
            });
            tableHtml += '</tbody></table>';
            
            return tableHtml;
        });
        
        // Process other markdown elements (existing functionality)
        formatted = formatted
            // Headers (h1-h6)
            .replace(/^###### (.*$)/gim, '<h6>$1</h6>')
            .replace(/^##### (.*$)/gim, '<h5>$1</h5>')
            .replace(/^#### (.*$)/gim, '<h4>$1</h4>')
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            // Bold text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            // Italic
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            // Monospace
            .replace(/`(.*?)`/g, '<code>$1</code>')
            // Horizontal rule
            .replace(/^\s*---\s*$/gm, '<hr>')
            // Unordered lists
            .replace(/^- (.*?)(?=\n|$)/gm, '<li>$1</li>')
            .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
            // Ordered lists
            .replace(/^\d+\. (.*?)(?=\n|$)/gm, '<li>$1</li>')
            .replace(/(<li>.*<\/li>)/gs, '<ol>$1</ol>')
            // Links
            .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>');
        
        // Split into paragraphs
        const paragraphs = formatted.split('\n\n');
        return paragraphs.map(p => {
            // If paragraph already contains HTML tags, don't wrap in <p>
            if (/<(h[1-6]|ul|ol|li|hr|strong|em|code|a|table|thead|tbody|tr|th|td)/.test(p)) {
                return p;
            }
            // Otherwise wrap in <p>
            return `<p>${p.replace(/\n/g, '<br>')}</p>`;
        }).join('');
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