=============
StoreCategory
=============

List
====

.. http:get:: /v1/customers/storecategory/

    **Pagination disabled.**

    List the store categories.

    Authentication: :doc:`/authentication/user`

    Serializer: :doc:`/serializers/global/StoreCategory`

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 403: authentication failed
