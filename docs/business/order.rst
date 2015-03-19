=====
Order
=====

List
====

.. http:get:: /v1/business/order/(String:option)

    List all of the orders with the status: placed, received, started and waiting ordered by 'orderedTime' descending or 'pickupTime' ascending.

    Authentication: :doc:`/authentication/employee`

    Serializer: :doc:`/serializers/business/shortOrder`

    :resheader Content-Type: application/json

    :query String option: Choices between 'orderedTime' or 'pickupTime'. If none is given, it's 'orderedTime'.

    :statuscode 200: no error
    :statuscode 403: authentication failed


Specific
========

.. http:get:: /v1/business/order/(int:order_id)/

    Update the status of an order.

    Authentication: :doc:`/authentication/employee`

    Serializer: :doc:`/serializers/business/order`

    :resheader Content-Type: application/json

    :query int order_id: :doc:`/serializers/business/order` ID

    :statuscode 200: no error
    :statuscode 403: authentication failed


Update status
=============

.. http:patch:: /v1/business/order/(int:order_id)/

    Update the status of an order.

    Authentication: :doc:`/authentication/employee`

    Serializer: :doc:`/serializers/business/order`

    :resheader Content-Type: application/json

    :query int order_id: :doc:`/serializers/business/order` ID

    :statuscode 200: no error
    :statuscode 403: authentication failed
