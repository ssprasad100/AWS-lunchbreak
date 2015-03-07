Order
=====

* Fields
    - **id** (*int*) - Order ID
    - **name** (*string*) - Name
    - **store** (:doc:`/serializers/global/store`) - Store
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
    - **food** (:doc:`/serializers/customers/orderedFood` array) - Ordered food

* Read only fields
    - id
    - store
    - orderedTime
    - pickupTime
    - status
    - paid
    - total
    - food
