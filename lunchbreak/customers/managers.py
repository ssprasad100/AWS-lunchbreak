from decimal import Decimal

from django.apps import apps
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from lunch.models import Food, Ingredient, IngredientGroup

from .exceptions import OrderedFoodNotOriginal


class UserManager(BaseUserManager):

    def get_by_natural_key(self, username):
        return self.get(
            phone__phone=username
        )

    def _create_user(self, phone, name, password=None, **kwargs):
        user = self.model(
            phone__phone=phone,
            name=name,
            **kwargs
        )
        user.set_password(password)
        user.save()
        return user

    def create_user(self, phone, name, password=None, **kwargs):
        kwargs.setdefault('is_staff', False)
        kwargs.setdefault('is_superuser', False)

        return self._create_user(
            phone=phone,
            name=name,
            password=password,
            **kwargs
        )

    def create_superuser(self, phone, name, password=None, **kwargs):
        kwargs['is_staff'] = True
        kwargs['is_superuser'] = True

        return self._create_user(
            phone=phone,
            name=name,
            password=password,
            **kwargs
        )


class OrderManager(models.Manager):

    def create_with_orderedfood(self, orderedfood, **kwargs):
        self.model.is_valid(orderedfood, **kwargs)

        Order = apps.get_model('customers.Order')
        if self.model == Order:
            instance = self.create(**kwargs)
        else:
            instance, created = self.get_or_create(**kwargs)
            if not created:
                instance.orderedfood.all().delete()

        OrderedFood = apps.get_model('customers.OrderedFood')

        try:
            for f in orderedfood:
                if isinstance(f, dict):
                    OrderedFood.objects.create_for_order(
                        order=instance,
                        **f
                    )
                elif isinstance(f, OrderedFood):
                    f.order = instance
                    f.save()
        except:
            instance.delete()
            raise

        instance.save()
        return instance


class OrderedFoodManager(models.Manager):

    def create_for_order(self, original, amount, total, ingredients=None, **kwargs):
        if not isinstance(amount, Decimal):
            amount = Decimal(amount)

        if not isinstance(total, Decimal):
            total = Decimal(total)

        original.foodtype.is_valid_amount(
            amount=amount,
            quantity=original.quantity
        )

        if ingredients is not None and len(ingredients) > 0 \
                and not isinstance(ingredients[0], Ingredient):
            ingredients = Ingredient.objects.filter(
                id__in=ingredients
            )

        # It's still the original if the ingredients are the same
        is_original = ingredients is None
        if not is_original:
            selected_ingredientrelations = original.ingredientrelation_set.filter(
                selected=True
            ).select_related(
                'ingredient'
            )
            original_ingredients = {
                rel.ingredient for rel in selected_ingredientrelations
            }
            if set(ingredients) == original_ingredients:
                is_original = True

        if not is_original:
            IngredientGroup.check_ingredients(
                ingredients=ingredients,
                food=original
            )

            closest_food = Food.objects.closest(
                ingredients=ingredients,
                original=original
            )

            if closest_food != original:
                raise OrderedFoodNotOriginal()

            base_cost = self.model.calculate_cost(
                ingredients=ingredients,
                food=original
            )
            self.model.check_total(
                base_cost=base_cost,
                food=original,
                amount=amount,
                given_total=total
            )
            instance = self.create(
                amount=amount,
                original=original,
                cost=base_cost,
                is_original=False,
                **kwargs
            )
            instance.ingredients = ingredients
        else:
            self.model.check_total(
                base_cost=original.cost,
                food=original,
                amount=amount,
                given_total=total
            )
            instance = self.model(
                amount=amount,
                original=original,
                cost=original.cost,
                is_original=True,
                **kwargs
            )

        instance.save()

        return instance
