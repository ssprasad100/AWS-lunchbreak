=====
Order
=====

List
====

.. http:get:: /v1/business/order/

    List all of the orders with the status: placed, received, started and waiting.

    Authentication: :doc:`/authentication/employee`

    Serializer: :doc:`/serializers/business/shortOrder`

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 403: authentication failed


Update status
=============

.. http:get:: /v1/business/order/(int:order_id)/

    Update the status of an order.

    Authentication: :doc:`/authentication/employee`

    Serializer: :doc:`/serializers/business/staff`

    :resheader Content-Type: application/json

    :query int order_id: :doc:`/serializers/business/order` ID

    :statuscode 200: no error
    :statuscode 403: authentication failed
