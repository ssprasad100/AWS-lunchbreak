from . import LunchTestCase
from ..models import Food, Menu


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

        menu = Menu.objects.create(
            name='test_soft_delete',
            store=self.store
        )

        food = Food.objects.create(
            name='Food',
            cost=1,
            foodtype=self.foodtype,
            menu=menu
        )

        self.assertIsNone(menu.deleted)
        menu.delete()
        self.assertRaises(
            Menu.DoesNotExist,
            Menu.objects.all_with_deleted().get,
            pk=menu.pk
        )
        self.assertRaises(
            Food.DoesNotExist,
            Food.objects.all_with_deleted().get,
            pk=food.pk
        )
