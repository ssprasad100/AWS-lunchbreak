=====
Store
=====

Nearby stores
=============

.. http:get:: /v1/customers/store/nearby/(double:latitude)/(double:longitude)/(number:proximity)

    Stores within a proximity.

    :reqheader X-Identifier: Identifier token of the UserToken
    :reqheader X-User: ID of the user
    :reqheader X-Device: Name of the device

    :query double latitude: latitude coordinate
    :query double longitude: longitude coordinate
    :query number proximity: proximity, default is 5 km

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: user authentication failed

    :resjsonarr int id: store ID
    :resjsonarr string name: store name
    :resjsonarr string country: store country
    :resjsonarr string province: store province
    :resjsonarr string city: store city
    :resjsonarr string postcode: store postal code
    :resjsonarr string street: store street
    :resjsonarr int number: store street number
    :resjsonarr double latitude: store latitude coordinate
    :resjsonarr double longitude: store longitude coordinate
    :resjsonarr string-array categories: store categorie names


Specific store
==============

.. http:get:: /v1/customers/store/(int:store_id)

    Store with the given ID.

    :reqheader X-Identifier: Identifier token of the UserToken
    :reqheader X-User: ID of the user
    :reqheader X-Device: Name of the device

    :query int store_id: ID of the store

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: user authentication failed

    :resjsonarr int id: store ID
    :resjsonarr string name: store name
    :resjsonarr string country: store country
    :resjsonarr string province: store province
    :resjsonarr string city: store city
    :resjsonarr string postcode: store postal code
    :resjsonarr string street: store street
    :resjsonarr int number: store street number
    :resjsonarr double latitude: store latitude coordinate
    :resjsonarr double longitude: store longitude coordinate
    :resjsonarr string-array categories: store categorie names
