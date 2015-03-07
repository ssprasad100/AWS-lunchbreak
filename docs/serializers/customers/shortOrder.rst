ShortOrder
==========

* Fields
    - **id** (*int*) - Order ID
    - **name** (*string*) - Name
    - **store** (:doc:`/serializers/global/store`) - Store
    - **pickupTime** (*datetime*) - Datetime of pickup
    - **paid** (*boolean*) - Already paid or not
    - **total** (*decimal*) - Total cost
    - **food** (:doc:`/serializers/customers/orderedFood` array) - Ordered food

* Read only fields
    - id
    - paid
    - total

* Write only fields
    - store
    - pickupTime
    - food
