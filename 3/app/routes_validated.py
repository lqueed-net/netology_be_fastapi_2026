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


@router.get("/students", tags=['Students'], response_model=models.StudentListResponse)
async def get_students(
        current_user: dict = Depends(dependencies.get_current_user),
        min_age: Optional[int] = Query(None, ge=16, le=30, description='min age'),
        max_age: Optional[int] = Query(None, ge=16, le=30, description='min age'),
        gender: Optional[models.Gender] = Query(None, description='gender'),
        status: Optional[models.StudentStatus] = Query(None, description='status')
):
    # validate age
    if min_age and max_age and min_age > max_age:
        raise HTTPException(status_code=400, detail='min_age cannot be greater than max_age')

    filtered_students = []

    # FILTRATION LOGIC
    for student_id, student_data in students_db.items():
        filtered_students.append(models.StudentResponse(**student_data))

    limit = 10

    return models.StudentListResponse(
        students=filtered_students[:limit],
        total=len(filtered_students),
        limit=limit,
        filters={
            "min_age": min_age,
            "max_age": max_age,
            "gender": gender,
            "status": status
        }
    )





@router.get("/students/{student_id}", tags=['Students'])
async def get_student_by_id(
        student_id: int,
        current_user: dict = Depends(dependencies.get_current_user)
):
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail='Студент не найден')

    return utils.format_student_response(students_db[student_id].dict())


@router.post("/students", tags=['Students'], response_model=models.StudentResponse, status_code=201)
async def create_student(
        student_data: models.CreateStudentRequest,
        current_user: dict = Depends(dependencies.get_current_user)
):
    new_id = max(students_db.keys()) + 1 if students_db else 1

    new_student = {
        'id': new_id,
        **student_data.model_dump(),
        "status": models.StudentStatus.active,
        "created_at": datetime.now(),
        "updated_at": None
    }
    students_db[new_id] = new_student

    return models.StudentResponse(**new_student)

