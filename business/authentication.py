from business.models import StaffToken, EmployeeToken
from lunch.authentication import TokenAuthentication


class StaffAuthentication(TokenAuthentication):
    FOREIGN_KEY_ATTRIBUTE = 'staff'
    FOREIGN_KEY_TOKEN = StaffToken


class EmployeeAuthentication(TokenAuthentication):
    FOREIGN_KEY_ATTRIBUTE = 'employee'
    FOREIGN_KEY_TOKEN = EmployeeToken
