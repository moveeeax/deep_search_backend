// Получаем элементы DOM
const form = document.getElementById('searchForm');
const queryInput = document.getElementById('query');
const agentTypeSelect = document.getElementById('agentType');
const loadingDiv = document.getElementById('loading');
const resultDiv = document.getElementById('result');

// Обработчик отправки формы
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Получаем значения из формы
    const query = queryInput.value.trim();
    const agentType = agentTypeSelect.value;
    
    // Проверяем, что запрос не пустой
    if (!query) {
        alert('Пожалуйста, введите вопрос');
        return;
    }
    
    // Показываем индикатор загрузки
    loadingDiv.classList.remove('hidden');
    resultDiv.classList.add('hidden');
    resultDiv.innerHTML = '';
    
    try {
        // Получаем URL API из переменных окружения или используем значение по умолчанию
        const apiUrl = window.env ? window.env.API_URL : 'http://localhost:8080';
        
        // Отправляем запрос к API
        const response = await fetch(`${apiUrl}/agent`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                input: query,
                agent_type: agentType
            })
        });
        
        // Проверяем успешность ответа
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // Парсим JSON ответ
        const data = await response.json();
        
        // Логируем полученные данные для диагностики
        console.log('Полученные данные:', data);
        
        // Отображаем результат с указанием режима
        displayResult(data.response, data.agent_type);
    } catch (error) {
        // Обрабатываем ошибки
        console.error('Ошибка при отправке запроса:', error);
        resultDiv.innerHTML = '<p class="error">Произошла ошибка при обработке запроса. Пожалуйста, попробуйте еще раз.</p>';
        resultDiv.classList.remove('hidden');
    } finally {
        // Скрываем индикатор загрузки
        loadingDiv.classList.add('hidden');
    }
});

// Функция для отображения результата в формате Markdown
function displayResult(markdownText, agentType) {
    // Логируем текст markdown для диагностики
    console.log('Markdown текст:', markdownText);
    
    // Преобразуем markdown в HTML с помощью библиотеки marked
    const htmlContent = marked.parse(markdownText);
    
    // Определяем название режима для отображения
    let modeName = "Неизвестный";
    if (agentType === "fast") {
        modeName = "Быстрый";
    } else if (agentType === "deep") {
        modeName = "Глубокий";
    }
    
    // Отображаем результат с указанием режима
    resultDiv.innerHTML = `
        <div class="mode-indicator">Режим: ${modeName}</div>
        <div class="markdown-content">${htmlContent}</div>
    `;
    resultDiv.classList.remove('hidden');
}