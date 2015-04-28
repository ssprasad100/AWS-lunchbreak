ShortOrder
==========

Fields
------
    - **id** (*int*) - Order ID
    - **store** (*int*) - :doc:`/serializers/global/store` ID
    - **pickupTime** (*datetime*) - Datetime of pickup
    - **paid** (*boolean*) - Already paid or not
    - **total** (*decimal*) - Total cost
    - **orderedFood** (:doc:`/serializers/customers/orderedFood` list) - Ordered food, cannot be empty
    - **status** (*int*) - :ref:`orderStatusses`.

Read only
^^^^^^^^^
    - id
    - paid
    - total
    - status
