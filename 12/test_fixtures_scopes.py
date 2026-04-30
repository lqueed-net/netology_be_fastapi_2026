import pytest

# Демонстрация различных scope фикстур

# Фикстура с scope='function' (по умолчанию) - создается для каждой функции

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

def test_function_fixture1(function_counter, module_counter, session_counter):
    function_counter["count"] += 1
    module_counter["count"] += 1
    session_counter["count"] += 1
    assert function_counter["count"] == 1
    assert module_counter["count"] >= 1
    assert session_counter["count"] >= 1

def test_function_fixture2(function_counter, module_counter, session_counter):
    function_counter["count"] += 1
    module_counter["count"] += 1
    session_counter["count"] += 1
    assert function_counter["count"] == 1  # Сбрасывается для каждой функции
    assert module_counter["count"] >= 2
    assert session_counter["count"] >= 2

class TestClassWithFixtures:
    def test_class_fixture1(self, class_counter, module_counter, session_counter):
        class_counter["count"] += 1
        module_counter["count"] += 1
        session_counter["count"] += 1
        assert class_counter["count"] == 1
        assert module_counter["count"] >= 3
        assert session_counter["count"] >= 3

    def test_class_fixture2(self, class_counter, module_counter, session_counter):
        class_counter["count"] += 1
        module_counter["count"] += 1
        session_counter["count"] += 1
        assert class_counter["count"] == 2  # Не сбрасывается в классе
        assert module_counter["count"] >= 4
        assert session_counter["count"] >= 4
