# test_cart.py
import pytest

class ShoppingCart:
    def __init__(self):
        self.items = []

    def add_item(self, name: str, price: float):
        if price <= 0:
            raise ValueError("Price must be positive")
        self.items.append({"name": name, "price": price})

    def total(self) -> float:
        return sum(item["price"] for item in self.items)

    def count(self) -> int:
        return len(self.items)

@pytest.fixture
def empty_cart():
    """Фикстура создаёт пустую корзину"""
    return ShoppingCart()

@pytest.fixture
def cart_with_items():
    """Фикстура создаёт корзину с товарами"""
    cart = ShoppingCart()
    cart.add_item("Book", 500)
    cart.add_item("Pen", 50)
    return cart

def test_initial_state(empty_cart):
    assert empty_cart.count() == 0
    assert empty_cart.total() == 0.0

def test_add_item(empty_cart):
    empty_cart.add_item("Coffee", 300)
    assert empty_cart.count() == 1
    assert empty_cart.total() == 300.0

def test_total_calculation(cart_with_items):
    assert cart_with_items.total() == 550.0
    assert cart_with_items.count() == 2

def test_invalid_price(empty_cart):
    with pytest.raises(ValueError, match="Price must be positive"):
        empty_cart.add_item("Free", 0)


        # python -m pytest -v test_cart.py