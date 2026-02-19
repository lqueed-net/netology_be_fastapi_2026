from fastapi import Header, HTTPException, Depends
from typing import Optional

SECRET_KEY = 'student-secret'

# проверка ключа
def verify_api_key(
        api_key: Optional[str] = Header(None, alias='X-API-Key')
):
    if not api_key or api_key != SECRET_KEY:
        raise HTTPException(
            status_code=403,
            detail='Invalid API key'
        )
    return api_key


# Получение текущего пользователя
def get_current_user(api_key: str = Depends(verify_api_key)):
    # DB request
    return {'username': 'student_user', 'role': 'student'}