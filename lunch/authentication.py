from rest_framework import authentication

from lunch.models import User
from lunch.exceptions import AuthenticationFailed


class LunchbreakAuthentication(authentication.BaseAuthentication):
	def authenticate(self, request):
		identifier = request.META.get('HTTP_IDENTIFIER')
		userId = request.META.get('HTTP_USER')
		device = request.META.get('HTTP_DEVICE')

		if not identifier or not userId or not device:
			raise AuthenticationFailed('Not all of the headers were provided.')

		try:
			user = User.objects.get(userId=userId)
			user.token_set.get(identifier=identifier, device=device)
		except:
			raise AuthenticationFailed('User not found.')

		return (user, None)
