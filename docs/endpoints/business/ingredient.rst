==========
Ingredient
==========

List/Create
===========

.. http:get:: /v1/business/ingredient/(datetime:since)/

    List the ingredients or create an ingredient with a POST request.

    Permissions: :doc:`/permissions/business/storeOwner`

    Authentication: :doc:`/authentication/employee`

    Serializer: :doc:`/serializers/business/ingredient`

    :query datetime since: Optional datetime to return the ingredients that have been modified since that datetime.


List Default
============

.. http:get:: /v1/business/ingredient/default/

    **Pagination disabled.**

    List the default ingredients.

    Authentication: :doc:`/authentication/employee`

    Serializer: :doc:`/serializers/business/ingredient`


Retrieve/Update/Delete
======================

.. http:get:: /v1/business/ingredient/(int:id)/

    Retrieve/update/delete an ingredient by its ID.

    Permissions: :doc:`/permissions/business/storeOwner`

    Authentication: :doc:`/authentication/employee`

    Serializer: :doc:`/serializers/business/ingredient`

    :query int id: :doc:`/serializers/business/ingredient` ID
