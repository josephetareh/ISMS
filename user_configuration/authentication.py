from django.contrib.auth import get_user_model


class EmailAuthBackend(object):
    """
    class to authenticate users using their emails
    """
    user_model = get_user_model()

    def authenticate(self, request, username=None, password=None):
        # todo : maybe add it so only verified emails can be authenticated and look into stopping timing attacks here
        try:
            # in the case that an email is input into the username field, then django, then we want to check
            # against our model for this value.
            user = self.user_model.objects.get(email__iexact=username)
            if user.check_password(password):
                return user
        except self.user_model.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return self.user_model.objects.get(pk=user_id)
        except self.user_model.DoesNotExist:
            return None
