===============
IngredientGroup
===============

List
====

.. http:get:: /v1/business/ingredientgroup/

    **Pagination disabled.**

    List the IngredientGroups.

    Authentication: :doc:`/authentication/employee`

    Serializer: :doc:`/serializers/business/shortIngredientGroup`

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 403: authentication failed
