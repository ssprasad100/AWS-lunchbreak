========
Employee
========

List
====

.. http:get:: /v1/business/employee/

    Employees in the authenticated staff.

    Authentication: :doc:`/authentication/staff`

    Serializer: :doc:`/serializers/business/employee`

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: authentication failed


Login
=====

.. http:post:: /v1/business/employee/

    Log into a :doc:`/serializers/business/employee` and receive a :doc:`/serializers/business/employeeToken`

    Authentication: :doc:`/authentication/staff`

    Request serializer: :doc:`/serializers/business/employee`

    Response serializer: :doc:`/serializers/business/employeeToken`

    :resheader Content-Type: application/json

    :statuscode 200: no error
    :statuscode 401: authentication failed


Specific
========

.. http:get:: /v1/business/employee/(int:employee_id)/

    Employees in the authenticated staff.

    Authentication: :doc:`/authentication/staff`

    Serializer: :doc:`/serializers/business/employee`

    :resheader Content-Type: application/json

    :query int employee_id: :doc:`/serializers/business/employee` ID

    :statuscode 200: no error
    :statuscode 401: authentication failed


Password reset request
======================

.. http:get:: /v1/business/employee/reset/request/(int:employee_id)/

    Employees in the authenticated staff.

    Authentication: :doc:`/authentication/staff`

    :resheader Content-Type: application/json

    :query int employee_id: :doc:`/serializers/business/employee` ID

    :statuscode 200: no error
    :statuscode 401: authentication failed
