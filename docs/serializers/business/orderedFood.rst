OrderedFood
===========

Fields
------
    - **id** (*int*) - (Default)Food ID
    - **ingredients** (*list*) - Ingredients IDs
    - **amount** (*integer*) - Amount, default 1
    - **unitAmount** (*decimal*) - Weight (unit) amount, default null
    - **original** (*int*) - Reference :doc:`/serializers/global/food` ID
    - **cost** (*decimal*) - Cost
    - **useOriginal** (*boolean*) - Use original Food

Read only
^^^^^^^^^
    - id
    - ingredients
    - amount
    - unitAmount
    - original
    - cost
    - useOriginal
