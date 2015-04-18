OrderedFood
===========

Fields
------
    - **id** (*int*) - (Default)Food ID
    - **ingredients** (*list*) - Ingredients IDs
    - **amount** (*decimal*) - Amount, default 1
    - **order** (*int*) - :doc:`/serializers/customers/order` ID
    - **original** (*int*) - Reference :doc:`/serializers/global/food` ID
    - **ingredientGroups** (:doc:`/serializers/global/ingredientGroup` list) - Ingredient groups
    - **cost** (*decimal*) - Cost

Read only
^^^^^^^^^
    - id
    - ingredientGroups
