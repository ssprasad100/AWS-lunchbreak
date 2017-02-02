from datetime import datetime, time, timedelta

from . import LunchTestCase
from ..models import Food, FoodType, Menu, Store


class MenuTestCase(LunchTestCase):

    def test_soft_delete(self):
        menu = Menu.objects.create(
            name='test_soft_delete',
            store=self.store
        )

        menu.delete()
        self.assertRaises(
            Menu.DoesNotExist,
            menu.refresh_from_db
        )
        print(menu.deleted)
        print(Menu.objects.count())
        print(Menu.objects.all_with_deleted().count())

        menu = Menu.objects.create(
            name='test_soft_delete',
            store=self.store
        )

        food = Food.objects.create(
            name='Food',
            cost=1,
            foodtype=self.foodtype,
            menu=menu,
            store=self.store
        )

        self.assertIsNone(menu.deleted)
        print(menu.deleted)
        print(Menu.objects.count())
        print(Menu.objects.all_with_deleted().count())
        menu.delete()
        print(menu.deleted)
        print(Menu.objects.count())
        print(Menu.objects.all_with_deleted().count())
        menu.refresh_from_db()
        self.assertIsNotNone(menu.deleted)
        food.delete()
        self.assertRaises(
            Food.DoesNotExist,
            food.refresh_from_db
        )
        self.assertRaises(
            Menu.DoesNotExist,
            menu.refresh_from_db
        )
