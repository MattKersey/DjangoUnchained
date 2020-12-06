from rest_framework.test import APITestCase
from api.models import Store, Category, Association, Role
import datetime
import requests_mock
from oauth2_provider.models import get_application_model, get_access_token_model
from api.tests.views.utils import setupOAuth

Application = get_application_model()
AccessToken = get_access_token_model()


class Test_OAuth(APITestCase):
    def setUp(self):
        setupOAuth(self)
        self.store = Store.objects.create(
            address="1 Main Street", name="Test Store", category=Category.FOOD
        )
        self.user.stores.add(self.store)
        time = datetime.datetime.now().date()
        self.association = Association.objects.create(
            user=self.user,
            store=self.store,
            membership=time,
            role=Role.VENDOR,
        )
        self.user.save()

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
            "POST",
            "http://127.0.0.1:8000/o/token/",
            text='{"testdata": "hello world!"}',
        )
        url = "http://127.0.0.1:8000/o/authorize/"
        url += "?response_type=code"
        url += "&client_id=" + self.application.client_id
        url += "&redirect_uri=http://127.0.0.1:8000/authredirect/"
        r = self.client.get(url, follow=True)
        self.assertEqual(200, r.status_code)
        self.assertEqual(b'{"testdata":"hello world!"}', r.content)
        pass

    def tearDown(self):
        self.user.delete()
        self.application.delete()
        self.token.delete()
        pass
