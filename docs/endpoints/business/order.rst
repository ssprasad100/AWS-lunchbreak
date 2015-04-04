=====
Order
=====

List
====

.. http:get:: /v1/business/order/(String:option)/(String:since)

    List all of the orders with the status: placed, received, started and waiting.

    Authentication: :doc:`/authentication/employee`

    Serializer: :doc:`/serializers/business/shortOrder`

    :resheader Content-Type: application/json

    :query String option: Optional choice between 'orderedTime' or 'pickupTime'. Order by 'orderedTime' descending (default if empty) or 'pickupTime' ascending.
    :query String since: Optional datetime from where the 'option' parameter should be returned. Format '%d-%m-%Y-%H-%M'. Can be used if option is not given too.

    :statuscode 200: no error
    :statuscode 403: authentication failed


Specific
========

.. http:get:: /v1/business/order/(int:id)/

    Update the status of an order.

    Authentication: :doc:`/authentication/employee`

    Serializer: :doc:`/serializers/business/order`

    :resheader Content-Type: application/json

    :query int id: :doc:`/serializers/business/order` ID

    :statuscode 200: no error
    :statuscode 403: authentication failed


Update status
=============

.. http:patch:: /v1/business/order/(int:id)/

    Update the status of an order.

    Authentication: :doc:`/authentication/employee`

    Serializer: :doc:`/serializers/business/order`

    :resheader Content-Type: application/json

    :query int id: :doc:`/serializers/business/order` ID

    :statuscode 200: no error
    :statuscode 403: authentication failed
