import asyncio
from datetime import datetime

async def simulate_long_task(task_id: str, duration: float = 1.0):
    # имитация долгой IO задачи
    await asyncio.sleep(duration)
    return {'task_id': task_id, 'status': 'completed', 'duration': duration}


async def log_new_student(student_data: dict, created: str):
    # фоновая задача
    await asyncio.sleep(0.5)
    try:
        print(f"Новый студент создан: {student_data['name']}, создатель: {created}")
        return True
    except Exception as e:
        print(f'Ошибка создания пользователя: {e}')
    return False


def format_student_response(student_data: dict):
    # форматирование ответа - добавление нужных полей
    return {
        **student_data,
        'formatted_at': str(datetime.now()),
        'is_active': True
    }