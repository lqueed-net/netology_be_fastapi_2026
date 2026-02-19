from fastapi import Header, HTTPException, Depends
from typing import Optional

# Простая проверка API ключа
def verify_api_key(api_key: Optional[str] = Header(None, alias="X-API-Key")):
    if not api_key or api_key != "student-secret":
        raise HTTPException(
            status_code=403, 
            detail="Invalid or missing API key"
        )
    return api_key

# Зависимость для получения текущего пользователя
def get_current_user(api_key: str = Depends(verify_api_key)):
    # Здесь мог бы быть запрос к БД
    return {"username": "student_user", "role": "student"}

# Зависимость для кэширования
cache = {}
def get_cache():
    return cache