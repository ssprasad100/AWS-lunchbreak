OrderedFood
===========

* Fields extends :doc:`/serializers/global/food`
    - **referenceId** (*int*) - Reference :doc:`/serializers/global/food` ID, not required
    - **amount** (*int*) - Amount, default 1

* Read only fields
    - id
    - ingredientGroups
    - store
    - category
    - name

* Write only fields
    - referenceId
