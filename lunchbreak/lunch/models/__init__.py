from django.db.models.signals import m2m_changed, post_save

from .abstract_address import AbstractAddress  # noqa
from .base_token import BaseToken  # noqa
from .delivery_period import DeliveryPeriod  # noqa
from .food import Food  # noqa
from .food_type import FoodType  # noqa
from .holiday_period import HolidayPeriod  # noqa
from .ingredient import Ingredient  # noqa
from .ingredient_group import IngredientGroup  # noqa
from .ingredient_relation import IngredientRelation  # noqa
from .menu import Menu  # noqa
from .opening_period import OpeningPeriod  # noqa
from .period import Period  # noqa
from .quantity import Quantity  # noqa
from .region import Region  # noqa
from .store import Store  # noqa
from .store_category import StoreCategory  # noqa
from .store_header import StoreHeader  # noqa

m2m_changed.connect(
    Food.changed_ingredients,
    sender=Food.ingredientgroups.through,
    weak=False
)
post_save.connect(
    Food.changed_ingredients,
    sender=IngredientRelation,
    weak=False
)
m2m_changed.connect(
    Food.changed_ingredients,
    sender=Food.ingredients.through,
    weak=False
)
m2m_changed.connect(
    Food.check_ingredientgroups,
    sender=Food.ingredientgroups.through,
    weak=False
)
