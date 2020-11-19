from django.utils import timezone
from rest_framework.test import APITestCase
from api.models import User
import datetime
import requests_mock

from oauth2_provider.models import get_application_model, get_access_token_model

Application = get_application_model()
AccessToken = get_access_token_model()


class Test_OAuth(APITestCase):
    def setUp(self):
        # oauth2_settings._SCOPES = ["read", "write"
        CLIENT_ID = "abselskfjlskdfj"
        CLIENT_SECRET = "laksdfjlaksjdflksjdflksdjf"
        self.user = User.objects.create_superuser(
            email="superuserOAuth@email.com", password="superuser"
        )
        self.application = Application.objects.create(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            client_type=Application.CLIENT_CONFIDENTIAL,
            name="OAuth-Test-API",
            redirect_uris="http://127.0.0.1:8000/authredirect/",
            skip_authorization=True
        )
        self.application.save()
        self.token = AccessToken.objects.create(
            user=self.user,
            token="adfslkfjavsdfeslfkjgh",
            application=self.application,
            expires=timezone.now() + datetime.timedelta(days=1),
            scope="read write",
        )
        self.token.save()

    def test_bad_access(self):
        url = "http://127.0.0.1:8000/api/ping/"
        r = self.client.get(url)
        self.assertEqual(401, r.status_code)
        self.assertEqual(
            b'{"detail":"Authentication credentials were not provided."}', r.content
        )

    def test_good_access(self):
        url = "http://127.0.0.1:8000/api/ping/"
        r = self.client.get(url, HTTP_AUTHORIZATION="Bearer " + self.token.token)
        self.assertEqual(200, r.status_code)
        self.assertEqual(b'{"ping":"pong"}', r.content)

    @requests_mock.Mocker()
    def test_OAuth_redirect(self, m):
        self.client.force_login(self.user)
        m.register_uri(
            'POST',
            'http://127.0.0.1:8000/o/token/',
            text="{\"testdata\": \"hello world!\"}"
        )
        url = 'http://127.0.0.1:8000/o/authorize/'
        url += '?response_type=code'
        url += '&client_id=' + self.application.client_id
        url += '&redirect_uri=http://127.0.0.1:8000/authredirect/'
        r = self.client.get(url, follow=True)
        print(r.content)
        self.assertEqual(200, r.status_code)
        self.assertEqual(b'{"testdata":"hello world!"}', r.content)
        pass

    def tearDown(self):
        self.application.delete()
        self.token.delete()
        pass
