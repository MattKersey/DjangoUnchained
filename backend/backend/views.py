from rest_framework import viewsets
from rest_framework.response import Response
import requests
import json
import os


class OAuthCallbackViewSet(viewsets.ViewSet):
    authentication_classes = []
    permission_classes = []

    def list(self, request):
        CLIENT_ID = os.getenv("CLIENT_ID")
        CLIENT_SECRET = os.getenv("CLIENT_SECRET")
        code = request.query_params["code"]
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        # print(request.query_params['code'])
        # payload = 'client_id=' + os.getenv("CLIENT_ID")
        # payload += '&client_secret=' + os.getenv("CLIENT_SECRET")
        # payload += '&code=' + request.query_params['code']
        # payload += '&redirect_uri=http://127.0.0.1:8000/authredirect/'
        # payload += '&grant_type=authorization_code'

        payload = {
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "redirect_uri": "http://127.0.0.1:8000/authredirect/",
        }
        url = "http://127.0.0.1:8000/o/token/"
        r = requests.post(url, data=payload, headers=headers)
        return Response(data=json.loads(r.text))
