ShortFood
=========

Fields
------
    - **id** (*int*) - (Default)Food ID
    - **name** (*String*) - Name
    - **cost** (*decimal*) - Cost
    - **category** (:doc:`/serializers/global/foodCategory`) - Food category
    - **foodType** (:doc:`/serializers/global/foodType`) - Food type
    - **ingredients** (list) - :doc:`/serializers/business/ingredient` IDs
    - **ingredientRelations** (:doc:`/serializers/business/ingredient`) - (Default)Ingredients

Read only
^^^^^^^^^
    - id
    - ingredients

Write only
^^^^^^^^^^
    - ingredientRelations


The difference between ingredients and ingredientRelations is in the backend and won't be explained in these docs. Just keep in mind to use ingredients when reading and ingredientRelations when writing.
