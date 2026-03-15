# FastAPI Langflow Proxy

Этот проект представляет собой FastAPI-приложение, которое служит прокси для Langflow, позволяя выполнять умножение чисел через AI-агента в Langflow.

## Функции

- **API Endpoint**: POST `/multiply` для умножения списка чисел.
- **Консольная версия**: Запуск `python main.py` для интерактивного ввода чисел в терминале.
- **Интеграция с Langflow**: Отправка запросов на Langflow для обработки выражений умножения.

## Установка

1. Клонируйте репозиторий:
   ```
   git clone https://github.com/yourusername/FastAPI.git
   cd FastAPI
   ```

2. Создайте виртуальное окружение:
   ```
   python -m venv .venv
   .venv\Scripts\activate  # На Windows
   ```

3. Установите зависимости:
   ```
   pip install -r requirements.txt
   ```

4. Настройте переменные окружения: Скопируйте `.env.example` в `.env` и заполните значения.

## Переменные окружения

Создайте файл `.env` в корне проекта со следующими переменными:

- `LANGFLOW_URL`: URL вашего Langflow сервера (по умолчанию `http://127.0.0.1:7860`).
- `LANGFLOW_FLOW_ID`: ID потока в Langflow.
- `LANGFLOW_API_KEY`: API ключ для аутентификации в Langflow.
- `LANGFLOW_INPUT_TYPE`: Тип ввода (по умолчанию `chat`).
- `LANGFLOW_OUTPUT_TYPE`: Тип вывода (по умолчанию `chat`).
- `LOVEABLE_ORIGIN`: Origin для CORS (опционально).
- `CORS_ALLOW_ALL`: Разрешить все origins для CORS (опционально, `true` или `false`).

## Запуск

### Веб-сервер
```
uvicorn main:app --reload
```
Сервер запустится на `http://127.0.0.1:8000`.

### Консольная версия
```
python main.py
```
Введите числа через пробел или 'exit' для выхода.

## Использование API

### POST /multiply
Отправьте JSON с массивом чисел.

**Пример запроса:**
```json
{
  "numbers": [2.0, 3.0, 4.0],
  "session_id": "optional-session-id"
}
```

**Пример ответа:**
```json
{
  "input": "2.0 * 3.0 * 4.0",
  "auth_used": "x-api-key",
  "result_text": "Результат вычисления (2.0 × 3.0 × 4.0) равен 24.",
  "raw": { ... }
}
```

### Другие endpoints
- `GET /`: Проверка статуса.
- `GET /health`: Проверка здоровья.

## Развертывание

Проект можно развернуть на Heroku с использованием `Procfile`.

## Лицензия

MIT License. См. файл LICENSE.
