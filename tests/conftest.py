from unittest.mock import Mock

import pytest

from praktikum.bun import Bun
from praktikum.burger import Burger
from praktikum.ingredient import Ingredient
from praktikum.ingredient_types import INGREDIENT_TYPE_SAUCE


@pytest.fixture
def burger():
    return Burger()


@pytest.fixture
def make_bun():

    def _make_bun(name='black bun', price=100):
        bun = Mock(spec=Bun)
        bun.get_name.return_value = name
        bun.get_price.return_value = price
        return bun

    return _make_bun


@pytest.fixture
def make_ingredient():

    def _make_ingredient(ingredient_type=INGREDIENT_TYPE_SAUCE, name='hot sauce', price=100):
        ingredient = Mock(spec=Ingredient)
        ingredient.get_type.return_value = ingredient_type
        ingredient.get_name.return_value = name
        ingredient.get_price.return_value = price
        return ingredient

    return _make_ingredient


@pytest.fixture
def mock_bun(make_bun):
    return make_bun()


@pytest.fixture
def burger_with_ingredients(burger, make_ingredient):

    def _build(count=3):
        ingredients = [make_ingredient() for _ in range(count)]
        for ingredient in ingredients:
            burger.add_ingredient(ingredient)
        return burger, ingredients

    return _build


@pytest.fixture
def burger_with_three_ingredients(burger, make_ingredient):
    for name in ('first', 'second', 'third'):
        burger.add_ingredient(make_ingredient(name=name))
    return burger


@pytest.fixture
def make_burger(burger, make_bun, make_ingredient):

    def _build(bun_name='black bun', bun_price=100, ingredients=()):
        burger.set_buns(make_bun(name=bun_name, price=bun_price))
        for spec in ingredients:
            burger.add_ingredient(make_ingredient(**spec))
        return burger

    return _build


@pytest.fixture
def ingredient_names():
    return lambda burger_obj: [item.get_name() for item in burger_obj.ingredients]
