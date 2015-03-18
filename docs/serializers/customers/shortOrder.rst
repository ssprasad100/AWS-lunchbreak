ShortOrder
==========

* Fields
    - **id** (*int*) - Order ID
    - **name** (*String*) - Name
    - **store** (:doc:`/serializers/customers/shortStore`) - ShortStore
    - **storeId** (*int*) - :doc:`/serializers/global/store` ID
    - **pickupTime** (*datetime*) - Datetime of pickup
    - **paid** (*boolean*) - Already paid or not
    - **total** (*decimal*) - Total cost
    - **food** (:doc:`/serializers/customers/orderedFood` array) - Ordered food, cannot be empty

* Read only fields
    - id
    - store
    - paid
    - total

* Write only fields
    - storeId
    - pickupTime
    - food
