from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
import asyncio
import time
from datetime import datetime

import models, dependencies, utils
from db import students_db, courses_db

router = APIRouter()

# ENDPOINTS
@router.get("/status", tags=['System'])
async def health_check():
    #health check
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
    }


@router.get("/students", tags=['Students'])
async def get_students(
        current_user: dict = Depends(dependencies.get_current_user),
        min_age: int = None,
        max_age: int = None,
):
    print(f"Пользователь {current_user['username']} запросил список студентов")

    filtered_students = []

    for student in students_db.values():
        if min_age is not None and student.age < min_age:
            continue
        if max_age is not None and student.age > max_age:
            continue
        filtered_students.append(utils.format_student_response(student.dict()))

    return filtered_students


@router.get("/students/{student_id}", tags=['Students'])
async def get_student_by_id(
        student_id: int,
        current_user: dict = Depends(dependencies.get_current_user)
):
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail='Студент не найден')

    return utils.format_student_response(students_db[student_id].dict())


@router.post("/students", tags=['Students'])
async def create_student(
        name: str,
        email: str,
        age: int,
        background_tasks: BackgroundTasks,
        current_user: dict = Depends(dependencies.get_current_user)
):
    # создание студента
    new_id = max(students_db.keys()) + 1

    new_student = models.Student(
        id=new_id,
        name=name,
        email=email,
        age=age,
        courses=[]
    )

    # "SAVE"
    students_db[new_id] = new_student

    # backgroud logging
    background_tasks.add_task(
        utils.log_new_student,
        new_student.model_dump(),
        current_user['username']
    )

    return {
        'message': 'Студент успешно создан',
        'student_id': new_id,
        'student': utils.format_student_response(new_student.model_dump())
    }


