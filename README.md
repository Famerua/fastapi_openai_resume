FastAPI OpenAI Resume
=====================

Веб‑сервис для генерации резюме при помощи OpenAI Responses API. Приложение принимает структурированные данные кандидата, формирует текст резюме на выбранном языке и, при необходимости, сохраняет DOCX файл.

Возможности
-----------
- Асинхронный запрос к OpenAI (`AsyncOpenAI`) через FastAPI.
- Поддержка языков `en`, `ru`, `kz` с локализованными секциями резюме.
- Генерация Markdown‑структурированного текста и краткого summary.
- Экспорт резюме в формат DOCX (каталог `files/`).
- Структурированное логирование, зависящее от флага `DEBUG`.

Технологический стек
--------------------
- Python 3.10+
- FastAPI [standard] (uvicorn, Starlette, Pydantic v2)
- OpenAI Python SDK (`AsyncOpenAI`)
- pydantic-settings
- python-docx

Подготовка окружения
--------------------
1. Убедитесь, что установлен [uv](https://docs.astral.sh/uv/).
2. Создайте и активируйте виртуальное окружение:
   ```bash
   uv init --python 3.10
   uv venv
   source .venv/bin/activate
   ```
3. Установите зависимости проекта:
   ```bash
   uv sync
   ```

Настройка переменных среды
--------------------------
Создайте файл `.env` в корне проекта либо задайте переменные среды напрямую:
```
OPENAI_API_KEY=sk-...
DEBUG=true
```
`DEBUG` управляет уровнем логирования (DEBUG/INFO).

Запуск сервиса
--------------
```bash
uv run fastapi dev app.main:app --reload
```
или в активированном виртуальном окружении
```bash
uvicorn app.main:app --reload
```
Приложение будет доступно по адресу `http://127.0.0.1:8000`. Документацию Swagger можно открыть по `http://127.0.0.1:8000/docs`.

Описание API
------------

### POST /generate_resume
Генерирует текст резюме и краткое summary.
- Query-параметры:
  - `lang`: `en` | `ru` | `kz` (по умолчанию `en`)
  - `gen_file`: логический флаг; при `true` формируется DOCX в папке files.
- Тело запроса (`ResumeRequest`):
  ```json
  {
    "full_name": "Kozhagaliyev Taubay",
    "position": "Python Software Developer",
    "skills": ["Python", "SQL", "FastAPI"],
    "experience": "3 years in backend development, banking automation projects",
    "education": "Bachelor in Computer Science",
    "languages": ["English - B2", "Kazakh - native", "Russian - fluent"]
  }
  ```
- Ответ (`ResumeResponse`):
  ```json
  {
    "resume_text": "## Summary\n...\n## Skills\n- ...",
    "summary": "Short paragraph..."
  }
  ```
- При `gen_file=true` файл DOCX сохраняется в `files/resume_agent_demo_<имя>.docx`.

### POST /export_resume
Принимает уже готовый `ResumeResponse`, создает DOCX и возвращает путь к файлу.
