import asyncio
import time
from typing import List

async def simulate_long_task(task_id: int, duration: float = 1.0):
    """Имитация долгой задачи"""
    await asyncio.sleep(duration)
    return {"task_id": task_id, "status": "completed", "duration": duration}

def format_student_response(student_data: dict):
    """Форматирование ответа студента"""
    return {
        **student_data,
        "formatted_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "is_active": True
    }

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

async def log_new_student(student_data: dict, created_by: str):
    """Фоновая задача для логирования"""
    await asyncio.sleep(0.5)  # Имитация долгой операции
    print(f"Новый студент создан: {student_data['name']}, создатель: {created_by}")
    return True