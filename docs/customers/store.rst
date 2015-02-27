=====
Store
=====

Nearby stores
=============

.. http:get:: /v1/customers/store/nearby/(double:latitude)/(double:longitude)/(number:proximity)

    Stores within a proximity.

    :query double latitude: latitude coordinate
    :query double longitude: longitude coordinate
    :query number proximity: proximity, default is 5 km

    :>jsonarr int id: store ID
    :>jsonarr string name: store name
    :>jsonarr string country: store country
    :>jsonarr string province: store province
    :>jsonarr string city: store city
    :>jsonarr string postcode: store postal code
    :>jsonarr string street: store street
    :>jsonarr int number: store street number
    :>jsonarr double latitude: store latitude coordinate
    :>jsonarr double longitude: store longitude coordinate
    :>jsonarr string-array categories: store categorie names

    :>header X-Identifier: Identifier token of the UserToken
    :>header X-User: ID of the user
    :>header X-Device: Name of the device

    :<header Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: user authentication failed


Specific store
==============

.. http:get:: /v1/customers/store/(int:store_id)

    Store with the given ID.

    :query int store_id: ID of the store

    :>jsonarr int id: store ID
    :>jsonarr string name: store name
    :>jsonarr string country: store country
    :>jsonarr string province: store province
    :>jsonarr string city: store city
    :>jsonarr string postcode: store postal code
    :>jsonarr string street: store street
    :>jsonarr int number: store street number
    :>jsonarr double latitude: store latitude coordinate
    :>jsonarr double longitude: store longitude coordinate
    :>jsonarr string-array categories: store categorie names

    :>header X-Identifier: Identifier token of the UserToken
    :>header X-User: ID of the user
    :>header X-Device: Name of the device

    :<header Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: user authentication failed
