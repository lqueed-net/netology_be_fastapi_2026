# 1. Установите зависимости
pip install -r requirements.txt

# 2. Запустите сервер
python app.py

# Или через uvicorn напрямую
uvicorn app:app --reload --host 0.0.0.0 --port 8000

запрос с ошибкой валидации
curl --location 'localhost:8000/v2/students?min_age=11&gender=cat' \
--header 'X-API-Key: student-secret'

пост корректный
curl --location 'localhost:8000/v2/students' \
--header 'X-API-Key: student-secret' \
--header 'Content-Type: application/json' \
--data-raw '{
    "first_name": "Иван",
    "last_name": "Иванов",
    "email": "ivanov@example.com",
    "age": 22,
    "gender": "male",
    "course_ids": [1, 2, 3],
    "birth_date": "2003-05-15",
    "gpa": 4.5,
    "phone": "+7 (999) 123-45-67"
}'

пост с ошибкой валидации
СНАЧАЛА показываем год, потом остальное
curl --location 'localhost:8000/v2/students' \
--header 'X-API-Key: student-secret' \
--header 'Content-Type: application/json' \
--data-raw '{
    "first_name": "Иван",
    "last_name": "Иванов",
    "email": "ivanov@email",
    "age": 22,
    "gender": "asd",
    "course_ids": [1, 2, 3],
    "birth_date": "2001-01-15",
    "gpa": 4.5,
    "phone": "+7 (999) 23-45-67"
}'