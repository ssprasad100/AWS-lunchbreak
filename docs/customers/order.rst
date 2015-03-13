=====
Order
=====

Specific order
==============

.. http:get:: /v1/customers/order/(int:id)/

    Order with the given ID.

    Authentication: :doc:`/authentication/user`

    Serializer: :doc:`/serializers/customers/order`

    :query int id: ID of the order

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: authentication failed


User's orders
=============

.. http:get:: /v1/customers/order/

    All of the authenticated user's orders.

    Authentication: :doc:`/authentication/user`

    Serializer: :doc:`/serializers/customers/shortOrder`

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: authentication failed


Place order
===========

.. http:post:: /v1/customers/order/

    All of the authenticated user's orders.

    Authentication: :doc:`/authentication/user`

    Serializer: :doc:`/serializers/customers/shortOrder`
    :reqheader Content-Type: application/json

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: authentication failed


Request price
=============

.. http:post:: /v1/customers/order/price/

    Request the price of an order.

    Authentication: :doc:`/authentication/user`

    Serializer: :doc:`/serializers/customers/orderedFoodPrice`
    :reqheader Content-Type: application/json

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: authentication failed

