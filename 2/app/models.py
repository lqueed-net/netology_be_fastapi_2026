from pydantic import BaseModel
from typing import List

class Student(BaseModel):
    id: int
    name: str
    email: str
    age: int
    courses: List[str]

class Course(BaseModel):
    id: int
    name: str
    credits: int