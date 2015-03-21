============
FoodCategory
============

List
====

.. http:get:: /v1/business/foodcategory/

    **Pagination disabled.**

    List the food categories.

    Authentication: :doc:`/authentication/employee`

    Serializer: :doc:`/serializers/global/defaultFoodCategory`

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 403: authentication failed
