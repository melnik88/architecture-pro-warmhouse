# API Спецификация для платформы "Теплый дом"

## Обзор

Данная спецификация описывает REST API для веб-приложения платформы "Теплый дом" - системы управления умным домом с фокусом на регулирование температуры.

## Архитектура API

### Базовый URL
```
https://api.warmhouse.com/v1
```

### Аутентификация
API использует JWT токены для аутентификации. Токен должен передаваться в заголовке:
```
Authorization: Bearer <jwt_token>
```

## Группы эндпоинтов

### 1. Аутентификация (`/auth`)

#### POST /auth/login
Вход пользователя в систему
- **Тело запроса**: `{ "username": "string", "password": "string" }`
- **Ответ**: `{ "access_token": "string", "token_type": "bearer", "expires_in": 3600 }`

#### POST /auth/logout
Выход из системы
- **Заголовки**: Authorization Bearer token
- **Ответ**: `{ "message": "Successfully logged out" }`

#### POST /auth/refresh
Обновление токена
- **Заголовки**: Authorization Bearer token
- **Ответ**: `{ "access_token": "string", "token_type": "bearer", "expires_in": 3600 }`

### 2. Пользователи (`/users`)

#### GET /users/me
Получение профиля текущего пользователя
- **Заголовки**: Authorization Bearer token
- **Ответ**:
```json
{
  "user_id": "uuid",
  "username": "string",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /users/me
Обновление профиля пользователя
- **Заголовки**: Authorization Bearer token
- **Тело запроса**: `{ "username": "string" }`
- **Ответ**: Обновленный профиль пользователя

### 3. Дома (`/homes`)

#### GET /homes
Получение списка домов пользователя
- **Заголовки**: Authorization Bearer token
- **Ответ**:
```json
[
  {
    "home_id": "uuid",
    "home_name": "string",
    "address": "string",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

#### POST /homes
Создание нового дома
- **Заголовки**: Authorization Bearer token
- **Тело запроса**:
```json
{
  "home_name": "string",
  "address": "string"
}
```
- **Ответ**: Созданный дом

#### GET /homes/{home_id}
Получение информации о конкретном доме
- **Заголовки**: Authorization Bearer token
- **Параметры пути**: `home_id` (UUID)
- **Ответ**: Информация о доме

#### PUT /homes/{home_id}
Обновление информации о доме
- **Заголовки**: Authorization Bearer token
- **Параметры пути**: `home_id` (UUID)
- **Тело запроса**: `{ "home_name": "string", "address": "string" }`
- **Ответ**: Обновленная информация о доме

#### DELETE /homes/{home_id}
Удаление дома
- **Заголовки**: Authorization Bearer token
- **Параметры пути**: `home_id` (UUID)
- **Ответ**: `{ "message": "Home deleted successfully" }`

### 4. Устройства (`/devices`)

#### GET /homes/{home_id}/devices
Получение списка устройств в доме
- **Заголовки**: Authorization Bearer token
- **Параметры пути**: `home_id` (UUID)
- **Ответ**:
```json
[
  {
    "device_id": "uuid",
    "device_name": "string",
    "device_type": "temperature|humidity|motion",
    "status": "online|offline|error",
    "configuration": {},
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### POST /homes/{home_id}/devices
Добавление нового устройства в дом
- **Заголовки**: Authorization Bearer token
- **Параметры пути**: `home_id` (UUID)
- **Тело запроса**:
```json
{
  "device_name": "string",
  "device_type": "temperature|humidity|motion",
  "configuration": {}
}
```
- **Ответ**: Созданное устройство

#### GET /devices/{device_id}
Получение информации об устройстве
- **Заголовки**: Authorization Bearer token
- **Параметры пути**: `device_id` (UUID)
- **Ответ**: Информация об устройстве

#### PUT /devices/{device_id}
Обновление устройства
- **Заголовки**: Authorization Bearer token
- **Параметры пути**: `device_id` (UUID)
- **Тело запроса**:
```json
{
  "device_name": "string",
  "device_type": "string",
  "status": "string",
  "configuration": {}
}
```
- **Ответ**: Обновленное устройство

#### DELETE /devices/{device_id}
Удаление устройства
- **Заголовки**: Authorization Bearer token
- **Параметры пути**: `device_id` (UUID)
- **Ответ**: `{ "message": "Device deleted successfully" }`

### 5. Телеметрия (`/telemetry`)

#### GET /devices/{device_id}/telemetry
Получение телеметрических данных устройства
- **Заголовки**: Authorization Bearer token
- **Параметры пути**: `device_id` (UUID)
- **Параметры запроса**:
  - `start_date` (ISO 8601 datetime, optional)
  - `end_date` (ISO 8601 datetime, optional)
  - `limit` (integer, default: 100)
- **Ответ**:
```json
[
  {
    "telemetry_id": "uuid",
    "metric_name": "string",
    "value": 23.5,
    "unit": "°C",
    "timestamp": "2024-01-01T00:00:00Z",
    "raw_data": {}
  }
]
```

#### POST /devices/{device_id}/telemetry
Добавление телеметрических данных (для устройств)
- **Заголовки**: Authorization Bearer token
- **Параметры пути**: `device_id` (UUID)
- **Тело запроса**:
```json
{
  "metric_name": "string",
  "value": 23.5,
  "unit": "°C",
  "raw_data": {}
}
```
- **Ответ**: Созданная запись телеметрии

### 6. Сценарии (`/scenarios`)

#### GET /homes/{home_id}/scenarios
Получение списка сценариев для дома
- **Заголовки**: Authorization Bearer token
- **Параметры пути**: `home_id` (UUID)
- **Ответ**:
```json
[
  {
    "scenario_id": "uuid",
    "scenario_title": "string",
    "actions": {},
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### POST /homes/{home_id}/scenarios
Создание нового сценария
- **Заголовки**: Authorization Bearer token
- **Параметры пути**: `home_id` (UUID)
- **Тело запроса**:
```json
{
  "scenario_title": "string",
  "actions": {},
  "is_active": true
}
```
- **Ответ**: Созданный сценарий

#### GET /scenarios/{scenario_id}
Получение информации о сценарии
- **Заголовки**: Authorization Bearer token
- **Параметры пути**: `scenario_id` (UUID)
- **Ответ**: Информация о сценарии

#### PUT /scenarios/{scenario_id}
Обновление сценария
- **Заголовки**: Authorization Bearer token
- **Параметры пути**: `scenario_id` (UUID)
- **Тело запроса**:
```json
{
  "scenario_title": "string",
  "actions": {},
  "is_active": true
}
```
- **Ответ**: Обновленный сценарий

#### DELETE /scenarios/{scenario_id}
Удаление сценария
- **Заголовки**: Authorization Bearer token
- **Параметры пути**: `scenario_id` (UUID)
- **Ответ**: `{ "message": "Scenario deleted successfully" }`

#### POST /scenarios/{scenario_id}/execute
Выполнение сценария
- **Заголовки**: Authorization Bearer token
- **Параметры пути**: `scenario_id` (UUID)
- **Ответ**: `{ "message": "Scenario executed successfully", "execution_id": "uuid" }`

## Модели данных

### User
```json
{
  "user_id": "uuid",
  "username": "string",
  "created_at": "datetime"
}
```

### Home
```json
{
  "home_id": "uuid",
  "owner_id": "uuid",
  "home_name": "string",
  "address": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Device
```json
{
  "device_id": "uuid",
  "owner_id": "uuid",
  "home_id": "uuid",
  "device_name": "string",
  "device_type": "string",
  "status": "string",
  "configuration": "object",
  "created_at": "datetime"
}
```

### Telemetry
```json
{
  "telemetry_id": "uuid",
  "device_id": "uuid",
  "metric_name": "string",
  "value": "number",
  "unit": "string",
  "timestamp": "datetime",
  "raw_data": "object"
}
```

### Scenario
```json
{
  "scenario_id": "uuid",
  "owner_id": "uuid",
  "home_id": "uuid",
  "scenario_title": "string",
  "actions": "object",
  "is_active": "boolean",
  "created_at": "datetime"
}
```

## Коды ошибок

### HTTP Status Codes
- `200` - OK
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

### Формат ошибок
```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {}
  }
}
```

## Безопасность

### JWT Token Structure
```json
{
  "sub": "user_id",
  "username": "string",
  "exp": 1234567890,
  "iat": 1234567890
}
```

### Rate Limiting
- 1000 запросов в час для аутентифицированных пользователей
- 100 запросов в час для неаутентифицированных запросов

## Пагинация

Для эндпоинтов, возвращающих списки, используется пагинация:

### Параметры запроса
- `page` (integer, default: 1) - номер страницы
- `limit` (integer, default: 20, max: 100) - количество элементов на странице

### Формат ответа
```json
{
  "data": [],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5
  }
}
```

## Примеры использования

### Аутентификация и получение домов
```bash
# Вход в систему
curl -X POST https://api.warmhouse.com/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user@example.com", "password": "password"}'

# Получение списка домов
curl -X GET https://api.warmhouse.com/v1/homes \
  -H "Authorization: Bearer <token>"
```

### Создание дома и добавление устройства
```bash
# Создание дома
curl -X POST https://api.warmhouse.com/v1/homes \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"home_name": "Мой дом", "address": "ул. Примерная, 123"}'

# Добавление устройства
curl -X POST https://api.warmhouse.com/v1/homes/{home_id}/devices \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"device_name": "Датчик температуры гостиной", "device_type": "temperature"}'
