from unittest.mock import patch

import pytest

from praktikum.burger import Burger
from praktikum.ingredient_types import INGREDIENT_TYPE_FILLING, INGREDIENT_TYPE_SAUCE


class TestBurgerInit:

    def test_init_bun_is_none(self, burger):
        assert burger.bun is None

    def test_init_ingredients_is_empty_list(self, burger):
        assert burger.ingredients == []

    def test_init_ingredients_are_not_shared_between_burgers(self, burger, make_ingredient):
        burger.add_ingredient(make_ingredient())

        assert Burger().ingredients == []


class TestBurgerSetBuns:

    def test_set_buns_saves_bun(self, burger, mock_bun):
        burger.set_buns(mock_bun)

        assert burger.bun is mock_bun

    def test_set_buns_replaces_previous_bun(self, burger, make_bun):
        old_bun = make_bun(name='black bun')
        new_bun = make_bun(name='white bun')
        burger.set_buns(old_bun)

        burger.set_buns(new_bun)

        assert burger.bun is new_bun


class TestBurgerAddIngredient:

    def test_add_ingredient_appends_in_order(self, burger, make_ingredient):
        first = make_ingredient(name='hot sauce')
        second = make_ingredient(name='cutlet')

        burger.add_ingredient(first)
        burger.add_ingredient(second)

        assert burger.ingredients == [first, second]

    def test_add_same_ingredient_twice_keeps_both(self, burger, make_ingredient):
        ingredient = make_ingredient()

        burger.add_ingredient(ingredient)
        burger.add_ingredient(ingredient)

        assert burger.ingredients == [ingredient, ingredient]


class TestBurgerRemoveIngredient:

    @pytest.mark.parametrize(
        'index, expected_names',
        [
            (0, ['second', 'third']),
            (1, ['first', 'third']),
            (2, ['first', 'second']),
            (-1, ['first', 'second']),
        ],
        ids=['first', 'middle', 'last', 'negative index'],
    )
    def test_remove_ingredient_by_index(
        self, burger_with_three_ingredients, ingredient_names, index, expected_names
    ):
        burger_with_three_ingredients.remove_ingredient(index)

        assert ingredient_names(burger_with_three_ingredients) == expected_names

    @pytest.mark.parametrize(
        'count, index',
        [
            (0, 0),
            (3, 3),
            (3, -4),
        ],
        ids=['empty burger', 'above range', 'below range'],
    )
    def test_remove_ingredient_with_wrong_index_raises_error(
        self, burger_with_ingredients, count, index
    ):
        burger, _ = burger_with_ingredients(count)

        with pytest.raises(IndexError):
            burger.remove_ingredient(index)


class TestBurgerMoveIngredient:

    @pytest.mark.parametrize(
        'index, new_index, expected_names',
        [
            (0, 2, ['second', 'third', 'first']),
            (2, 0, ['third', 'first', 'second']),
            (1, 1, ['first', 'second', 'third']),
            (-1, 0, ['third', 'first', 'second']),
            (0, 10, ['second', 'third', 'first']),
        ],
        ids=[
            'forward',
            'backward',
            'same position',
            'negative index',
            'new_index above length',
        ],
    )
    def test_move_ingredient_changes_order(
        self, burger_with_three_ingredients, ingredient_names, index, new_index, expected_names
    ):
        burger_with_three_ingredients.move_ingredient(index, new_index)

        assert ingredient_names(burger_with_three_ingredients) == expected_names

    @pytest.mark.parametrize(
        'count, index, new_index',
        [
            (0, 0, 0),
            (1, 5, 0),
            (1, -2, 0),
        ],
        ids=['empty burger', 'above range', 'below range'],
    )
    def test_move_ingredient_with_wrong_index_raises_error(
        self, burger_with_ingredients, count, index, new_index
    ):
        burger, _ = burger_with_ingredients(count)

        with pytest.raises(IndexError):
            burger.move_ingredient(index, new_index)


class TestBurgerGetPrice:

    @pytest.mark.parametrize(
        'bun_price, ingredients, expected_price',
        [
            (100, (), 200),
            (200, ({'price': 100}, {'price': 200}, {'price': 300}), 1000),
            (0, ({'price': 0},), 0),
            (0.1, ({'price': 0.2}, {'price': 0.3}), 0.7),
        ],
        ids=[
            'bun only',
            'with ingredients',
            'zero prices',
            'float prices',
        ],
    )
    def test_get_price_is_double_bun_plus_ingredients(
        self, make_burger, bun_price, ingredients, expected_price
    ):
        burger = make_burger(bun_price=bun_price, ingredients=ingredients)

        assert burger.get_price() == pytest.approx(expected_price)

    def test_get_price_without_bun_raises_error(self, burger):
        with pytest.raises(AttributeError):
            burger.get_price()


class TestBurgerGetReceipt:

    @pytest.mark.parametrize(
        'bun_name, ingredients, price, expected_receipt',
        [
            (
                'black bun',
                (),
                200,
                '(==== black bun ====)\n'
                '(==== black bun ====)\n'
                '\n'
                'Price: 200',
            ),
            (
                'white bun',
                ({'ingredient_type': INGREDIENT_TYPE_SAUCE, 'name': 'hot sauce'},),
                500,
                '(==== white bun ====)\n'
                '= sauce hot sauce =\n'
                '(==== white bun ====)\n'
                '\n'
                'Price: 500',
            ),
            (
                'red bun',
                (
                    {'ingredient_type': INGREDIENT_TYPE_FILLING, 'name': 'cutlet'},
                    {'ingredient_type': INGREDIENT_TYPE_SAUCE, 'name': 'sour cream'},
                    {'ingredient_type': INGREDIENT_TYPE_FILLING, 'name': 'dinosaur'},
                ),
                1100.5,
                '(==== red bun ====)\n'
                '= filling cutlet =\n'
                '= sauce sour cream =\n'
                '= filling dinosaur =\n'
                '(==== red bun ====)\n'
                '\n'
                'Price: 1100.5',
            ),
        ],
        ids=['bun only', 'one sauce', 'fillings and sauce'],
    )
    def test_get_receipt_format(
        self, make_burger, bun_name, ingredients, price, expected_receipt
    ):
        burger = make_burger(bun_name=bun_name, ingredients=ingredients)

        with patch.object(Burger, 'get_price', return_value=price):
            receipt = burger.get_receipt()

        assert receipt == expected_receipt

    def test_get_receipt_lowercases_ingredient_type(self, make_burger):
        burger = make_burger(
            bun_name='white bun',
            ingredients=({'ingredient_type': 'SaUcE', 'name': 'hot sauce'},),
        )

        with patch.object(Burger, 'get_price', return_value=500):
            receipt = burger.get_receipt()

        assert '= sauce hot sauce =' in receipt

    def test_get_receipt_includes_calculated_price(self, make_burger):
        burger = make_burger(
            bun_name='black bun',
            bun_price=150,
            ingredients=(
                {'ingredient_type': INGREDIENT_TYPE_SAUCE, 'price': 50},
                {'ingredient_type': INGREDIENT_TYPE_FILLING, 'price': 100},
            ),
        )

        receipt = burger.get_receipt()

        assert receipt.endswith('Price: 450')

    def test_get_receipt_without_bun_raises_error(self, burger):
        with pytest.raises(AttributeError):
            burger.get_receipt()
