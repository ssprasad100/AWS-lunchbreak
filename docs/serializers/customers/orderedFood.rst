OrderedFood
===========

Fields
------
    - **id** (*int*) - (Default)Food ID
    - **ingredients** (*list*) - Ingredients IDs. **Do not send ingredients if the original hasn't been edited! An empty list means no ingredients were selected!**
    - **amount** (*integer*) - Amount, default 1
    - **order** (*int*) - :doc:`/serializers/customers/order` ID
    - **original** (*int*) - Reference :doc:`/serializers/global/food` ID
    - **ingredientGroups** (:doc:`/serializers/global/ingredientGroup` list) - Ingredient groups
    - **cost** (*decimal*) - Cost
    - **useOriginal** (*boolean*) - Use original Food

Read only
^^^^^^^^^
    - id
    - ingredientGroups
    - useOriginal
