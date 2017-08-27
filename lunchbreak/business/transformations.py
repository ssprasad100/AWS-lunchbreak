from versioning_prime import Transformation


class PostgreSQLTransformation(Transformation):

    bases = [
        'business.serializers.OrderSpreadSerializer',
    ]
    version = '2.0.0'

    weekdays = {
        #               PostgreSQL "dow"    MySQL "weekday"
        # Monday        1                   0
        # Tuesday       2                   1
        # Wednesday     3                   2
        # Thursday      4                   3
        # Friday        5                   4
        # Saturday      6                   5
        # Sunday        0                   6
        1: 0,
        2: 1,
        3: 2,
        4: 3,
        5: 4,
        6: 5,
        0: 6,
    }

    def is_weekday(self, request):
        return request.query_params.get('unit') == 'weekday'

    def backwards_serializer(self, data, obj, request):
        if self.is_weekday(request):
            data['unit'] = self.weekdays[data['unit']]
        return data
