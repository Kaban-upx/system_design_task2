# Delivery Service API  
**Вариант 6: Сервис доставки (аналог CDEK)**  
REST API для управления доставкой посылок между пользователями.  

---

## 📋 Данные

- Пользователь  
- Посылка  
- Доставка  

---

## 🚀 Запуск

### Требования
- Python 3.10+  
- pip  

### Установка
```bash
git clone <ваш-репозиторий>
cd delivery-service
pip3 install -r requirements.txt --user
```

### Запуск сервера
```bash
python3 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Документация: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📡 API Endpoints

### Аутентификация

| Метод | Endpoint                         | Описание                  |
|-------|----------------------------------|---------------------------|
| POST  | `/api/users/register`            | Регистрация пользователя  |
| POST  | `/api/users/login`               | Получение JWT токена      |

### Пользователи

| Метод | Endpoint                    | Описание                  |
|-------|-----------------------------|---------------------------|
| GET   | `/api/users/search/login`   | Поиск по логину           |
| GET   | `/api/users/search/name`    | Поиск по имени/фамилии    |

### Посылки (требуется авторизация)

| Метод | Endpoint          | Описание          |
|-------|-------------------|-------------------|
| POST  | `/api/parcels`    | Создание посылки  |
| GET   | `/api/parcels/me` | Мои посылки       |

### Доставки

| Метод | Endpoint                           | Описание                       |
|-------|------------------------------------|--------------------------------|
| POST  | `/api/deliveries`                  | Создание доставки              |
| GET   | `/api/deliveries/sender/{id}`      | Доставки отправителя           |
| GET   | `/api/deliveries/recipient/{id}`   | Доставки получателя            |

---

## 🔐 Аутентификация

### 1. Получите токен

```bash
curl -X POST "http://127.0.0.1:8000/api/users/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=ivan_ivanov&password=password123"
```

Ответ:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. Используйте токен

```bash
curl -X POST "http://127.0.0.1:8000/api/parcels" \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"description":"Коробка","weight":2.5}'
```

---

## 📝 Примеры запросов

### Регистрация пользователя

```bash
curl -X POST "http://127.0.0.1:8000/api/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "login": "ivan_ivanov",
    "password": "password123",
    "first_name": "Ivan",
    "last_name": "Ivanov"
  }'
```

### Создание посылки

```bash
curl -X POST "http://127.0.0.1:8000/api/parcels" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"description":"Коробка с книгами","weight":2.5}'
```

### Создание доставки

```bash
curl -X POST "http://127.0.0.1:8000/api/deliveries" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"parcel_id":1,"recipient_id":2}'
```

---

## 🧪 Тесты

```bash
# Запуск всех тестов
python3 -m pytest tests/ -v

# Запуск конкретного теста
python3 -m pytest tests/test_api.py::TestUserRegistration -v
```

**Покрытие:** 34 теста (успешные сценарии + обработка ошибок)

---

## 🐳 Docker

```bash
# Сборка и запуск
docker-compose up --build

# Остановка
docker-compose down
```

---



## 📁 Структура проекта

- `app/main.py`          — точка входа, маршруты API
- `app/models.py`        — модели данных
- `app/schemas.py`       — Pydantic DTO‑схемы
- `app/auth.py`          — аутентификация (JWT)
- `app/storage.py`       — in‑memory хранилище
- `tests/test_api.py`    — тесты (34 теста)
- `openapi.yaml`         — OpenAPI‑спецификация
- `requirements.txt`     — зависимости
- `Dockerfile`           — Docker‑конфигурация
- `docker-compose.yaml`  — Docker Compose
- `README.md`            — этот файл


---

## ⚠️ Коды ответов

| Код | Описание             |
|-----|----------------------|
| 200 | OK                   |
| 201 | Created              |
| 400 | Bad Request          |
| 401 | Unauthorized         |
| 403 | Forbidden            |
| 404 | Not Found            |
| 422 | Validation Error     |


