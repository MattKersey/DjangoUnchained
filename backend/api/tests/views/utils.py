from django.utils import timezone
from api.models import User
import os
import datetime
from oauth2_provider.models import get_application_model, get_access_token_model

Application = get_application_model()
AccessToken = get_access_token_model()


def setupOAuth(self, stores=[]):
    CLIENT_ID = os.getenv("CLIENT_ID", "defaultTestClientID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET", "defaultTestClientSecret")
    self.user = User.objects.create_superuser(
        email="superuserOAuth@email.com", password="superuser"
    )
    self.employeeUser = User.objects.create_user(
        email="employeeOAuth@email.com", password="password"
    )
    self.managerUser = User.objects.create_user(
        email="managerOAuth@email.com", password="password"
    )
    self.application = Application.objects.create(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        client_type=Application.CLIENT_CONFIDENTIAL,
        name="OAuth-Test-API",
        redirect_uris="http://127.0.0.1:8000/authredirect/",
        skip_authorization=True,
    )
    self.application.save()
    scope = "read write"

    # EMPLOYEE
    for pk in stores:
        scope += " store_" + str(pk) + ":employee"
    self.empToken = AccessToken.objects.create(
        user=self.employeeUser,
        token="asdfhffgdhjfdjgdsfgjh",
        application=self.application,
        expires=timezone.now() + datetime.timedelta(days=1),
        scope=scope,
    )
    self.empToken.save()

    # MANAGER
    for pk in stores:
        scope += " store_" + str(pk) + ":manager"
    self.manToken = AccessToken.objects.create(
        user=self.managerUser,
        token="dfslkghjewrkjkhh",
        application=self.application,
        expires=timezone.now() + datetime.timedelta(days=1),
        scope=scope,
    )
    self.manToken.save()

    # VENDOR
    for pk in stores:
        scope += " store_" + str(pk) + ":vendor"
    self.token = AccessToken.objects.create(
        user=self.user,
        token="adfslkfjavsdfeslfkjgh",
        application=self.application,
        expires=timezone.now() + datetime.timedelta(days=1),
        scope=scope,
    )
    self.token.save()
