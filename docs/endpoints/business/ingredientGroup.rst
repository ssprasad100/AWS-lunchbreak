===============
IngredientGroup
===============

List/Create
===========

.. http:get:: /v1/business/ingredientgroup/

    **Pagination disabled.**

    List the ingredient groups of the store or create one with a POST request.

    Permissions: :doc:`/permissions/business/storeOwner`

    Authentication: :doc:`/authentication/employee`

    Serializer: :doc:`/serializers/business/shortIngredientGroup`


Retrieve/Update
===============

.. http:get:: /v1/business/ingredientgroup/(int:id)/

    **Pagination disabled.**

    Retrieve an ingredient group of the store or update one with a PATCH request.

    Permissions: :doc:`/permissions/business/storeOwner`

    Authentication: :doc:`/authentication/employee`

    Serializer: :doc:`/serializers/business/shortIngredientGroup`

    :query int id: :doc:`/serializers/global/ingredientGroup` ID
