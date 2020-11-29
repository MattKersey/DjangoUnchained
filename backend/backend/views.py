from django.utils import timezone
from oauth2_provider.views import AuthorizationView
from oauth2_provider.exceptions import OAuthToolkitError
from oauth2_provider.scopes import get_scopes_backend
from oauth2_provider.models import get_access_token_model, get_application_model
from oauth2_provider.settings import oauth2_settings
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
    # This method is a slight modification of the get method from AuthorizationView
    # You can find the original in the Django-OAuth-Toolkit repo at
    # https://github.com/jazzband/django-oauth-toolkit/blob/master/oauth2_provider/views/base.py
    # This version dynamically determines scope
    def get(self, request, *args, **kwargs):
        try:
            _, credentials = self.validate_authorization_request(request)
        except OAuthToolkitError as error:
            # Application is not available at this time.
            return self.error_response(error, application=None)
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

        all_scopes = get_scopes_backend().get_all_scopes()
        kwargs["scopes_descriptions"] = [all_scopes[scope] for scope in scopes]
        kwargs["scopes"] = scopes
        # at this point we know an Application instance with such client_id exists in the database

        # TODO: Cache this!
        application = get_application_model().objects.get(client_id=credentials["client_id"])

        kwargs["application"] = application
        kwargs["client_id"] = credentials["client_id"]
        kwargs["redirect_uri"] = credentials["redirect_uri"]
        kwargs["response_type"] = credentials["response_type"]
        kwargs["state"] = credentials["state"]
        if "code_challenge" in credentials:
            kwargs["code_challenge"] = credentials["code_challenge"]
        if "code_challenge_method" in credentials:
            kwargs["code_challenge_method"] = credentials["code_challenge_method"]

        self.oauth2_data = kwargs
        # following two loc are here only because of https://code.djangoproject.com/ticket/17795
        form = self.get_form(self.get_form_class())
        kwargs["form"] = form

        # Check to see if the user has already granted access and return
        # a successful response depending on "approval_prompt" url parameter
        require_approval = request.GET.get(
            "approval_prompt",
            oauth2_settings.REQUEST_APPROVAL_PROMPT
        )

        try:
            # If skip_authorization field is True, skip the authorization screen even
            # if this is the first use of the application and there was no previous authorization.
            # This is useful for in-house applications-> assume an in-house applications
            # are already approved.
            if application.skip_authorization:
                uri, headers, body, status = self.create_authorization_response(
                    request=self.request,
                    scopes=" ".join(scopes),
                    credentials=credentials,
                    allow=True
                )
                return self.redirect(uri, application)

            elif require_approval == "auto":
                tokens = (
                    get_access_token_model()
                    .objects.filter(
                        user=request.user,
                        application=kwargs["application"],
                        expires__gt=timezone.now()
                    )
                    .all()
                )

                # check past authorizations regarded the same scopes as the current one
                for token in tokens:
                    if token.allow_scopes(scopes):
                        uri, headers, body, status = self.create_authorization_response(
                            request=self.request,
                            scopes=" ".join(scopes),
                            credentials=credentials,
                            allow=True
                        )
                        return self.redirect(uri, application, token)

        except OAuthToolkitError as error:
            return self.error_response(error, application)

        return self.render_to_response(self.get_context_data(**kwargs))
