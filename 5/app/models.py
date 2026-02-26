from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from app.database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    age = Column(Integer)
    courses = Column(ARRAY(String), nullable=False, default=[])  # массив названий курсов

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    credits = Column(Integer)