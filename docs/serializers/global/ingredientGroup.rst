IngredientGroup
===============

Fields
------
    - **id** (*int*) - IngredientGroup ID
    - **name** (*String*) - Name
    - **maximum** (*int*) - Maximum amount of items selected, 0 means unlimited
    - **ingredients** (:doc:`/serializers/global/nestedIngredient` list) - Ingredients
    - **priority** (*int*) - Priority number
    - **cost** (*decimal*) - Cost
