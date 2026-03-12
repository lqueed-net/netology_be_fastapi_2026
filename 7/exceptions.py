from fastapi import HTTPException, status

class ItemServiceError(HTTPException):
    """Базовое исключение для ошибок сервиса товаров."""
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class ItemNotFoundError(ItemServiceError):
    """Товар с указанным идентификатором не найден."""
    def __init__(self, item_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )

class DuplicateItemError(ItemServiceError):
    """Попытка создать товар с уже существующим уникальным полем."""
    def __init__(self, detail: str = "Item with this name already exists"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )

class DatabaseError(ItemServiceError):
    """Ошибка при работе с базой данных."""
    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )