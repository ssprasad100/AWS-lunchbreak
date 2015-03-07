DefaultFood
===========

* Fields
    - **id** (*int*) - (Default)Food ID
    - **name** (*string*) - Name
    - **cost** (*decimal*) - Cost
    - **ingredientGroups** (:doc:`/serializers/global/ingredientGroup` array) - Ingredient groups
    - **ingredients** (*list*) - Ingredients IDs
    - **category** (:doc:`/serializers/global/foodCategory`) - Food category
    - **foodType** (:doc:`/serializers/global/foodType`) - Food type

* Read only fields
    - id
    - ingredientGroups
