====
Food
====

Specific food
=============

.. http:get:: /v1/customers/food/(int:id)

    Food with the given ID.

    Serializer: :doc:`/serializers/global/food`

    :reqheader X-Identifier: Identifier token of the UserToken
    :reqheader X-User: ID of the user
    :reqheader X-Device: Name of the device

    :query int id: ID of the food

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: user authentication failed


Specific store
==============

.. http:get:: /v1/customers/food/store/(int:store_id)

    Food with the given store ID.

    Serializer: :doc:`/serializers/global/food`

    :reqheader X-Identifier: Identifier token of the UserToken
    :reqheader X-User: ID of the user
    :reqheader X-Device: Name of the device

    :query int store_id: ID of the store

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: user authentication failed
