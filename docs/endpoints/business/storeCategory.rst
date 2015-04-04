=============
StoreCategory
=============

List
====

.. http:get:: /v1/business/storecategory/

    **Pagination disabled.**

    List the store categories.

    Authentication: :doc:`/authentication/employee`

    Serializer: :doc:`/serializers/global/storeCategory`

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 403: authentication failed
