# Устанавливаем alembic
pip install alembic

# Инициализируем alembic в проекте
alembic init migrations


# в alembic.ini:
sqlalchemy.url = postgresql://postgres:pwd@localhost:5432/test


СНАЧАЛА - database.py


# в env.py
from app.database import Base
from app import models  # noqa
target_metadata = Base.metadata


# Создаем миграцию
alembic revision --autogenerate -m "Initial migration"

# Применяем миграцию
alembic upgrade head


# коннект к постгре
psql postgresql://postgres:pwd@localhost:5432/test
\dt - инфа о таблицах
\d users - инфа о таблице юзерс

# запросы
curl -X POST 'localhost:8000/students/?name=test&email=test@test.ru&age=21'
curl -X POST 'localhost:8000/students/?name=test2&email=test2@test.ru&age=18'

curl -X GET 'localhost:8000/students/'

curl -X POST 'localhost:8000/courses/?name=testcourse1&credits=4
curl -X POST 'localhost:8000/courses/?name=testcourse2&credits=5
curl -X POST 'localhost:8000/courses/?name=testcourse3&credits=2

curl -X PUT 'localhost:8000/students/1/add_course?student_id=1&course_name=testcourse'
