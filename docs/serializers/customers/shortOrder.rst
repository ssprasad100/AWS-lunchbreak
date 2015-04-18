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
    - **status** (*int*) - Status number
        + **0** - *Placed*
        + **1** - *Denied*
        + **2** - *Received*
        + **3** - *Started*
        + **4** - *Waiting*
        + **5** - *Completed*

Read only
^^^^^^^^^
    - id
    - paid
    - total
    - status
