from datetime import datetime, time, timedelta

import mock
from Lunchbreak.tests.testcase import LunchbreakTestCase

from ..models import Food, FoodType, Menu, Store


class FoodTestCase(LunchbreakTestCase):

    @mock.patch('googlemaps.Client.timezone')
    @mock.patch('googlemaps.Client.geocode')
    def test_orderable(self, mock_geocode, mock_timezone):
        self.mock_timezone_result(mock_timezone)
        self.mock_geocode_results(mock_geocode)
        preorder_time = time(hour=12)

        store = Store.objects.create(
            name='valid',
            country='Belgie',
            province='Oost-Vlaanderen',
            city='Wetteren',
            postcode='9230',
            street='Dendermondesteenweg',
            number=10,
            wait=timedelta()
        )

        foodtype = FoodType.objects.create(
            name='Test foodtype',
            store=store
        )

        menu = Menu.objects.create(
            name='Test menu',
            store=store
        )

        food = Food.objects.create(
            name='Test food',
            cost=1,
            foodtype=foodtype,
            menu=menu,
            preorder_days=None,
            preorder_time=preorder_time
        )

        def do_tests(now, pickup, preorder_disabled):
            for i in range(2):
                # Ordering without preorder_days should always return true
                now -= timedelta(hours=1)
                self.assertTrue(food.is_orderable(pickup, now=now))

                now += timedelta(hours=2)
                self.assertTrue(food.is_orderable(pickup, now=now))

                # Ordering before the preorder_time should add 1 preorder_day in the background
                # and should therefore return false if wanting to pick up the next day.

                # with preorder_days == 0, same day order is possible
                food.preorder_days = 0
                food.save()
                now -= timedelta(hours=2)
                self.assertTrue(food.is_orderable(pickup, now=now))

                now += timedelta(hours=2)
                self.assertEqual(
                    food.is_orderable(pickup, now=now),
                    preorder_disabled
                )

                # with preorder_days == 1, same day order is impossible
                food.preorder_days = 1
                food.save()
                now -= timedelta(hours=2)
                self.assertEqual(
                    food.is_orderable(pickup, now=now),
                    preorder_disabled
                )

                now += timedelta(hours=2)
                self.assertEqual(
                    food.is_orderable(pickup, now=now),
                    preorder_disabled
                )

                # with preorder_days == 1:
                #   * ordering before preorder_time should allow for next day ordering.
                #   * ordering after preorder_time should not allow for next day ordering.
                pickup += timedelta(days=1)
                now -= timedelta(hours=2)
                self.assertTrue(food.is_orderable(pickup, now=now))

                now += timedelta(hours=2)
                self.assertEqual(
                    food.is_orderable(pickup, now=now),
                    preorder_disabled
                )

                # If it's ordered for within 2 days, before/after preorder_time doesn't matter
                pickup += timedelta(days=1)
                now -= timedelta(hours=2)
                self.assertTrue(food.is_orderable(pickup, now=now))

                now += timedelta(hours=2)
                self.assertTrue(food.is_orderable(pickup, now=now))

                # with preorder_days == 2:
                #   * ordering before preorder_time should allow for 2 day ordering.
                #   * ordering after preorder_time should not allow for 2 day ordering.
                food.preorder_days = 2
                food.save()
                now -= timedelta(hours=2)
                self.assertTrue(food.is_orderable(pickup, now=now))

                now += timedelta(hours=2)
                self.assertEqual(
                    food.is_orderable(pickup, now=now),
                    preorder_disabled
                )

                # If it's ordered for within 3 days, before/after preorder_time doesn't matter
                pickup += timedelta(days=1)
                now -= timedelta(hours=2)
                self.assertTrue(food.is_orderable(pickup, now=now))

                now += timedelta(hours=2)
                self.assertTrue(food.is_orderable(pickup, now=now))

                food.preorder_days = None
                food.save()
                now = datetime.now()
                now = now.replace(hour=12, minute=0)
                pickup = datetime.now()
                pickup = pickup.replace(hour=14, minute=0)

        for j in range(2):
            food.preorder_days = None
            food.save()

            now = datetime.now()
            now = now.replace(hour=12, minute=0)

            pickup = datetime.now()
            pickup = pickup.replace(hour=12, minute=0)

            do_tests(
                now=now,
                pickup=pickup,
                preorder_disabled=food.preorder_disabled
            )

            foodtype.preorder_days = food.preorder_days
            foodtype.preorder_time = food.preorder_time
            foodtype.save()

            food.preorder_days = None
            food.save()

        food.preorder_disabled = True
        food.save()

        do_tests(
            now=now,
            pickup=pickup,
            preorder_disabled=food.preorder_disabled
        )
