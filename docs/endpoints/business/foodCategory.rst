============
FoodCategory
============

List/Create
===========

.. http:get:: /v1/business/foodcategory/

    **Pagination disabled.**

    List the food categories or create a food category with a POST request.

    Permissions: :doc:`/permissions/business/storeOwner`

    Authentication: :doc:`/authentication/employee`

    Serializer: :doc:`/serializers/global/defaultFoodCategory`


Retrieve/Update
===============

.. http:get:: /v1/business/foodcategory/(int:id)/

    Retrieve/patch a food category by its ID.

    Permissions: :doc:`/permissions/business/storeOwner`

    Authentication: :doc:`/authentication/employee`

    Serializer: :doc:`/serializers/global/defaultFoodCategory`

    :query int id: :doc:`/serializers/global/foodCategory` ID
