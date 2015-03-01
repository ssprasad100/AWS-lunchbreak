====
Order
====

Specific order
=============

.. http:get:: /v1/customers/order/(int:id)

    Order with the given ID.

    :reqheader X-Identifier: Identifier token of the UserToken
    :reqheader X-User: ID of the user
    :reqheader X-Device: Name of the device

    :query int id: ID of the order

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: user authentication failed

    :resjsonarr int id: order ID
    :resjsonarr string pickupTime: time of pickup in the format 'YYYY-DD-MMTHH:MM:SSZ'
    :resjsonarr boolean paid: paid or not
    :resjsonarr list food: ordered food

        - (*dict*)
            - **id** (*int*) - food ID
            - **name** (*string*) - name
            - **cost** (*double*) - cost
            - **ingredientGroups** (*list*) - groups of the ingredients
                - (*dict*)
                    - **id** (*int*) - ingredientGroup ID
                    - **name** (*string*) - name
                    - **maximum** (*int*) - maximum amount of ingredients selected
                    - **ingredients** (*list*) - ingredients
                        - (*dict*)
                            - **id** (*int*) - ingredient ID
                            - **name** (*string*) - name
                            - **cost** (*double*) - cost
    :resjsonarr list ingredients: ingredient IDs
    :resjsonarr int store: store ID
    :resjsonarr dict category:
        - **id** (*int*) - category ID
        - **name** (*string*) - category name
        - **priority** (*int*) - priority
        - **store** (*int*) - store ID
    :resjsonarr dict foodType:
        - **name** (*string*) - foodType name
        - **icon** (*int*) - icon ID
        - **quantifier** (*string*) - quantifier
        - **inputType** (*int*) - inputType ID
    :resjsonarr int amount: amount ordered


User's orders
=============

.. http:get:: /v1/customers/order/

    All of the authenticated user's orders.

    :reqheader X-Identifier: Identifier token of the UserToken
    :reqheader X-User: ID of the user
    :reqheader X-Device: Name of the device

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: user authentication failed

    :resjsonarr int id: order ID
    :resjsonarr string pickupTime: time of pickup in the format 'YYYY-DD-MMTHH:MM:SSZ'
    :resjsonarr boolean paid: paid or not
    :resjsonarr list food: ordered food

        - (*dict*)
            - **id** (*int*) - food ID
            - **name** (*string*) - name
            - **cost** (*double*) - cost
            - **ingredientGroups** (*list*) - groups of the ingredients
                - (*dict*)
                    - **id** (*int*) - ingredientGroup ID
                    - **name** (*string*) - name
                    - **maximum** (*int*) - maximum amount of ingredients selected
                    - **ingredients** (*list*) - ingredients
                        - (*dict*)
                            - **id** (*int*) - ingredient ID
                            - **name** (*string*) - name
                            - **cost** (*double*) - cost
    :resjsonarr list ingredients: ingredient IDs
    :resjsonarr int store: store ID
    :resjsonarr dict category:
        - **id** (*int*) - category ID
        - **name** (*string*) - category name
        - **priority** (*int*) - priority
        - **store** (*int*) - store ID
    :resjsonarr dict foodType:
        - **name** (*string*) - foodType name
        - **icon** (*int*) - icon ID
        - **quantifier** (*string*) - quantifier
        - **inputType** (*int*) - inputType ID
    :resjsonarr int amount: amount ordered


Place order
===========

.. http:post:: /v1/customers/order/

    All of the authenticated user's orders.

    :reqheader X-Identifier: Identifier token of the UserToken
    :reqheader X-User: ID of the user
    :reqheader X-Device: Name of the device
    :reqheader Content-Type: application/json

    :reqjson list food: ordered food

        - (*dict*) option 1
            - **name** (*string*) - name (temporary)
            - **ingredients** (*list*) - ingredient IDs
            - **amount** (*int*) - amount (default 1)
        - (*dict*) option 2
            - **name** (*string*) - name (temporary)
            - **referenceId** (*int*) - referenceId
            - **amount** (*int*) - amount (default 1)
    :reqjson int storeId: store ID
    :reqjson string pickupTime: time of pickup in the format 'YYYY-DD-MMTHH:MM:SSZ'

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: user authentication failed

    :resjson int id: order ID
    :resjson boolean paid: paid or not


Request price
=============

.. http:post:: /v1/customers/order/price/

    Request the price of an order.

    :reqheader X-Identifier: Identifier token of the UserToken
    :reqheader X-User: ID of the user
    :reqheader X-Device: Name of the device
    :reqheader Content-Type: application/json

    :reqjsonarr list: ordered food

        - (*dict*)
            - **name** (*string*) - name (temporary)
            - **ingredients** (*list*) - ingredient IDs

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: user authentication failed

    :resjson int: price

