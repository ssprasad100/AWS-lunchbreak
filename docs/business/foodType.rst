========
FoodType
========

List
====

.. http:get:: /v1/business/foodtype/

    List the FoodTypes.

    Authentication: :doc:`/authentication/employee`

    Serializer: :doc:`/serializers/global/foodType`

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 403: authentication failed
