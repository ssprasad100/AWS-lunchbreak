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

    Retrieve an ingredient group of the store or update one with a PATCH request.

    Permissions: :doc:`/permissions/business/storeOwner`

    Authentication: :doc:`/authentication/employee`

    Serializer: :doc:`/serializers/business/ingredientGroup`

    :query int id: :doc:`/serializers/business/ingredientGroup` ID


List Default
============

.. http:get:: /v1/business/ingredientgroup/default/(int:foodType)/

    **Pagination disabled.**

    List the default ingredient groups.

    Authentication: :doc:`/authentication/employee`

    Serializer: :doc:`/serializers/business/ingredientGroup`

    :query foodType id: optional :doc:`/serializers/global/foodType` ID to filter on
