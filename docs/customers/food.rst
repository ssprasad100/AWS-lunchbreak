====
Food
====

Specific food
=============

.. http:get:: /v1/customers/food/(int:id)/

    Food with the given ID.

    Authentication: :doc:`/authentication/user`

    Serializer: :doc:`/serializers/global/food`

    :query int id: ID of the food

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: authentication failed


Specific store
==============

.. http:get:: /v1/customers/food/store/(int:store_id)/

    Food with the given store ID.

    Authentication: :doc:`/authentication/user`

    Serializer: :doc:`/serializers/global/food`

    :query int store_id: ID of the store

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: authentication failed
