IngredientGroup
===============

Fields
------
    - **id** (*int*) - IngredientGroup ID
    - **name** (*String*) - Name
    - **maximum** (*int*) - Maximum amount of items selected, 0 means unlimited
    - **minimum** (*int*) - Minimum amount of items selected, 0 means no minimum
    - **ingredients** (:doc:`/serializers/global/nestedIngredient` list) - Ingredients
    - **priority** (*int*) - Priority number
    - **cost** (*decimal*) - Cost
    - **foodType** (*int*) - :doc:`/serializers/global/foodType` ID
