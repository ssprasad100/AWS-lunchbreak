=====
Staff
=====

List
====

.. http:get:: /v1/business/staff/

    List the staff.

    Serializer: :doc:`/serializers/business/staff`

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 403: authentication failed


Login
=====

.. http:post:: /v1/business/staff/

    Log into a :doc:`/serializers/business/staff` and receive a :doc:`/serializers/business/staffToken`

    Request serializer: :doc:`/serializers/business/staff`

    Response serializer: :doc:`/serializers/business/staffToken`

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 403: authentication failed


Specific
========

.. http:get:: /v1/business/staff/(int:id)/

    Staff

    Serializer: :doc:`/serializers/business/staff`

    :resheader Content-Type: application/json

    :query int id: :doc:`/serializers/business/staff` ID

    :statuscode 200: no error
    :statuscode 403: authentication failed


Nearby
======

.. http:get:: /v1/business/staff/(decimal:latitude)/(decimal:latitude)/(decimal:proximity)/

    Staff in the authenticated staff.

    Serializer: :doc:`/serializers/business/staff`

    :resheader Content-Type: application/json

    :query decimal latitude: latitude coordinate
    :query decimal longitude: longitude coordinate
    :query decimal proximity: proximity in km, optional, default is 5 km

    :statuscode 200: no error
    :statuscode 403: authentication failed


Password reset request
======================

.. http:get:: /v1/business/staff/reset/request/(String:staff_email)/

    Send an email to reset the password off the given Staff e-mailadress.

    :resheader Content-Type: application/json

    :query String staff_email: :doc:`/serializers/business/staff` email

    :statuscode 200: no error
    :statuscode 403: authentication failed
