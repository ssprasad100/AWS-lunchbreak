=====
Order
=====

Retrieve order
==============

.. http:get:: /v1/customers/order/(int:id)/

    Order with the given ID.

    Authentication: :doc:`/authentication/user`

    Serializer: :doc:`/serializers/customers/order`

    :query int id: ID of the order


User's orders
=============

.. http:get:: /v1/customers/order/

    All of the authenticated user's orders ordered by pickupTime descending.

    Authentication: :doc:`/authentication/user`

    Serializer: :doc:`/serializers/customers/shortOrder`


Place order
===========

.. http:post:: /v1/customers/order/

    All of the authenticated user's orders.

    Authentication: :doc:`/authentication/user`

    Serializer: :doc:`/serializers/customers/shortOrder`


Request price
=============

.. http:post:: /v1/customers/order/price/

    Request the price of an order.

    Authentication: :doc:`/authentication/user`

    Request serializer: :doc:`/serializers/customers/orderedFoodPrice`

    :resjsonarr decimal cost: Calculated cost
    :resjsonarr int food: :doc:`/serializers/global/food` ID
