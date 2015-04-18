Order
=====

Fields
------
    - **id** (*int*) - Order ID
    - **store** (*int*) - :doc:`/serializers/global/store` ID
    - **orderedTime** (*datetime*) - Datetime of order
    - **pickupTime** (*datetime*) - Datetime of pickup
    - **status** (*int*) - Status number
        + **0** - *Placed*
        + **1** - *Denied*
        + **2** - *Received*
        + **3** - *Started*
        + **4** - *Waiting*
        + **5** - *Completed*
    - **paid** (*boolean*) - Already paid or not
    - **total** (*decimal*) - Total cost
    - **orderedFood** (:doc:`/serializers/customers/orderedFood` list) - Ordered food

Read only
^^^^^^^^^
    - id
    - store
    - orderedTime
    - pickupTime
    - status
    - paid
    - total
    - food
