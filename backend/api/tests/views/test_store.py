from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from api.models import Store, Category, Item, History_of_Item
import json
from oauth2_provider.models import get_application_model, get_access_token_model
from api.tests.views.utils import setupOAuth

Application = get_application_model()
AccessToken = get_access_token_model()


class Test_StoreView(APITestCase):
    def setUp(self):
        self.file_path = settings.BASE_DIR / "api/fixtures/food.jpeg"
        with open(file=self.file_path, mode="rb") as infile:
            file = SimpleUploadedFile(self.file_path, infile.read())
            self.item1 = Item.objects.create(
                image=file,
                name="Item 1",
                stock=1,
                price=1.0,
                description="Item 1",
            )
            self.item2 = Item.objects.create(
                image=file,
                name="Item 2",
                stock=2,
                price=1.0,
                description="Item 2",
            )
            self.item3 = Item.objects.create(
                image=file,
                name="Item 3",
                stock=1,
                price=1.0,
                description="Item 3",
            )
        self.history1 = History_of_Item.objects.create(
            before_name="Item 0",
            after_name="Item 3",
            before_stock=1,
            after_stock=1,
            before_price=0.5,
            after_price=1.0,
            before_description="Item 0",
            after_description="Item 3",
        )
        self.history2 = History_of_Item.objects.create(
            before_name="Item 4",
            after_name="Item 2",
            before_stock=2,
            after_stock=2,
            before_price=0.5,
            after_price=1.0,
            before_description="Item 4",
            after_description="Item 2",
        )
        self.item3.history.add(self.history1)
        self.item3.save()
        self.item2.history.add(self.history2)
        self.item2.save()
        self.store1 = Store.objects.create(
            address="1 Main Street", name="Store 1", category=Category.FOOD
        )
        self.store2 = Store.objects.create(
            address="2 Main Street", name="Store 2", category=Category.FOOD
        )
        self.store1.items.add(self.item2)
        self.store1.save()
        self.store2.items.add(self.item3)
        self.store2.save()
        setupOAuth(self, stores=[self.store1.pk, self.store2.pk])
        url = (
            "http://127.0.0.1:8000/api/stores/"
            + str(self.store1.pk)
            + "/create_checkout_session/"
        )
        sess_res = self.client.post(
            url,
            json.dumps(
                {
                    "items": [
                        {"id": self.item2.pk, "quantity": 1},
                    ]
                }
            ),
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
            content_type="application/json",
        )
        self.example_session_id = sess_res.data

    def test_retrieve_store(self):
        url = "http://127.0.0.1:8000/api/stores/"
        r = self.client.get(
            url + str(self.store1.pk) + "/",
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual("Store 1", r.data["name"])

    def test_retrieve_store_bad(self):
        url = "http://127.0.0.1:8000/api/stores/"
        r = self.client.get(
            url + "100000000/",
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(403, r.status_code)

    def test_my_retrieve_store(self):
        url = "http://127.0.0.1:8000/api/stores/"
        r = self.client.get(
            url + str(self.store1.pk) + "/my_retrieve/",
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual(self.store1.pk, r.data["store_pk"])

    def test_my_retrieve_store_bad(self):
        url = "http://127.0.0.1:8000/api/stores/"
        r = self.client.get(
            url + "100000000/my_retrieve/",
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(404, r.status_code)
        self.assertEqual("The store does not exist.", r.data["message"])

    def test_list_store(self):
        url = "http://127.0.0.1:8000/api/stores/"
        r = self.client.get(url, HTTP_AUTHORIZATION="Bearer " + self.token.token)
        self.assertEqual(200, r.status_code)
        self.assertLessEqual(1, len(r.data))

    def test_update_store(self):
        url = "http://127.0.0.1:8000/api/stores/"
        r = self.client.put(
            url + str(self.store2.pk) + "/",
            {"name": "Updated Name"},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
            follow=True,
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual(0, Store.objects.filter(name="Store 2").count())
        self.assertEqual(1, Store.objects.filter(name="Updated Name").count())

    def test_update_store_bad(self):
        url = "http://127.0.0.1:8000/api/stores/"
        r = self.client.put(
            url + "100000000/",
            {"name": "Updated Name"},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
            follow=True,
        )
        self.assertEqual(403, r.status_code)

    def test_update_store_employee_auth(self):
        url = "http://127.0.0.1:8000/api/stores/"
        r = self.client.put(
            url + str(self.store2.pk) + "/",
            {"name": "Updated Name"},
            HTTP_AUTHORIZATION="Bearer " + self.empToken.token,
            follow=True,
        )
        self.assertEqual(403, r.status_code)

    def test_update_store_manager_auth(self):
        url = "http://127.0.0.1:8000/api/stores/"
        r = self.client.put(
            url + str(self.store2.pk) + "/",
            {"name": "Updated Name"},
            HTTP_AUTHORIZATION="Bearer " + self.manToken.token,
            follow=True,
        )
        self.assertEqual(403, r.status_code)

    def test_update_store_too_long_name(self):
        url = "http://127.0.0.1:8000/api/stores/"
        r = self.client.put(
            url + str(self.store1.pk) + "/",
            {"name": "123456789012345678901234567890123456789012345678901234567890"},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
            follow=True,
        )
        self.assertEqual(406, r.status_code)
        self.assertEqual("The store cannot be updated.", r.data["message"])

    def test_add_item(self):
        url = "http://127.0.0.1:8000/api/stores/" + str(self.store1.pk) + "/add_item/"
        r = self.client.post(
            url,
            {"item_id": self.item1.pk},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual(2, len(self.store1.items.all()))
        self.store1.items.remove(self.item1)
        self.assertEqual(1, len(self.store1.items.all()))

    def test_add_item_bad_item(self):
        url = "http://127.0.0.1:8000/api/stores/" + str(self.store1.pk) + "/add_item/"
        r = self.client.post(
            url,
            {"item_id": 100000000},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(404, r.status_code)
        self.assertEqual("The item does not exist.", r.data["message"])

    def test_add_item_bad_store(self):
        url = "http://127.0.0.1:8000/api/stores/100000000/add_item/"
        r = self.client.post(
            url,
            {"item_id": self.item1.pk},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(403, r.status_code)

    # def test_add_item_bad_combo(self):
    #     url = "http://127.0.0.1:8000/api/stores/" + str(self.store1.pk) + "/add_item/"
    #     r = self.client.post(
    #         url,
    #         {"item_id": self.item2.pk},
    #         HTTP_AUTHORIZATION="Bearer " + self.token.token,
    #     )
    #     self.assertEqual(406, r.status_code)
    #     self.assertEqual("The item cannot be added.", r.data["message"])

    def test_create_checkout_session(self):
        url = (
            "http://127.0.0.1:8000/api/stores/"
            + str(self.store1.pk)
            + "/create_checkout_session/"
        )
        r = self.client.post(
            url,
            json.dumps(
                {
                    "items": [
                        {"id": self.item2.pk, "quantity": 1},
                    ]
                }
            ),
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
            content_type="application/json",
        )
        self.assertEqual(200, r.status_code)
        self.assertContains(r, "cs_test")

    def test_add_item_employee_auth(self):
        url = "http://127.0.0.1:8000/api/stores/" + str(self.store1.pk) + "/add_item/"
        r = self.client.post(
            url,
            {"item_id": self.item1.pk},
            HTTP_AUTHORIZATION="Bearer " + self.empToken.token,
        )
        self.assertEqual(403, r.status_code)

    def test_add_item_manager_auth(self):
        url = "http://127.0.0.1:8000/api/stores/" + str(self.store1.pk) + "/add_item/"
        r = self.client.post(
            url,
            {"item_id": self.item1.pk},
            HTTP_AUTHORIZATION="Bearer " + self.manToken.token,
        )
        self.assertEqual(403, r.status_code)

    def test_purchase_items(self):
        url = (
            "http://127.0.0.1:8000/api/stores/"
            + str(self.store1.pk)
            + "/purchase_items/"
        )
        r = self.client.post(
            url,
            json.dumps({"session_id": self.example_session_id}),
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
            content_type="application/json",
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual(1, Item.objects.get(name=self.item2.name).stock)

    def test_purchase_items_bad_store(self):
        url = "http://127.0.0.1:8000/api/stores/100000000/purchase_items/"
        r = self.client.post(
            url,
            json.dumps(
                {
                    "items": [
                        {"id": self.item2.pk, "quantity": 1},
                    ]
                }
            ),
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
            content_type="application/json",
        )
        self.assertEqual(403, r.status_code)

    def test_purchase_items_over_stock(self):
        url = (
            "http://127.0.0.1:8000/api/stores/"
            + str(self.store1.pk)
            + "/create_checkout_session/"
        )
        r = self.client.post(
            url,
            json.dumps(
                {
                    "items": [
                        {"id": self.item2.pk, "quantity": 100000000000000},
                    ]
                }
            ),
            HTTP_AUTHORIZATION="Bearer " + self.empToken.token,
            content_type="application/json",
        )
        self.assertEqual(406, r.status_code)
        self.assertEqual(
            "The purchase quantity for '" + self.item2.name + "' exceeds minimum.",
            r.data["message"],
        )

    def test_purchase_items_wrong_store(self):
        url = (
            "http://127.0.0.1:8000/api/stores/"
            + str(self.store2.pk)
            + "/create_checkout_session/"
        )
        r = self.client.post(
            url,
            json.dumps(
                {
                    "items": [
                        {"id": self.item2.pk, "quantity": 1},
                    ]
                }
            ),
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
            content_type="application/json",
        )
        self.assertEqual(406, r.status_code)
        self.assertEqual(
            "The item '" + self.item2.name + "' doesn't belong to store.",
            r.data["message"],
        )

    def test_remove_item(self):
        url = (
            "http://127.0.0.1:8000/api/stores/" + str(self.store1.pk) + "/remove_item/"
        )
        r = self.client.post(
            url,
            {"item_id": self.item2.pk},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual(0, len(self.store1.items.all()))
        self.store1.items.add(self.item2)
        self.assertEqual(1, len(self.store1.items.all()))

    def test_remove_item_bad_item(self):
        url = (
            "http://127.0.0.1:8000/api/stores/" + str(self.store1.pk) + "/remove_item/"
        )
        r = self.client.post(
            url,
            {"item_id": 100000000},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(404, r.status_code)
        self.assertEqual("The item does not exist.", r.data["message"])

    def test_remove_item_bad_store(self):
        url = "http://127.0.0.1:8000/api/stores/100000000/remove_item/"
        r = self.client.post(
            url,
            {"item_id": self.item2.pk},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(403, r.status_code)

    def test_remove_item_employee_auth(self):
        url = (
            "http://127.0.0.1:8000/api/stores/" + str(self.store1.pk) + "/remove_item/"
        )
        r = self.client.post(
            url,
            {"item_id": self.item2.pk},
            HTTP_AUTHORIZATION="Bearer " + self.empToken.token,
        )
        self.assertEqual(403, r.status_code)

    def test_remove_item_manager_auth(self):
        url = (
            "http://127.0.0.1:8000/api/stores/" + str(self.store1.pk) + "/remove_item/"
        )
        r = self.client.post(
            url,
            {"item_id": self.item2.pk},
            HTTP_AUTHORIZATION="Bearer " + self.manToken.token,
        )
        self.assertEqual(403, r.status_code)

    # def test_remove_item_bad_combo(self):
    #     url = (
    #         "http://127.0.0.1:8000/api/stores/" + str(self.store2.pk) + "/remove_item/"
    #     )
    #     r = self.client.post(
    #         url,
    #         {"item_id": self.item2.pk},
    #         HTTP_AUTHORIZATION="Bearer " + self.token.token,
    #     )
    #     self.assertEqual(406, r.status_code)
    #     self.assertEqual("The item cannot be added.", r.data["message"])

    def test_delete_item(self):
        url = "http://127.0.0.1:8000/api/stores/delete_item/"
        r = self.client.delete(
            url,
            {"item_id": self.item3.pk, "store_id": self.store2.pk},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual(0, Item.objects.filter(name="Item 3").count())

    def test_delete_item_bad_item(self):
        url = "http://127.0.0.1:8000/api/stores/delete_item/"
        r = self.client.delete(
            url,
            {"item_id": 100000000, "store_id": self.store2.pk},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(404, r.status_code)
        self.assertEqual("The item does not exist.", r.data["message"])

    def test_delete_item_bad_store(self):
        url = "http://127.0.0.1:8000/api/stores/delete_item/"
        r = self.client.delete(
            url,
            {"item_id": self.item3.pk, "store_id": 100000000},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(403, r.status_code)

    def test_delete_item_employee_auth(self):
        url = "http://127.0.0.1:8000/api/stores/delete_item/"
        r = self.client.delete(
            url,
            {"item_id": self.item3.pk, "store_id": self.store2.pk},
            HTTP_AUTHORIZATION="Bearer " + self.empToken.token,
        )
        self.assertEqual(403, r.status_code)

    def test_delete_item_manager_auth(self):
        url = "http://127.0.0.1:8000/api/stores/delete_item/"
        r = self.client.delete(
            url,
            {"item_id": self.item3.pk, "store_id": self.store2.pk},
            HTTP_AUTHORIZATION="Bearer " + self.manToken.token,
        )
        self.assertEqual(403, r.status_code)

    def test_delete_item_bad_combo(self):
        url = "http://127.0.0.1:8000/api/stores/delete_item/"
        r = self.client.delete(
            url,
            {"item_id": self.item2.pk, "store_id": self.store2.pk},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(406, r.status_code)
        self.assertEqual("The item cannot be deleted.", r.data["message"])
