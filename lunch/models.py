from django.db import models


class LocationManager(models.Manager):

    def nearby(self, latitude, longitude, proximity):
        # Haversine formule is het beste om te gebruiken bij korte afstanden.
        # d = 2asin( sqrt( sin^2( ( lat2-lat1 ) / 2 ) +
        # cos(lat1)*cos(lat2)*sin^2( (lon2-lon1) / 2 ) ) )
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


class Category(models.Model):
    name = models.CharField(max_length=50)


class Store(models.Model):
    name = models.CharField(max_length=256)

    country = models.CharField(max_length=256)
    province = models.CharField(max_length=256)
    city = models.CharField(max_length=256)
    code = models.CharField(max_length=20, verbose_name="Postal code")
    street = models.CharField(max_length=256)
    number = models.IntegerField()

    objects = LocationManager()
    latitude = models.FloatField()
    longitude = models.FloatField()

    categories = models.ManyToManyField(Category)

    def __unicode__(self):
        return self.name
