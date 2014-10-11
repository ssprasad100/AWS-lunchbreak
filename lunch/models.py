from django.db import models


class LocationManager(models.Manager):

    def nearby(self, latitude, longitude, proximity):
        # Haversine formule is het beste om te gebruiken bij korte afstanden.
        # d = 2 * r * asin( sqrt( sin^2( ( lat2-lat1 ) / 2 ) + cos(lat1)*cos(lat2)*sin^2( (lon2-lon1) / 2 ) ) )
        haversine = '''
        (
            (2*6371)
            * ASIN(
                SQRT(
                    POW(
                        SIN( (RADIANS(%s) - RADIANS(latitude)) / 2 )
                    , 2)
                    + (
                        COS(RADIANS(latitude))
                        * COS(RADIANS(%s))
                        * POW(
                            SIN(
                                (RADIANS(%s) - RADIANS(longitude)) / 2
                            )
                        , 2
                        )
                    )
                )
            )
        )
        '''
        haversine_where = "{} < %s".format(haversine)
        return self.get_queryset()\
            .exclude(latitude=None)\
            .exclude(longitude=None)\
            .extra(
                select={'distance': haversine},
                select_params=[latitude, latitude, longitude],
                where=[haversine_where],
                params=[latitude, latitude, longitude, proximity],
                order_by=['distance']
            )


class StoreCategory(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = 'Store Categories'

    def __unicode__(self):
        return self.name


class Store(models.Model):
    name = models.CharField(max_length=256)

    country = models.CharField(max_length=256)
    province = models.CharField(max_length=256)
    city = models.CharField(max_length=256)
    code = models.CharField(max_length=20, verbose_name="Postal code")
    street = models.CharField(max_length=256)
    number = models.IntegerField()

    objects = LocationManager()
    latitude = models.DecimalField(blank=True, decimal_places=7, max_digits=10)
    longitude = models.DecimalField(blank=True, decimal_places=7, max_digits=10)

    categories = models.ManyToManyField(StoreCategory)

    def __unicode__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=256)

    def __unicode__(self):
        return self.name


class IngredientGroupName(models.Model):
    name = models.CharField(max_length=256)

    def __unicode__(self):
        return self.name


class IngredientGroup(models.Model):
    name = models.ForeignKey(IngredientGroupName)
    maximum = models.IntegerField(default=0)

    ingredients = models.ManyToManyField(Ingredient)

    def __unicode__(self):
        return self.name


class Food(models.Model):
    name = models.CharField(max_length=256)
    cost = models.DecimalField(decimal_places=2, max_digits=5)

    store = models.ForeignKey(Store)

    ingredientGroups = models.ManyToManyField(IngredientGroup)

    def __unicode__(self):
        return self.name
