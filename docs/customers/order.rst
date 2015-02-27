====
Order
====

Specific order
=============

.. http:get:: /v1/customers/order/(int:id)

    Order with the given ID.

    :query int id: ID of the order

    :>jsonarr int id: order ID
    :>jsonarr string pickupTime: time of pickup in the format 'YYYY-DD-MMTHH:MM:SSZ'
    :>jsonarr boolean paid: paid or not
    :>jsonarr list food: ordered food

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
    :>jsonarr list ingredients: ingredient IDs
    :>jsonarr int store: store ID
    :>jsonarr dict category:
        - **id** (*int*) - category ID
        - **name** (*string*) - category name
        - **priority** (*int*) - priority
        - **store** (*int*) - store ID
    :>jsonarr dict foodType:
        - **name** (*string*) - foodType name
        - **icon** (*int*) - icon ID
        - **quantifier** (*string*) - quantifier
        - **inputType** (*int*) - inputType ID
    :>jsonarr int amount: amount ordered

    :>header X-Identifier: Identifier token of the UserToken
    :>header X-User: ID of the user
    :>header X-Device: Name of the device

    :<header Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: user authentication failed


User's orders
=============

.. http:get:: /v1/customers/order/

    All of the authenticated user's orders.

    :>jsonarr int id: order ID
    :>jsonarr string pickupTime: time of pickup in the format 'YYYY-DD-MMTHH:MM:SSZ'
    :>jsonarr boolean paid: paid or not
    :>jsonarr list food: ordered food

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
    :>jsonarr list ingredients: ingredient IDs
    :>jsonarr int store: store ID
    :>jsonarr dict category:
        - **id** (*int*) - category ID
        - **name** (*string*) - category name
        - **priority** (*int*) - priority
        - **store** (*int*) - store ID
    :>jsonarr dict foodType:
        - **name** (*string*) - foodType name
        - **icon** (*int*) - icon ID
        - **quantifier** (*string*) - quantifier
        - **inputType** (*int*) - inputType ID
    :>jsonarr int amount: amount ordered

    :>header X-Identifier: Identifier token of the UserToken
    :>header X-User: ID of the user
    :>header X-Device: Name of the device

    :<header Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: user authentication failed


Place order
===========

.. http:post:: /v1/customers/order/

    All of the authenticated user's orders.

    :<json list food: ordered food

        - (*dict*) option 1
            - **name** (*string*) - name (temporary)
            - **ingredients** (*list*) - ingredient IDs
            - **amount** (*int*) - amount (default 1)
        - (*dict*) option 2
            - **name** (*string*) - name (temporary)
            - **referenceId** (*int*) - referenceId
            - **amount** (*int*) - amount (default 1)
    :<json int storeId: store ID
    :<json string pickupTime: time of pickup in the format 'YYYY-DD-MMTHH:MM:SSZ'

    :>json int id: order ID
    :>json boolean paid: paid or not

    :>header X-Identifier: Identifier token of the UserToken
    :>header X-User: ID of the user
    :>header X-Device: Name of the device

    :<header Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: user authentication failed


Request price
=============

.. http:post:: /v1/customers/order/price/

    Request the price of an order.

    :<jsonarr list: ordered food

        - (*dict*)
            - **name** (*string*) - name (temporary)
            - **ingredients** (*list*) - ingredient IDs

    :>json int: price

    :>header X-Identifier: Identifier token of the UserToken
    :>header X-User: ID of the user
    :>header X-Device: Name of the device

    :<header Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: user authentication failed

