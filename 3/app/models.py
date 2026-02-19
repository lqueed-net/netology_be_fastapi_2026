from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Student(BaseModel):
    id: int
    name: str
    email: str
    age: int
    courses: List[str]

class CreateStudentRequest(BaseModel):
    name: str
    email: str
    age: int

class Course(BaseModel):
    id: int
    name: str
    credits: int


###
import enum
from datetime import date, datetime
from pydantic import ConfigDict, field_validator, model_validator, Field

class Gender(str, enum.Enum):
    MALE = 'male'
    FEMALE = 'female'
    OTHER = 'other'

class StudentStatus(enum.Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    GRADUATED = 'graduated'
    EXPELLED = 'expelled'

# Модель для создания
class CreateStudentRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "first_name": "Ivan"
            }
        }
    )

    first_name: str = Field(
        min_length=2,
        max_length=50,
        description='Имя студента',
        examples=['Ivan']
    )

    last_name: str = Field(
        min_length=2,
        max_length=50,
        description='Фамилия студента',
        examples=['Ivanov']
    )

    email: str = Field(
        pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        description='Электронная почта студента',
        examples=["student@example.com"]
    )

    age: int = Field(
        ge=16,
        le=30,
        description='Возраст студента',
        examples=[20]
    )

    gender: Gender = Field(
        description='Пол студента'
    )

    course_ids: Optional[List[int]] = Field(
        default = [],
        description='ID курсов, на которых учится студент',
        examples=[1, 2, 3]
    )

    birth_date: date = Field(
        description='Дата рождения студента',
    )

    gpa: Optional[float] = Field(
        default = None,
        ge=0.0,
        le=5.0,
        description='Средний балл успеваемости студента',
        examples=[4.5]
    )

    phone: Optional[str] = Field(
        default=None,
        min_length=5,
        max_length=20,
        description='Номер телефона студента',
        examples=["+1234567890"]
    )

    # валидация email
    @field_validator('email')
    @classmethod
    def validate_email_domain(cls, v: str) -> str:
        if 'spam' in v.lower():
            raise ValueError('Emain содержит запрещенную подстроку')
        return v.lower()

    # валидация даты рождения
    @field_validator('birth_date')
    @classmethod
    def validate_birth_date(cls, v: date) -> date:
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))

        if age < 16:
            raise ValueError('Студент должен быть старше 16')
        if age > 30:
            raise ValueError('Студент должен быть младше 30')

        return v

    # валидация номера телефона
    # через regex
    @field_validator('phone')
    @classmethod
    def validate_phone_format(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v

        if not isinstance(v, str):
            raise ValueError('Номер телефона должен быть строкой')

        return v

    # комплексная валидация
    @model_validator(mode='after')
    def validate_age_birth_rate(self) -> 'CreateStudentRequest':
        if self.birth_date:
            today = date.today()
            calculated_age = today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )

            if calculated_age != self.age:
                raise ValueError('Возраст не соотвествует дате рождения')

        return self


# модель ответа
class StudentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="уникальный идентификатор студента")
    first_name: str
    last_name: str
    email: str
    age: int
    gender: Gender
    status: StudentStatus = Field(default=StudentStatus.ACTIVE)
    birth_date: date
    created_at: datetime
    gpa: Optional[float] = None
    phone: Optional[float] = None
    updated_at: Optional[datetime] = None
    course_ids: List[int] = Field(default_factory=list, description="список идентификаторов курсов, на которых учится студент")


# Модель ответа для получения списка студентов
class StudentListResponse(BaseModel):
    students: List[StudentResponse]
    total: int
    limit: int
    filters: dict = Field(default_factory=dict)


# модель query параметров запроса студентов
class StudentFilterParams(BaseModel):
    model_config = ConfigDict(extra='ignore')

    min_age: Optional[int] = Field(
        default=None,
        ge=16,
        le=30,
        description="Минимальный возраст студента"
    )
    max_age: Optional[int] = Field(
        default=None,
        ge=16,
        le=30,
        description="Максимальный возраст студента"
    )
    gender: Optional[Gender] = None
    status: Optional[StudentStatus] = None

    @model_validator(mode='after')
    def validate_age_range(self) -> 'StudentFilterParams':
        if self.min_age and self.max_age and self.min_age > self.max_age:
            raise ValueError("min_age cannot be greater than max_age")
        return self