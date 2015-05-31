=====
Staff
=====

Login
=====

.. http:post:: /v1/business/staff/

    Log into a :doc:`/serializers/business/staff` and receive a :doc:`/serializers/business/staffToken`

    Serializer: :doc:`/serializers/business/staffToken`


Nearby
======

.. http:get:: /v1/business/staff/(decimal:latitude)/(decimal:latitude)/(decimal:proximity)/

    Staff in the authenticated staff.

    Serializer: :doc:`/serializers/business/staff`

    :query decimal latitude: latitude coordinate
    :query decimal longitude: longitude coordinate
    :query decimal proximity: proximity in km, optional, default is 5 km


Retrieve
========

.. http:get:: /v1/business/staff/(int:id)/

    Retrieve a staff by its ID.

    Authentication: :doc:`/authentication/staff`

    Serializer: :doc:`/serializers/business/staff`

    :query int id: :doc:`/serializers/business/staff` ID


Password reset request
======================

.. http:get:: /v1/business/staff/reset/request/(String:staff_email)/

    Send an email to reset the password off the given Staff e-mailadress.

    :query String staff_email: :doc:`/serializers/business/staff` email
