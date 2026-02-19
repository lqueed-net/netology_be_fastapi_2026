import models

students_db = {
    1: models.Student(
        id=1,
        name="Ivan Petrov",
        email="ivan.petrov@example.com",
        age=20,
        courses=['Math', 'Physics']
    ),
    2: models.Student(
        id=1,
        name="Egor Ivanov",
        email="egor.ivanov@example.com",
        age=20,
        courses=['Programming']
    ),
    3: models.Student(
        id=1,
        name="Elena Kuznecova",
        email="elena.kuznica@example.com",
        age=20,
        courses=['Chemistry', 'Physics']
    )
}

courses_db = {
    1: models.Course(id=1, name='Math', credits=5),
    2: models.Course(id=2, name='Physics', credits=4),
    3: models.Course(id=3, name='Chemistry', credits=3),
    4: models.Course(id=4, name='Programming', credits=2),
}