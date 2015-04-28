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


Specific store
==============

.. http:get:: /v1/customers/food/store/(int:id)/

    Food with the given store ID.

    Authentication: :doc:`/authentication/user`

    Serializer: :doc:`/serializers/global/shortDefaultFood`

    :query int id: ID of the store
