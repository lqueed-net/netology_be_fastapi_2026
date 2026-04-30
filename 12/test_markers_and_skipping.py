import pytest
import sys

# Демонстрация маркеров, пропусков и ожидаемых ошибок

def divide(a: float, b: float) -> float:
    """Делит a на b"""
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b

def is_even(number: int) -> bool:
    """Проверяет, является ли число четным"""
    return number % 2 == 0

def slow_calculation(n: int) -> int:
    """Имитация медленного вычисления"""
    result = 0
    for i in range(n * 1000000):
        result += i
    return result

# Простые тесты с маркерами
@pytest.mark.math
def test_divide_positive_numbers():
    """Тест деления положительных чисел"""
    assert divide(10, 2) == 5.0

@pytest.mark.math
def test_divide_by_zero():
    """Тест деления на ноль"""
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

@pytest.mark.logic
def test_is_even():
    """Тест проверки четности"""
    assert is_even(4) is True
    assert is_even(3) is False

# Пропуск тестов
@pytest.mark.skip(reason="Этот функционал еще не реализован")
def test_unimplemented_feature():
    """Тест нереализованного функционала"""
    raise NotImplementedError("Not implemented yet")

@pytest.mark.skipif(sys.version_info < (3, 8), reason="Требуется Python 3.8 или выше")
def test_python_version_specific():
    """Тест, который работает только на Python 3.8+"""
    # Walrus operator (:=) доступен с Python 3.8
    numbers = [1, 2, 3, 4, 5]
    assert (n := len(numbers)) == 5

# Условный пропуск на основе внешних факторов
DATABASE_AVAILABLE = False  # Имитация недоступности базы данных

@pytest.mark.skipif(not DATABASE_AVAILABLE, reason="База данных недоступна")
def test_database_connection():
    """Тест подключения к базе данных"""
    assert DATABASE_AVAILABLE is True

# Ожидаемые ошибки (xfail)
@pytest.mark.xfail(reason="Известная ошибка в алгоритме", raises=ZeroDivisionError)
def test_known_bug():
    """Тест с известной ошибкой"""
    # Этот тест ожидаемо провалится из-за бага
    result = 10 / 0  # Это вызовет ZeroDivisionError
    assert result == 0

@pytest.mark.xfail(sys.platform == "win32", reason="Не работает на Windows")
def test_unix_specific_feature():
    """Тест, который работает только на Unix-системах"""
    import os
    assert os.name == "posix"

# Медленные тесты
@pytest.mark.slow
def test_slow_calculation_small():
    """Медленный тест"""
    result = slow_calculation(1)
    assert result >= 0

# Параметризованные тесты с маркерами
@pytest.mark.parametrize("number,expected", [
    (2, True),
    (3, False),
    (4, True),
    pytest.param(0, True, marks=pytest.mark.xfail(reason="Ноль считается четным, но есть баг")),
    pytest.param(-2, True, marks=pytest.mark.math),
])
def test_is_even_parametrized(number, expected):
    """Параметризованный тест четности с маркерами"""
    assert is_even(number) == expected

# Кастомные маркеры
@pytest.mark.integration
def test_integration_scenario():
    """Тест интеграционного сценария"""
    # Имитация интеграционного теста
    data = {"value": 42}
    processed = {"value": data["value"] * 2}
    assert processed["value"] == 84

# Группировка тестов в классе с маркерами
@pytest.mark.unit
class TestMathOperations:
    """Группа юнит-тестов для математических операций"""

    def test_addition(self):
        """Тест сложения"""
        assert 2 + 2 == 4

    def test_subtraction(self):
        """Тест вычитания"""
        assert 5 - 3 == 2

    @pytest.mark.skip(reason="Умножение пока не протестировано")
    def test_multiplication(self):
        """Тест умножения"""
        assert 3 * 4 == 12