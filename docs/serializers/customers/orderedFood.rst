OrderedFood
===========

Fields extends :doc:`/serializers/global/food`
----------------------------------------------
    - **referenceId** (*int*) - Reference :doc:`/serializers/global/food` ID, not required
    - **amount** (*int*) - Amount, default 1

Read only
^^^^^^^^^
    - id
    - ingredientGroups
    - store
    - category
    - name

Write only
^^^^^^^^^^
    - referenceId
