from models import (
    Student,
    Course,
    Gender,
    StudentStatus,
)
from datetime import date, datetime

# Инициализация данных
# students_db = {
#     1: Student(id=1, name="Иван Петров", email="ivan@example.com", age=20, courses=["Математика", "Физика"]),
#     2: Student(id=2, name="Мария Сидорова", email="maria@example.com", age=21, courses=["Программирование"]),
#     3: Student(id=3, name="Алексей Иванов", email="alex@example.com", age=22, courses=["Физика", "Химия"]),
# }

students_db = {
    1: {
        "id": 1,
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "email": "email@mail.com",
        "age": 20,
        "gender": Gender.MALE,
        "status": StudentStatus.ACTIVE,
        "birth_date": date(2003, 5, 15),
        "gpa": 4.5,
        "phone": "+71231112233",
        "created_at": datetime.now(),
        "updated_at": None,
        "course_ids": [1, 2]
    },
    2: {
        "id": 2,
        "first_name": "Elena",
        "last_name": "Ivanova",
        "email": "321@mail.com",
        "age": 24,
        "gender": Gender.FEMALE,
        "status": StudentStatus.ACTIVE,
        "birth_date": date(2000, 5, 15),
        "gpa": 4.5,
        "phone": "+71231112233",
        "created_at": datetime.now(),
        "updated_at": None,
        "course_ids": [1, 2]
    },
    3: {
        "id": 3,
        "first_name": "Petr",
        "last_name": "Ivanov",
        "email": "123@mail.com",
        "age": 22,
        "gender": Gender.MALE,
        "status": StudentStatus.ACTIVE,
        "birth_date": date(2001, 5, 15),
        "gpa": 4.5,
        "phone": "+71231112233",
        "created_at": datetime.now(),
        "updated_at": None,
        "course_ids": [1, 2]
    },
}

courses_db = {
    1: Course(id=1, name="Математика", credits=5),
    2: Course(id=2, name="Физика", credits=4),
    3: Course(id=3, name="Программирование", credits=6),
}
