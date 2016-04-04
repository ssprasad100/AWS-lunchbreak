from django.contrib.auth.models import BaseUserManager


class StaffManager(BaseUserManager):

    def create_user(self, email, password=None):
        if not password:
            raise ValueError('A password is required for staff.')

        email = self.normalize_email(email)
        staff = self.model(
            email=email
        )
        staff.set_password(password)
        staff.save()
        return staff

    def create_superuser(self, email, password):
        user = self.create_user(
            email=email,
            password=password
        )
        user.is_superuser = True
        user.save()
        return user
