====
Food
====

Specific food
=============

.. http:get:: /v1/customers/food/(int:id)

    Food with the given ID.

    :query int id: ID of the food

    :>jsonarr int id: food ID
    :>jsonarr string name: food name
    :>jsonarr double cost: cost per item
    :>jsonarr list ingredientGroups: groups of the ingredients

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

    :>header X-Identifier: Identifier token of the UserToken
    :>header X-User: ID of the user
    :>header X-Device: Name of the device

    :<header Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: user authentication failed



Specific store
==============

.. http:get:: /v1/customers/food/store/(int:store_id)

    Food with the given store ID.

    :query int store_id: ID of the store

    :>jsonarr int id: food ID
    :>jsonarr string name: food name
    :>jsonarr double cost: cost per item
    :>jsonarr list ingredientGroups: groups of the ingredients

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

    :>header X-Identifier: Identifier token of the UserToken
    :>header X-User: ID of the user
    :>header X-Device: Name of the device

    :<header Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: user authentication failed
