ShortOrder
==========

Fields
------
    - **id** (*int*) - Order ID
    - **user** (:doc:`/serializers/business/privateUser`) - User
    - **orderedTime** (*datetime*) - Time of order
    - **pickupTime** (*datetime*) - Time of pickup
    - **status** (*int*) - :ref:`orderStatusses`.
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
