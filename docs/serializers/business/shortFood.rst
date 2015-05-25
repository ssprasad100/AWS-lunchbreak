ShortFood
=========

Fields
------
    - **id** (*int*) - (Default)Food ID
    - **name** (*String*) - Name
    - **cost** (*decimal*) - Cost
    - **ingredients** (*list*) - Ingredients IDs
    - **category** (:doc:`/serializers/global/foodCategory`) - Food category
    - **foodType** (:doc:`/serializers/global/foodType`) - Food type
    - **ingredients** (:doc:`/serializers/business/ingredient`) - (Default)Ingredients
    - **ingredientRelations** (:doc:`/serializers/business/ingredient`) - (Default)Ingredients

Read only
^^^^^^^^^
    - id
    - name
    - ingredients

Write only
^^^^^^^^^^
    - ingredientRelations


The difference between ingredients and ingredientRelations is in the backend and won't be explained in these docs. Just keep in mind to use ingredients when reading and ingredientRelations when writing.
