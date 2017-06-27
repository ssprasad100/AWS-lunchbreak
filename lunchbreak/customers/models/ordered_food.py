import math
from decimal import Decimal

from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _
from lunch.config import COST_GROUP_ADDITIONS, COST_GROUP_BOTH, INPUT_SI_SET
from lunch.models import Food
from lunch.utils import uggettext_summation
from Lunchbreak.fields import (CostField, MoneyField, RoundingDecimalField,
                               StatusSignalField)
from Lunchbreak.mixins import CleanModelMixin
from Lunchbreak.models import StatusSignalModel
from safedelete import HARD_DELETE

from ..config import (ORDEREDFOOD_STATUS_OK, ORDEREDFOOD_STATUS_OUT_OF_STOCK,
                      ORDEREDFOOD_STATUSES)
from ..exceptions import CostCheckFailed, MinDaysExceeded
from ..managers import OrderedFoodManager


class OrderedFood(CleanModelMixin, StatusSignalModel):

    class Meta:
        verbose_name = _('besteld etenswaar')
        verbose_name_plural = _('bestelde etenswaren')

    def __str__(self):
        return str(self.original)

    objects = OrderedFoodManager()

    ingredients = models.ManyToManyField(
        'lunch.Ingredient',
        blank=True,
        verbose_name=_('ingrediënten'),
        help_text=_('Ingrediënten.')
    )
    amount = RoundingDecimalField(
        decimal_places=3,
        max_digits=7,
        default=1,
        verbose_name=_('hoeveelheid'),
        help_text=_('Hoeveelheid.')
    )
    cost = CostField(
        verbose_name=_('kostprijs'),
        help_text=_('Kostprijs.')
    )
    content_type = models.ForeignKey(
        'contenttypes.ContentType',
        on_delete=models.CASCADE,
        limit_choices_to=(
            models.Q(app_label='customers', model='order') |
            models.Q(app_label='customers', model='temporaryorder')
        )
    )
    object_id = models.PositiveIntegerField()
    order = GenericForeignKey(
        'content_type',
        'object_id',
    )
    original = models.ForeignKey(
        'lunch.Food',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('origineel etenswaar'),
        help_text=_('Origineel etenswaar.')
    )
    is_original = models.BooleanField(
        default=False,
        verbose_name=_('identiek aan origineel'),
        help_text=_(
            'Bestelde etenswaren zijn identiek aan het origineel als er geen '
            'ingrediënten toegevoegd of afgetrokken werden.'
        )
    )
    comment = models.TextField(
        blank=True,
        verbose_name=_('commentaar'),
        help_text=_('Commentaar.')
    )
    status = StatusSignalField(
        choices=ORDEREDFOOD_STATUSES,
        default=ORDEREDFOOD_STATUS_OK,
        verbose_name=_('status'),
        help_text=_('Status.')
    )
    total = MoneyField(
        default=0,
        verbose_name=_('totale prijs'),
        help_text=_('Totale prijs exclusief korting.')
    )

    @cached_property
    def ingredientgroups(self):
        return self.original.ingredientgroups

    @cached_property
    def food_amount(self):
        """Original amount of food used for calculating the total.

        See ``OrderedFood.clean_total`` for a usage example.

        Returns:
            1 if the input type is for a set amount of weight. Otherwise 1 is returned.
            int
        """
        return self.original.amount if self.original.foodtype.inputtype == INPUT_SI_SET else 1

    @cached_property
    def changes(self):
        return self.calculate_changes(
            orderedfood=self
        )

    @cached_property
    def discounted_total(self):
        if self.order is not None:
            return int(self.total * Decimal(100 - self.order.discount) / Decimal(100))

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def update_hard_delete(self):
        """Check whether Food and Ingredients scheduled for deletion can be deleted."""
        try:
            if self.original.deleted:
                inactive_food = not OrderedFood.objects.active_with(
                    food=self.original
                ).exists()
                if inactive_food:
                    self.original.delete(force_policy=HARD_DELETE)
        except Food.DoesNotExist:
            raise

        self.ingredients.filter(
            deleted__isnull=False
        ).delete()

    def clean_total(self):
        """Calculate the total cost of the ordered food.

        If there no longer is a reference to the original food, then we cannot
        update this value. If it's out of stock, then we set the total to 0.
        If a value calculation is possible in the end, then we return the most
        appropriate value.
        """
        if self.original is None:
            return

        if self.status == ORDEREDFOOD_STATUS_OUT_OF_STOCK:
            self.total = 0
        else:
            self.total = int(
                math.ceil(
                    self.cost * self.amount * self.food_amount
                )
            )

    def clean_order(self):
        from .order import Order

        if self.original is not None \
                and isinstance(self.order, Order) \
                and not self.original.is_orderable(
                    self.order.receipt,
                    now=self.order.placed
                ):
            raise MinDaysExceeded()

    def clean_amount(self):
        if self.original is not None:
            self.original.is_valid_amount(self.amount)

    def clean_comment(self):
        if self.original is not None \
                and not self.original.commentable and self.comment:
            self.comment = ''

    def status_changed(self):
        # Update the order total
        self.order.save()

    @staticmethod
    def post_save(sender, instance, using, **kwargs):
        instance.order.save()

    @staticmethod
    def calculate_changes(orderedfood, original_relations=None,
                          ordered_ingredients=None):
        if orderedfood.is_original or not orderedfood.original.has_ingredients:
            return _('Niet aangepast.')

        added_ingredients = set()
        removed_ingredients = set()
        if original_relations is None:
            original_relations = orderedfood.original.ingredientrelations.select_related(
                'ingredient',
                'food',
            ).all()
        if ordered_ingredients is None:
            ordered_ingredients = orderedfood.ingredients.all()

        original_ingredients = [
            relation.ingredient for relation in original_relations if relation.selected]

        for ingredient in ordered_ingredients:
            if ingredient not in original_ingredients:
                added_ingredients.add(ingredient)

        for ingredient in original_ingredients:
            if ingredient not in ordered_ingredients:
                removed_ingredients.add(ingredient)

        added_size = len(added_ingredients)
        removed_size = len(removed_ingredients)

        def to_representation(ingredient):
            return ingredient.name

        added = uggettext_summation(added_ingredients, to_representation).lower()
        removed = uggettext_summation(removed_ingredients, to_representation).lower()

        if added_size > 0:
            if removed_size > 0:
                return _('Met %(added)s, zonder %(removed)s.') % {
                    'added': added,
                    'removed': removed
                }
            else:
                return _('Met %(added)s.') % {
                    'added': added
                }
        elif removed_size > 0:
            return _('Zonder %(removed)s.') % {
                'removed': removed
            }
        return _('Niet aangepast.')

    @staticmethod
    def calculate_cost(ingredients, food):
        """Calculate the base cost of the given ingredients and food.

        The base cost of the OrderedFood means that that is the cost for
        an OrderedFood with amount == 1.

        Args:
            ingredients (list): List of ingredient ids
            food (Food): Food to base the calculation off of, most of the time
            the original/closest food.

        Returns:
            Decimal: Base cost of edited food.
        """

        food_selected_ingredients, food_deselected_ingredients = food.all_ingredients
        food_selected_groups = {ingredient.group for ingredient in food_selected_ingredients}

        added_ingredients = {
            ingredient for ingredient in ingredients
            if ingredient not in food_selected_ingredients
        }
        removed_ingredients = {
            ingredient for ingredient in food_selected_ingredients
            if ingredient not in ingredients
        }

        selected_groups = {
            ingredient.group for ingredient in ingredients
        }
        added_groups = {
            ingredient.group for ingredient in added_ingredients
            if ingredient.group not in food_selected_groups
        }
        removed_groups = {
            group for group in food_selected_groups
            if group not in selected_groups
        }

        cost = food.cost

        for group in added_groups:
            cost += group.cost
        for group in removed_groups:
            cost -= group.cost

        for ingredient in added_ingredients:
            if ingredient.group.calculation in [COST_GROUP_BOTH, COST_GROUP_ADDITIONS]:
                cost += ingredient.cost
        for ingredient in removed_ingredients:
            if ingredient.group.calculation == COST_GROUP_BOTH:
                cost -= ingredient.cost

        return cost

    @staticmethod
    def check_total(base_cost, food, amount, given_total):
        """Check if the given cost is correct based on a base cost, food and amount.

        Args:
            base_cost (Decimal): Base cost of edited food.
            food (Food): Original/closest food.
            amount (Decimal): Amount of food.
            given_total (Decimal): Cost given by user.

        Raises:
            CostCheckFailed: Cost given by user was calculated incorrectly.
        """
        exponent = Decimal('1.' + ('0' * 2))
        calculated_cost = (
            base_cost * amount * (
                # See OrderedFood.food_amount
                food.amount
                if food.foodtype.inputtype == INPUT_SI_SET
                else 1
            )
        ).quantize(exponent)
        if calculated_cost != given_total:
            raise CostCheckFailed(
                '{calculated_cost} != {given_total}'.format(
                    calculated_cost=calculated_cost,
                    given_total=given_total
                )
            )
