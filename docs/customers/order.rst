=====
Order
=====

Specific order
==============

.. http:get:: /v1/customers/order/(int:id)

    Order with the given ID.

    Serializer: :doc:`/serializers/customers/order`

    :reqheader X-Identifier: Identifier token of the UserToken
    :reqheader X-User: ID of the user
    :reqheader X-Device: Name of the device

    :query int id: ID of the order

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: user authentication failed


User's orders
=============

.. http:get:: /v1/customers/order/

    All of the authenticated user's orders.

    Serializer: :doc:`/serializers/customers/shortOrder`

    :reqheader X-Identifier: Identifier token of the UserToken
    :reqheader X-User: ID of the user
    :reqheader X-Device: Name of the device

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: user authentication failed


Place order
===========

.. http:post:: /v1/customers/order/

    All of the authenticated user's orders.

    Serializer: :doc:`/serializers/customers/shortOrder`

    :reqheader X-Identifier: Identifier token of the UserToken
    :reqheader X-User: ID of the user
    :reqheader X-Device: Name of the device
    :reqheader Content-Type: application/json

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: user authentication failed


Request price
=============

.. http:post:: /v1/customers/order/price/

    Request the price of an order.

    Serializer: :doc:`/serializers/customers/orderedFoodPrice`

    :reqheader X-Identifier: Identifier token of the UserToken
    :reqheader X-User: ID of the user
    :reqheader X-Device: Name of the device
    :reqheader Content-Type: application/json

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: user authentication failed

