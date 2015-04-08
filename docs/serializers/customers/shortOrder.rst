ShortOrder
==========

Fields
------
    - **id** (*int*) - Order ID
    - **name** (*String*) - Name
    - **store** (:doc:`/serializers/customers/shortStore`) - ShortStore
    - **storeId** (*int*) - :doc:`/serializers/global/store` ID
    - **pickupTime** (*datetime*) - Datetime of pickup
    - **paid** (*boolean*) - Already paid or not
    - **total** (*decimal*) - Total cost
    - **food** (:doc:`/serializers/customers/orderedFood` array) - Ordered food, cannot be empty
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
    - store
    - paid
    - total
    - status

Write only
^^^^^^^^^^
    - storeId
    - food
