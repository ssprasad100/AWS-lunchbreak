ShortOrder
==========

Fields
------
    - **id** (*int*) - Order ID
    - **user** (:doc:`/serializers/business/privateUser`) - User
    - **orderedTime** (*datetime*) - Time of order
    - **pickupTime** (*datetime*) - Time of pickup
    - **status** (*int*) - Status number
        + **0** - *Placed*
        + **1** - *Denied*
        + **2** - *Received*
        + **3** - *Started*
        + **4** - *Waiting*
        + **5** - *Completed*
    - **paid** (*boolean*) - Paid or not
    - **total** (*decimal*) - Total cost


Read only
^^^^^^^^^
    - id
    - user
    - orderedTime
    - pickupTime
    - paid
    - total
