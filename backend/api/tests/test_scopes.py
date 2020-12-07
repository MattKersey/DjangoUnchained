from django.test import TestCase
from api.models import Store, Category
from backend.scopes import CustomScopes

from oauth2_provider.models import get_application_model, get_access_token_model

Application = get_application_model()
AccessToken = get_access_token_model()


class Test_CustomScopes(TestCase):
    def setUp(self):
        self.customScopes = CustomScopes()
        self.store = Store.objects.create(
            address="1 Main Street", name="Test Store", category=Category.FOOD
        )

    def test_get_all_scopes(self):
        scopes = self.customScopes.get_all_scopes()
        self.assertTrue("store_1:employee" in scopes.keys())
        self.assertTrue("store_1:manager" in scopes.keys())
        self.assertTrue("store_1:vendor" in scopes.keys())

    def test_get_available_scopes(self):
        scopes = self.customScopes.get_available_scopes()
        self.assertTrue("store_1:employee" in scopes)
        self.assertTrue("store_1:manager" in scopes)
        self.assertTrue("store_1:vendor" in scopes)

    def test_get_default_scopes(self):
        scopes = self.customScopes.get_default_scopes()
        self.assertTrue("store_1:employee" in scopes)
        self.assertTrue("store_1:manager" in scopes)
        self.assertTrue("store_1:vendor" in scopes)
