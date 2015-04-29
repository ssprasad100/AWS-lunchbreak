==========
Ingredient
==========

List
====

.. http:get:: /v1/business/ingredient/(datetime:since)/

    List the ingredients.

    Authentication: :doc:`/authentication/employee`

    Serializer: :doc:`/serializers/business/singleIngredient`

    :query datetime since: Optional datetime to return the ingredients that have been modified since that datetime.


List Default
============

.. http:get:: /v1/business/ingredient/default/

    **Pagination disabled.**

    List the default ingredients.

    Authentication: :doc:`/authentication/employee`

    Serializer: :doc:`/serializers/business/singleIngredient`
