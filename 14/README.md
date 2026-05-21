# сборка и запуск контейнера
docker build -t simple-api .

# проброс порта
docker run -d -p 8080:80 --name my-api simple-api 

# тестовый запрос
curl http://localhost:8080