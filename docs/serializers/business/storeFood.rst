StoreFood
=========

Fields
------
    - **id** (*int*) - (Default)Food ID
    - **name** (*String*) - Name
    - **cost** (*decimal*) - Cost
    - **ingredientGroups** (:doc:`/serializers/global/ingredientGroup` list) - Ingredient groups
    - **ingredients** (*list*) - Ingredients IDs
    - **category** (:doc:`/serializers/global/foodCategory`) - Food category
    - **foodType** (:doc:`/serializers/global/foodType`) - Food type
    - **ingredients** (:doc:`/serializers/business/ingredient`) - (Default)Ingredients

Read only
^^^^^^^^^
    - id
    - ingredientGroups
