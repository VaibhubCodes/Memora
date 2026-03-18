from django.contrib.auth import get_user_model

User = get_user_model()


class EmailBackend:
    def authenticate(self, request, username=None, email=None, password=None, **kwargs):
        login_value = email or username
        if not login_value or not password:
            return None

        try:
            user = User.objects.get(email=login_value)
        except User.DoesNotExist:
            return None

        if user.check_password(password) and user.is_active:
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None