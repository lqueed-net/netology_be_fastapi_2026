# Сервис аутентификации на FastAPI

### 1. Роли пользователей (RBAC)
- Пользователи могут иметь роль "user" или "admin"
- При регистрации роль указывается в теле запроса (по умолчанию "user")
- Администраторы имеют доступ к расширенным эндпоинтам

### 2. Обновление профиля пользователя
- Пользователи могут изменять свой email и пароль
- Система проверяет уникальность нового email
- Пароль хешируется при обновлении

### 3. Административные функции
- Администраторы могут просматривать список всех пользователей
- Защита эндпоинтов с помощью зависимости get_current_admin

## Функциональные возможности

### 1. Регистрация нового пользователя
Принимает email, пароль и роль.
Проверяет уникальность email в базе данных.
Хеширует пароль с помощью bcrypt (автоматическая генерация соли).
Сохраняет пользователя в таблицу users.
Возвращает публичные данные: id, email и роль.

### 2. Вход в систему (получение токена)
Принимает email и пароль через форму (OAuth2-совместимый формат).
Ищет пользователя по email, проверяет пароль с использованием хранимого хеша.
При успехе генерирует JWT-токен с payload: {"sub": email, "exp": время_истечения}.
Возвращает токен и его тип (bearer).

### 3. Получение информации о текущем пользователе
Требует валидный JWT-токен в заголовке Authorization: Bearer <token>.
Декодирует токен, извлекает email, находит пользователя в БД.
Возвращает публичные данные пользователя (id, email, роль).

## Примеры использования API

### 1. Регистрация нового пользователя
Эндпоинт: POST /users/register
Тело запроса: JSON с полями email, password и role

# Регистрация обычного пользователя
curl -X POST "http://localhost:8000/users/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secret123", "role": "user"}'

# Регистрация администратора
curl -X POST "http://localhost:8000/users/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123", "role": "admin"}'

### 2. Вход в систему (получение JWT токена)
Эндпоинт: POST /users/login
Тело запроса: form-data (поля username и password).
Обратите внимание: в форме поле называется username, но мы используем его как email.

curl -X POST "http://localhost:8000/users/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=secret123"

### 3. Получение информации о текущем пользователе (профиль)
Эндпоинт: GET /users/me
Заголовок: Authorization: Bearer <token>

curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer <your_token_here>"

### 4. Обновление профиля пользователя
Эндпоинт: PUT /users/me
Заголовок: Authorization: Bearer <token>
Тело запроса: JSON с полями email и/или password

curl -X PUT "http://localhost:8000/users/me" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token_here>" \
  -d '{"email": "newemail@example.com", "password": "newpassword123"}'

### 5. Получение списка всех пользователей (только для администраторов)
Эндпоинт: GET /users/
Заголовок: Authorization: Bearer <admin_token>

curl -X GET "http://localhost:8000/users/" \
  -H "Authorization: Bearer <admin_token_here>"

### Ошибка: невалидный токен (подделан или истёк)

curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer invalid.token.here"