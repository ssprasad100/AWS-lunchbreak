from decimal import Decimal

from django.db import DatabaseError, models
from django.db.models import Q
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from Lunchbreak.exceptions import LunchbreakException
from Lunchbreak.fields import CostField, RoundingDecimalField
from Lunchbreak.mixins import CleanModelMixin
from openpyxl import load_workbook
from safedelete import HARD_DELETE, SOFT_DELETE
from safedelete.models import SafeDeleteModel

from ..exceptions import (IngredientGroupMaxExceeded,
                          IngredientGroupsMinimumNotMet, LinkingError)
from ..utils import uggettext_summation


class Food(CleanModelMixin, SafeDeleteModel):

    class Meta:
        verbose_name = _('etenswaar')
        verbose_name_plural = _('etenswaren')

    def __str__(self):
        return self.name

    name = models.CharField(
        max_length=191,
        verbose_name=_('naam'),
        help_text=('Naam.')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('beschrijving'),
        help_text=('Beschrijving.')
    )
    amount = RoundingDecimalField(
        decimal_places=3,
        max_digits=7,
        default=1,
        verbose_name=_('standaardhoeveelheid'),
        help_text=('Hoeveelheid die standaard is ingevuld.')
    )
    cost = CostField(
        verbose_name=_('basisprijs'),
        help_text=(
            'Basisprijs, dit is inclusief de gekozen ingrediënten en '
            'ingrediëntengroepen.'
        )
    )
    foodtype = models.ForeignKey(
        'FoodType',
        on_delete=models.CASCADE,
        verbose_name=_('type etenswaar'),
        help_text=('Type etenswaar.')
    )
    wait = models.DurationField(
        default=None,
        null=True,
        blank=True,
        verbose_name=_('wachttijd'),
        help_text=_(
            'Minimum tijd dat op voorhand besteld moet worden. Dit leeg '
            'laten betekent dat deze instelling overgenomen wordt van het '
            'type etenswaar.'
        )
    )
    preorder_time = models.TimeField(
        default=None,
        null=True,
        blank=True,
        verbose_name=_('tijd voorafgaande bestelling'),
        help_text=_(
            'Indien bepaalde waren meer dan een dag op voorhand besteld moeten '
            'worden, moeten ze voor dit tijdstip besteld worden. Dit leeg '
            'laten betekent dat deze instelling overgenomen wordt van het '
            'type etenswaar.'
        )
    )
    preorder_days = models.IntegerField(
        default=None,
        null=True,
        blank=True,
        verbose_name=_('dagen op voorhand bestellen'),
        help_text=(
            'Minimum dagen op voorhand bestellen voor het uur ingesteld op '
            'de winkel. (0 is dezelfde dag, >=1 is dat aantal dagen voor het '
            'bepaalde uur.) Dit leeg laten betekent dat deze instelling '
            'overgenomen wordt van het type etenswaar.'
        )
    )
    preorder_disabled = models.BooleanField(
        default=False,
        verbose_name=_('voorhand bestelling uitschakelen'),
        help_text=(
            'Of de mogelijkheid om op voorhand te bestellen specifiek voor '
            'dit etenswaar is uitgeschakeld.'
        )
    )
    commentable = models.BooleanField(
        default=False,
        verbose_name=_('commentaar mogelijk'),
        help_text=(
            'Of er commentaar kan achter worden gelaten bij het bestellen.'
        )
    )
    priority = models.BigIntegerField(
        default=0,
        verbose_name=_('prioriteit'),
        help_text=('Prioriteit.')
    )

    menu = models.ForeignKey(
        'Menu',
        on_delete=models.CASCADE,
        related_name='food',
        verbose_name=_('menu'),
        help_text=('Menu.')
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='IngredientRelation',
        blank=True,
        verbose_name=_('ingrediënten'),
        help_text=('Ingrediënten.')
    )
    ingredientgroups = models.ManyToManyField(
        'IngredientGroup',
        blank=True,
        verbose_name=_('ingrediëntengroep'),
        help_text=('Ingrediëntengroep.')
    )

    enabled = models.BooleanField(
        default=True,
        verbose_name=_('ingeschakeld'),
        help_text=_('Ingeschakeld.')
    )
    last_modified = models.DateTimeField(
        auto_now=True,
        verbose_name=_('laatst aangepast'),
        help_text=('Laatst aangepast.')
    )

    @cached_property
    def _safedelete_policy(self):
        """Food can be deleted if no active OrderedFood use them.

        Returns:
            SOFT_DELETE if still used, HARD_DELETE otherwise.
        """
        from customers.models import OrderedFood

        active_order = OrderedFood.objects.active_with(
            food=self
        ).exists()
        if active_order:
            return SOFT_DELETE
        return HARD_DELETE

    @cached_property
    def store(self):
        return self.menu.store

    @cached_property
    def ingredients_count(self):
        try:
            self._prefetched_objects_cache[self.ingredients.prefetch_cache_name]
            # Ingredients is prefetched
            return len(self.ingredients.all())
        except (AttributeError, KeyError):
            # Not prefetched
            return self.ingredients.count()

    @cached_property
    def ingredientgroups_count(self):
        try:
            self._prefetched_objects_cache[self.ingredientgroups.prefetch_cache_name]
            # Ingredientgroups is prefetched
            return len(self.ingredientgroups.all())
        except (AttributeError, KeyError):
            # Not prefetched
            return self.ingredientgroups.count()

    @cached_property
    def has_ingredients(self):
        return self.ingredients_count > 0 or self.ingredientgroups_count > 0

    @cached_property
    def selected_ingredients(self):
        return self.ingredients.filter(
            selected=True
        )

    @cached_property
    def nonempty_ingredientgroups(self):
        return self.ingredientgroups.filter(
            # Do not include empty groups
            ingredients__isnull=False
        ).prefetch_related(
            'ingredients'
        ).distinct()

    @cached_property
    def all_ingredients(self):
        relations = self.ingredientrelations.select_related(
            'ingredient'
        ).all()

        deselected_ingredients = []
        selected_ingredients = []

        for relation in relations:
            if relation.selected:
                selected_ingredients.append(relation.ingredient)
            else:
                deselected_ingredients.append(relation.ingredient)

        for ingredientgroup in self.nonempty_ingredientgroups:
            group_ingredients = ingredientgroup.ingredients.all()
            for ingredient in group_ingredients:
                if ingredient not in selected_ingredients \
                        and ingredient not in deselected_ingredients:
                    deselected_ingredients.append(ingredient)

        return selected_ingredients, deselected_ingredients

    @cached_property
    def all_ingredientgroups(self):
        ingredientgroups = self.ingredientgroups.filter(
            # Do not include empty groups
            ingredients__isnull=False
        ).prefetch_related(
            'ingredients'
        ).distinct()

        ingredients = self.ingredients.all().select_related(
            'group'
        )

        ingredientgroups_added = []
        for ingredient in ingredients:
            if ingredient.group not in ingredientgroups \
                    and ingredient.group not in ingredientgroups_added:
                ingredientgroups_added.append(
                    ingredient.group
                )

        all_ingredientgroups = []
        all_ingredientgroups.extend(ingredientgroups)
        all_ingredientgroups.extend(ingredientgroups_added)

        return all_ingredientgroups

    @cached_property
    def quantity(self):
        from .quantity import Quantity

        try:
            return Quantity.objects.get(
                foodtype_id=self.foodtype_id,
                store_id=self.store.id
            )
        except Quantity.DoesNotExist:
            return None

    @cached_property
    def inherited_wait(self):
        return self.wait \
            if self.wait is not None \
            else self.foodtype.inherited_wait

    @property
    def preorder_settings(self):
        """Returns the preorder settings and include the inherited FoodType's settings."""

        if self.preorder_disabled:
            return None, None

        preorder_days = self.preorder_days \
            if self.preorder_days is not None \
            else self.foodtype.preorder_days
        preorder_time = self.preorder_time \
            if self.preorder_time is not None \
            else self.foodtype.preorder_time

        return preorder_days, preorder_time

    def get_cost_display(self):
        return str(
            (
                Decimal(self.cost) / Decimal(100)
            ).quantize(
                Decimal('0.01')
            )
        ).replace('.', ',')

    def get_ingredients_display(self):

        def to_representation(ingredient):
            return ingredient.name

        return uggettext_summation(
            self.ingredients.all(),
            to_representation
        ).capitalize() + '.'

    def update_typical(self):
        ingredientgroups = self.ingredientgroups.all()
        ingredientrelations = self.ingredientrelations.select_related(
            'ingredient__group'
        ).all()

        for ingredientrelation in ingredientrelations:
            ingredient = ingredientrelation.ingredient
            # Musn't the ingredient be selected before it can be typical?
            if ingredient.group not in ingredientgroups:
                if not ingredientrelation.typical:
                    ingredientrelation.typical = True
                    ingredientrelation.save()
            elif ingredientrelation.typical:
                ingredientrelation.typical = False
                ingredientrelation.save()

    def is_orderable(self, dt, now=None):
        """
        Check whether this food can be ordered for the given day.
        This does not check whether the Store.wait has been exceeded!
        """
        preorder_days, preorder_time = self.preorder_settings

        if preorder_days is None or preorder_time is None:
            return True

        now = timezone.now() if now is None else now
        # Amount of days needed to order in advance
        # (add 1 if it isn't before the preorder_time)
        preorder_days = preorder_days + (
            1 if now.time() > preorder_time else 0
        )

        # Calculate the amount of days between dt and now
        difference_day = (dt - now).days
        difference_day += (
            1
            if dt.time() < now.time() and
            (now + (dt - now)).day != now.day
            else 0
        )
        return difference_day >= preorder_days

    def is_valid_amount(self, amount, raise_exception=True):
        return self.foodtype.is_valid_amount(
            amount=amount,
            quantity=self.quantity,
            raise_exception=raise_exception
        )

    def clean_amount(self):
        self.foodtype.is_valid_amount(self.amount)

    def save(self, *args, **kwargs):
        self.full_clean()

        super(Food, self).save(*args, **kwargs)

        if self.deleted:
            self.delete()

    def check_ingredients(self, ingredients):
        """
        Check whether the given ingredients can be made into an OrderedFood.
        """

        ingredientgroups = {}
        for ingredient in ingredients:
            group = ingredient.group
            amount = 1
            if group.id in ingredientgroups:
                amount += ingredientgroups[group.id]
            if group.maximum > 0 and amount > group.maximum:
                raise IngredientGroupMaxExceeded()
            ingredientgroups[group.id] = amount

        from .ingredient import Ingredient

        allowed_ingredients = Ingredient.objects.filter(
            Q(food__pk=self.pk) | Q(group__food__pk=self.pk)
        ).distinct()

        valid_ingredients = all(
            ingredient in allowed_ingredients for ingredient in ingredients
        )
        if not valid_ingredients:
            raise LinkingError(
                _('Ingrediënten zijn niet toegelaten voor het gegeven etenswaar.')
            )

        original_ingredients = self.ingredients.all()

        for ingredient in original_ingredients:
            group = ingredient.group
            if group.minimum > 0:
                if group.id not in ingredientgroups:
                    raise IngredientGroupsMinimumNotMet()
                amount = ingredientgroups[group.id]

                if amount < group.minimum:
                    raise IngredientGroupsMinimumNotMet()

    @staticmethod
    def changed_ingredients(sender, instance, action=None, **kwargs):
        from .ingredient_group import IngredientGroup
        from .ingredient import Ingredient
        from .ingredient_relation import IngredientRelation

        if action is None or len(action) > 4 and action[:4] == 'post':
            if isinstance(instance, Food):
                instance.update_typical()
            elif instance.__class__ in [Ingredient, IngredientGroup]:
                for food in instance.food_set.all():
                    food.update_typical()
            elif isinstance(instance, IngredientRelation):
                instance.food.update_typical()

    @classmethod
    def check_ingredientgroups(cls, action, instance, pk_set, **kwargs):
        if len(action) > 4 and action[:4] == 'post':
            groups = instance.ingredientgroups.filter(
                ~Q(store_id=instance.menu.store_id)
            )
            if groups.exists():
                raise LinkingError(
                    'The food and its ingredientgroups need to belong to the same store.'
                )

    @classmethod
    def from_excel(cls, store, file):
        workbook = load_workbook(
            filename=file,
            read_only=True
        )

        if 'Food' not in workbook:
            raise LunchbreakException(
                _('The worksheet "Food" could not be found. Please use our template.')
            )

        from .food_type import FoodType
        from .menu import Menu

        worksheet = workbook['Food']
        mapping = [
            {
                'field_name': 'name',
            },
            {
                'field_name': 'description',
            },
            {
                'field_name': 'menu',
                'instance': {
                    'model': Menu,
                    'create': True,
                    'field_name': 'name'
                }
            },
            {
                'field_name': 'cost',
            },
            {
                'field_name': 'foodtype',
                'instance': {
                    'model': FoodType,
                    'field_name': 'name',
                    'store': False
                }
            },
            {
                'field_name': 'preorder_days',
            },
            {
                'field_name': 'priority',
            },
        ]
        mapping_length = len(mapping)

        food_list = []
        created_relations = []
        skip = True
        for row in worksheet.rows:
            # Skip headers
            if skip:
                skip = False
                continue

            kwargs = {}
            exclude = []

            for cell in row:
                if not isinstance(cell.column, int):
                    continue

                i = cell.column - 1
                if i >= mapping_length:
                    continue
                info = mapping[i]
                value = cell.value
                if 'instance' in info:
                    instance = info['instance']
                    create = instance.get('create', False)
                    model = instance['model']

                    exclude.append(info['field_name'])
                    where = {
                        instance['field_name']: cell.value
                    }
                    if instance.get('store', True):
                        where['store'] = store

                    if create:
                        value, created = model.objects.get_or_create(
                            **where
                        )
                        if created:
                            created_relations.append(value)
                    else:
                        value = model.objects.get(
                            **where
                        )

                kwargs[info['field_name']] = value

            food = Food(
                **kwargs
            )
            try:
                food.clean_fields(exclude=exclude)
            except LunchbreakException:
                for relation in created_relations:
                    relation.delete()
                raise LunchbreakException(
                    _('Could not import row %(row)d.') % {
                        'row': cell.row
                    }
                )

            food_list.append(food)

        try:
            cls.objects.bulk_create(food_list)
        except DatabaseError:
            for relation in created_relations:
                relation.delete()
