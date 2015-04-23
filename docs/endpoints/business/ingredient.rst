==========
Ingredient
==========

List
====

.. http:get:: /v1/business/ingredient/(String:since)

    List the ingredients.

    Authentication: :doc:`/authentication/employee`

    Serializer: :doc:`/serializers/business/singleIngredient`

    :resheader Content-Type: application/json

    :query String since: Optional datetime to return the ingredients that have been modified since that datetime. Format '%d-%m-%Y-%H-%M'.

    :statuscode 200: no error
    :statuscode 403: authentication failed


List Default
============

.. http:get:: /v1/business/ingredient/default/

    **Pagination disabled.**

    List the default ingredients.

    Authentication: :doc:`/authentication/employee`

    Serializer: :doc:`/serializers/business/singleIngredient`

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 403: authentication failed
