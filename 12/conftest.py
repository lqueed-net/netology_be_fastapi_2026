import pytest
@pytest.fixture(scope="function")
def function_counter():
    """Счетчик вызывается для каждой тестовой функции"""
    print("\nCreating function counter")
    return {"count": 0}

# Фикстура с scope='class' - создается один раз для всего класса
@pytest.fixture(scope="class")
def class_counter():
    """Счетчик создается один раз для всего класса"""
    print("\nCreating class counter")
    return {"count": 0}

# Фикстура с scope='module' - создается один раз для модуля
@pytest.fixture(scope="module")
def module_counter():
    """Счетчик создается один раз для модуля"""
    print("\nCreating module counter")
    return {"count": 0}

# Фикстура с scope='session' - создается один раз для всей сессии тестирования
@pytest.fixture(scope="session")
def session_counter():
    """Счетчик создается один раз для всей сессии"""
    print("\nCreating session counter")
    return {"count": 0}