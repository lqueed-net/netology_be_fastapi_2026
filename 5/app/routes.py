from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime

from fastapi import  Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app import models, dependencies
from app.utils import get_db



router = APIRouter()


# ENDPOINTS
@router.get("/status", tags=['System'])
async def health_check():
    #health check
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
    }


### CRUD


# ---------- Студенты ----------
#create
@router.post("/students/", response_model=dict)
async def create_student(
        name: str, 
        email: str, 
        age: int, 
        db: AsyncSession = Depends(get_db), 
):
    student = models.Student(name=name, email=email, age=age, courses=[])
    db.add(student)
    await db.commit()
    await db.refresh(student)
    return {"id": student.id, "name": student.name, "email": student.email, "age": student.age, "courses": student.courses}

#read multiple
@router.get("/students/", response_model=List[dict])
async def read_students(
        skip: int = 0, 
        limit: int = 10, 
        db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(models.Student).offset(skip).limit(limit)
    )
    students = result.scalars().all()
    return [{"id": s.id, "name": s.name, "email": s.email, "age": s.age, "courses": s.courses} for s in students]

#read
@router.get("/students/{student_id}", response_model=dict)
async def read_student(
        student_id: int, 
        db: AsyncSession = Depends(get_db), 
):
    result = await db.execute(
        select(models.Student).where(models.Student.id == student_id)
    )
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"id": student.id, "name": student.name, "email": student.email, "age": student.age, "courses": student.courses}

#update
@router.put("/students/{student_id}/add_course")
async def add_course_to_student(
        student_id: int, 
        course_name: str,
        db: AsyncSession = Depends(get_db), 
):
    # Получаем студента
    result = await db.execute(
        select(models.Student).where(models.Student.id == student_id)
    )
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Проверяем, что курс существует
    result = await db.execute(
        select(models.Course).where(models.Course.name == course_name)
    )
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Обновляем массив курсов (если такого курса нет у студента)
    if course_name not in student.courses:
        student.courses = student.courses + [course_name]
        await db.commit()
        await db.refresh(student)
    
    return {"message": "Course added", "courses": student.courses}




# ---------- Курсы ----------
#create
@router.post("/courses/", response_model=dict)
async def create_course(
        name: str, 
        credits: int, 
        db: AsyncSession = Depends(get_db), 
):
    course = models.Course(name=name, credits=credits)
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return {"id": course.id, "name": course.name, "credits": course.credits}


# read
@router.get("/courses/", response_model=List[dict])
async def read_courses(
        skip: int = 0, 
        limit: int = 10,
        db: AsyncSession = Depends(get_db), 
):
    result = await db.execute(
        select(models.Course).offset(skip).limit(limit)
    )
    courses = result.scalars().all()
    return [{"id": c.id, "name": c.name, "credits": c.credits} for c in courses]
