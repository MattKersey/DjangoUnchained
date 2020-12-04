# from django.utils import timezone
from oauth2_provider.views import AuthorizationView

# from oauth2_provider.exceptions import OAuthToolkitError
# from oauth2_provider.scopes import get_scopes_backend
# from oauth2_provider.models import get_access_token_model, get_application_model
# from oauth2_provider.settings import oauth2_settings
from rest_framework import viewsets
from rest_framework.response import Response
from api.models import Association, Role, User
import requests
import json
import os


class OAuthCallbackViewSet(viewsets.ViewSet):
    authentication_classes = []
    permission_classes = []

    def list(self, request):
        CLIENT_ID = os.getenv("CLIENT_ID", "defaultTestClientID")
        CLIENT_SECRET = os.getenv("CLIENT_SECRET", "defaultTestClientSecret")
        # print(f"CLIENT_ID: {CLIENT_ID}, CLIENT_SECRET: {CLIENT_SECRET}")
        code = request.query_params["code"]
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        # print(code)
        payload = {
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "redirect_uri": "http://localhost:1234/loginredirect",
        }
        url = "http://127.0.0.1:8000/o/token/"
        r = requests.post(url, data=payload, headers=headers)
        return Response(data=json.loads(r.text))


class StoreAuthorizationView(AuthorizationView):
    def validate_authorization_request(self, request):
        _, credentials = super().validate_authorization_request(request)
        scopes = []
        user = User.objects.filter(email=request.user).first()
        associations = Association.objects.filter(user=user)
        for association in associations.all():
            print(association.role)
            if association.role in [Role.EMPLOYEE, Role.MANAGER, Role.VENDOR]:
                scopes.append("store_" + str(association.store.pk) + ":employee")
            if association.role in [Role.MANAGER, Role.VENDOR]:
                scopes.append("store_" + str(association.store.pk) + ":manager")
            if association.role == Role.VENDOR:
                scopes.append("store_" + str(association.store.pk) + ":vendor")

        return scopes, credentials
