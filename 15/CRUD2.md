1. создать заказ
curl -X POST "http://localhost:8000/orders/" \
  -H "Content-Type: application/json" \
  -d '{"status": "pending"}'


2. добавить позиции 1
curl -X POST "http://localhost:8000/order-items/" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 1,
    "item_id": 1,
    "quantity": 2,
    "price_at_order": 100.50
  }'


3. добавить позиции 2
curl -X POST "http://localhost:8000/order-items/" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 1,
    "item_id": 2,
    "quantity": 1,
    "price_at_order": 200.00
  }'


4. получение списка позиций заказа
curl "http://localhost:8000/orders/1/items"


5. Каскадное удаление:
удалим
curl -X DELETE "http://localhost:8000/items/1"
проверим 
curl "http://localhost:8000/orders/1/items"