Примеры запросов к API Items                                                       
                                                                                     
  1. Создание нового элемента (POST /items/)                                         
                                                                                     
  Создает новый товар в системе.                                                   

  Запрос:
  curl -X POST "http://localhost:8000/items/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ноутбук",
    "description": "Мощный игровой ноутбук",
    "price": 150000.0
  }'

  Ответ (200 OK):
  {
    "id": 1,
    "name": "Ноутбук",
    "description": "Мощный игровой ноутбук",
    "price": 150000.0
  }

  2. Получение всех элементов (GET /items/)

  Возвращает список всех товаров.

  Запрос:
  curl -X GET "http://localhost:8000/items/"

  Ответ (200 OK):
  [
    {
      "id": 1,
      "name": "Ноутбук",
      "description": "Мощный игровой ноутбук",
      "price": 150000.0
    },
    {
      "id": 2,
      "name": "Смартфон",
      "description": "Современный смартфон",
      "price": 80000.0
    }
  ]

  3. Получение конкретного элемента по ID (GET /items/{item_id})

  Возвращает информацию о конкретном товаре по его ID.

  Запрос:
  curl -X GET "http://localhost:8000/items/1"

  Ответ (200 OK):
  {
    "id": 1,
    "name": "Ноутбук",
    "description": "Мощный игровой ноутбук",
    "price": 150000.0
  }

  Ошибка (404 Not Found):
  Если элемент с указанным ID не существует:
  {
    "detail": "Item not found"
  }

  4. Обновление элемента (PUT /items/{item_id})

  Обновляет информацию о существующем товаре.

  Запрос:
  curl -X PUT "http://localhost:8000/items/1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ноутбук игровой",
    "description": "Очень мощный игровой ноутбук",
    "price": 160000.0
  }'

  Ответ (200 OK):
  {
    "id": 1,
    "name": "Ноутбук игровой",
    "description": "Очень мощный игровой ноутбук",
    "price": 160000.0
  }

  Частичное обновление:
  Можно обновить только некоторые поля:
  curl -X PUT "http://localhost:8000/items/1" \
  -H "Content-Type: application/json" \
  -d '{
    "price": 140000.0
  }'

  Ошибка (404 Not Found):
  Если элемент с указанным ID не существует:
  {
    "detail": "Item not found"
  }

  5. Удаление элемента (DELETE /items/{item_id})

  Удаляет товар из системы.

  Запрос:
  curl -X DELETE "http://localhost:8000/items/1"

  Ответ (200 OK):
  null

  Ошибка (404 Not Found):
  Если элемент с указанным ID не существует:
  {
    "detail": "Item not found"
  }