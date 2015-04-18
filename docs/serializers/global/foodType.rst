FoodType
========

Fields
------
    - **id** (*int*) - FoodType ID
    - **name** (*String*) - Name
    - **icon** (*int*) - Icon ID
    - **quantifier** (*String*) - Quantifier, e.g: sneedjes, kilogram...
    - **inputType** (*int*) - Integer representing how values should be inputted on the app
        + **0** - *Aantal*
        + **1** - *Gewicht*
    - **required** (*list*) - :doc:`/serializers/global/ingredientGroup` IDs
