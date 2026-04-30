import pytest

# validator.py
def validate_email(email: str) -> bool:
    if not isinstance(email, str):
        return False
    if "@" not in email:
        return False
    local, domain = email.split("@", 1)
    return bool(local and "." in domain)


@pytest.mark.parametrize("email,expected", [
    ("user@example.com", True),
    ("name.surname@mail.ru", True),
    ("invalid", False),
    ("missing@domain", False),
    ("@nodomain.com", False),
    ("", False),
    (123, False),  # не строка
])
def test_validate_email(email, expected):
    assert validate_email(email) == expected