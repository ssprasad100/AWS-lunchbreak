====
Food
====

Specific food
=============

.. http:get:: /v1/customers/food/(int:id)

    Food with the given ID.

    :reqheader X-Identifier: Identifier token of the UserToken
    :reqheader X-User: ID of the user
    :reqheader X-Device: Name of the device

    :query int id: ID of the food

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: user authentication failed

    :resjsonarr int id: food ID
    :resjsonarr string name: food name
    :resjsonarr double cost: cost per item
    :resjsonarr list ingredientGroups: groups of the ingredients

        - (*dict*)
            - **id** (*int*) - ingredientGroup ID
            - **name** (*string*) - name
            - **maximum** (*int*) - maximum amount of ingredients selected
            - **ingredients** (*list*) - ingredients
                - (*dict*)
                    - **id** (*int*) - ingredient ID
                    - **name** (*string*) - name
                    - **cost** (*double*) - cost
            - **priority** (*int*) - priority, always positive
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



Specific store
==============

.. http:get:: /v1/customers/food/store/(int:store_id)

    Food with the given store ID.

    :reqheader X-Identifier: Identifier token of the UserToken
    :reqheader X-User: ID of the user
    :reqheader X-Device: Name of the device

    :query int store_id: ID of the store

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: user authentication failed

    :resjsonarr int id: food ID
    :resjsonarr string name: food name
    :resjsonarr double cost: cost per item
    :resjsonarr list ingredientGroups: groups of the ingredients

        - (*dict*)
            - **id** (*int*) - ingredientGroup ID
            - **name** (*string*) - name
            - **maximum** (*int*) - maximum amount of ingredients selected
            - **ingredients** (*list*) - ingredients
                - (*dict*)
                    - **id** (*int*) - ingredient ID
                    - **name** (*string*) - name
                    - **cost** (*double*) - cost
            - **priority** (*int*) - priority, always positive
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
