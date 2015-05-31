========
Employee
========

List
====

.. http:get:: /v1/business/employee/

    **Pagination disabled.**

    Employees in the authenticated staff.

    Authentication: :doc:`/authentication/staff`

    Serializer: :doc:`/serializers/business/employee`


Login
=====

.. http:post:: /v1/business/employee/

    Log into a :doc:`/serializers/business/employee` and receive a :doc:`/serializers/business/employeeToken`

    Authentication: :doc:`/authentication/staff`

    Serializer: :doc:`/serializers/business/employeeToken`


Password reset request
======================

.. http:get:: /v1/business/employee/reset/request/(int:id)/

    Employees in the authenticated staff.

    Authentication: :doc:`/authentication/staff`

    :query int id: :doc:`/serializers/business/employee` ID
