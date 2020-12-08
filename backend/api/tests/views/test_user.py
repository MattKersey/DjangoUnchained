from rest_framework.test import APITestCase
from api.models import User, Store, Category, Association, Role
from oauth2_provider.models import get_application_model, get_access_token_model
from api.tests.views.utils import setupOAuth

Application = get_application_model()
AccessToken = get_access_token_model()


class Test_UserView(APITestCase):
    def setUp(self):
        self.store1 = Store.objects.create(
            address="1 Main Street", name="Store 1", category=Category.FOOD
        )
        self.store2 = Store.objects.create(
            address="2 Main Street", name="Store 2", category=Category.FOOD
        )
        self.store3 = Store.objects.create(
            address="3 Main Street", name="Store 3", category=Category.FOOD
        )
        self.userExists = User.objects.create_user(
            email="exists@example.com", password="password"
        )
        self.userExists.stores.add(self.store2)
        self.userExists.save()
        self.userMods = User.objects.create_user(
            email="before@example.com", password="password"
        )
        self.userMods.stores.add(self.store3)
        self.association1 = Association.objects.get(
            user=self.userMods, store=self.store3
        )
        self.association1.role = Role.EMPLOYEE
        self.association1.save()
        self.employee_user = User.objects.create_user(
            email="employee@example.com", password="employee"
        )
        self.manager_user = User.objects.create_user(
            email="manager@example.com", password="manager"
        )
        self.vendor_user = User.objects.create_user(
            email="vendor@example.com", password="vendor"
        )
        setupOAuth(self, stores=[self.store1.pk, self.store2.pk, self.store3.pk])

    def test_register_good(self):
        url = "http://127.0.0.1:8000/api/register/"
        user = {"email": "testuser@example.com", "password": "testpassword"}
        r = self.client.post(url, user)
        self.assertEqual(201, r.status_code)
        self.assertEqual(1, r.data["status"])

    def test_register_bad(self):
        url = "http://127.0.0.1:8000/api/register/"
        user = {"email": "exists@example.com", "password": "testpassword"}
        r = self.client.post(url, user)
        self.assertEqual(400, r.status_code)
        self.assertEqual(0, r.data["status"])

    def test_retrieve_user(self):
        url = "http://127.0.0.1:8000/api/users/"
        r = self.client.get(
            url + str(self.userExists.pk) + "/",
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual("exists@example.com", r.data["email"])

    def test_retrieve_user_does_not_exist(self):
        url = "http://127.0.0.1:8000/api/users/"
        r = self.client.get(
            url + "10000000/",
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(404, r.status_code)
        self.assertEqual("The user does not exist.", r.data["message"])

    def test_list_user(self):
        url = "http://127.0.0.1:8000/api/users/"
        r = self.client.get(url, HTTP_AUTHORIZATION="Bearer " + self.token.token)
        self.assertEqual(200, r.status_code)
        self.assertLessEqual(1, len(r.data))

    def test_update_user(self):
        url = "http://127.0.0.1:8000/api/users/"
        r = self.client.put(
            url + str(self.userMods.pk) + "/",
            {"email": "after@example.com"},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
            follow=True,
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual(0, User.objects.filter(email="before@example.com").count())
        self.assertEqual(1, User.objects.filter(email="after@example.com").count())

    def test_update_user_does_not_exist(self):
        url = "http://127.0.0.1:8000/api/users/"
        r = self.client.put(
            url + "100000000/",
            {"email": "after@example.com"},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
            follow=True,
        )
        self.assertEqual(404, r.status_code)
        self.assertEqual("The user does not exist.", r.data["message"])

    def test_update_user_email_already_used(self):
        url = "http://127.0.0.1:8000/api/users/"
        r = self.client.put(
            url + str(self.userExists.pk) + "/",
            {"email": "superuserOAuth@email.com"},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
            follow=True,
        )
        self.assertEqual(304, r.status_code)
        self.assertEqual("A user with that email already exist.", r.data["message"])

    def test_add_store(self):
        url = (
            "http://127.0.0.1:8000/api/users/" + str(self.userExists.pk) + "/add_store/"
        )
        r = self.client.post(
            url,
            {
                "name": self.store3.name,
                "category": self.store3.category,
                "address": self.store3.address,
            },
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual(2, len(self.userExists.stores.all()))
        self.userExists.stores.remove(self.store3)

    def test_add_store_bad_user(self):
        url = "http://127.0.0.1:8000/api/users/100000000/add_store/"
        r = self.client.post(
            url,
            {
                "name": self.store3.name,
                "category": self.store3.category,
                "address": self.store3.address,
            },
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(400, r.status_code)
        self.assertEqual("The user does not exist", r.data["message"])

    def test_add_store_too_long_name(self):
        url = (
            "http://127.0.0.1:8000/api/users/" + str(self.userExists.pk) + "/add_store/"
        )
        r = self.client.post(
            url,
            {
                "name": "123456789012345678901234567890123456789012345678901234567890",
                "category": self.store3.category,
                "address": self.store3.address,
            },
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(406, r.status_code)
        self.assertEqual("The store cannot be added.", r.data["message"])
        self.assertEqual(1, len(self.userExists.stores.all()))

    def test_add_store_no_name(self):
        url = (
            "http://127.0.0.1:8000/api/users/" + str(self.userExists.pk) + "/add_store/"
        )
        r = self.client.post(
            url,
            {
                "category": self.store3.category,
                "address": self.store3.address,
            },
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(400, r.status_code)
        self.assertEqual("Please add name to store", r.data["message"])
        self.assertEqual(1, len(self.userExists.stores.all()))

    def test_add_store_no_address(self):
        url = (
            "http://127.0.0.1:8000/api/users/" + str(self.userExists.pk) + "/add_store/"
        )
        r = self.client.post(
            url,
            {
                "name": self.store3.name,
                "category": self.store3.category,
            },
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(400, r.status_code)
        self.assertEqual("Please add address to store", r.data["message"])
        self.assertEqual(1, len(self.userExists.stores.all()))

    def test_add_store_no_category(self):
        url = (
            "http://127.0.0.1:8000/api/users/" + str(self.userExists.pk) + "/add_store/"
        )
        r = self.client.post(
            url,
            {
                "name": self.store3.name,
                "address": self.store3.address,
            },
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(400, r.status_code)
        self.assertEqual("Invalid category.", r.data["message"])
        self.assertEqual(1, len(self.userExists.stores.all()))

    def test_add_store_bad_category(self):
        url = (
            "http://127.0.0.1:8000/api/users/" + str(self.userExists.pk) + "/add_store/"
        )
        r = self.client.post(
            url,
            {
                "name": self.store3.name,
                "category": "brick",
                "address": self.store3.address,
            },
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(400, r.status_code)
        self.assertEqual("Invalid category.", r.data["message"])
        self.assertEqual(1, len(self.userExists.stores.all()))

    def test_remove_store(self):
        url = (
            "http://127.0.0.1:8000/api/users/"
            + str(self.userExists.pk)
            + "/remove_store/"
        )
        r = self.client.post(
            url,
            {"store_id": self.store2.pk},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual(0, len(self.userExists.stores.all()))
        self.userExists.stores.add(self.store2)
        self.assertEqual(1, len(self.userExists.stores.all()))

    def test_remove_store_employee_auth(self):
        url = (
            "http://127.0.0.1:8000/api/users/"
            + str(self.employeeUser.pk)
            + "/remove_store/"
        )
        r = self.client.post(
            url,
            {"store_id": self.store2.pk},
            HTTP_AUTHORIZATION="Bearer " + self.empToken.token,
        )
        self.assertEqual(403, r.status_code)

    def test_remove_store_bad_user(self):
        url = "http://127.0.0.1:8000/api/users/100000000/remove_store/"
        r = self.client.post(
            url,
            {"store_id": self.store2.pk},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(404, r.status_code)
        self.assertEqual("The user does not exist.", r.data["message"])

    def test_remove_store_bad_store(self):
        url = (
            "http://127.0.0.1:8000/api/users/"
            + str(self.userExists.pk)
            + "/remove_store/"
        )
        r = self.client.post(
            url,
            {"store_id": 100000000},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(403, r.status_code)

    def test_remove_store_bad_association(self):
        url = (
            "http://127.0.0.1:8000/api/users/"
            + str(self.userExists.pk)
            + "/remove_store/"
        )
        r = self.client.post(
            url,
            {"store_id": self.store3.pk},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(404, r.status_code)
        self.assertEqual("The association does not exist.", r.data["message"])

    def test_remove_store_bad_role(self):
        url = (
            "http://127.0.0.1:8000/api/users/"
            + str(self.userMods.pk)
            + "/remove_store/"
        )
        r = self.client.post(
            url,
            {"store_id": self.store3.pk},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(503, r.status_code)
        self.assertEqual(
            "You don't have the permission to add an item", r.data["message"]
        )

    def test_delete_store(self):
        url = (
            "http://127.0.0.1:8000/api/users/"
            + str(self.userExists.pk)
            + "/delete_store/"
        )
        store_id = self.store2.pk
        r = self.client.delete(
            url,
            {"user_id": self.userExists.pk, "store_id": self.store2.pk},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual(0, self.userExists.stores.all().count())
        self.assertFalse(Store.objects.filter(pk=store_id).exists())
        self.assertFalse(
            Association.objects.filter(
                user=self.userExists, store__pk=store_id
            ).exists()
        )

    def test_delete_store_bad_user(self):
        url = "http://127.0.0.1:8000/api/users/100000000/delete_store/"
        r = self.client.delete(
            url,
            {"user_id": 100000000, "store_id": self.store3.pk},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(404, r.status_code)
        self.assertEqual("The user does not exist.", r.data["message"])

    def test_delete_store_employee_auth(self):
        url = (
            "http://127.0.0.1:8000/api/users/"
            + str(self.employeeUser.pk)
            + "/delete_store/"
        )
        r = self.client.delete(
            url,
            {"user_id": self.employeeUser.pk, "store_id": self.store3.pk},
            HTTP_AUTHORIZATION="Bearer " + self.empToken.token,
        )
        self.assertEqual(403, r.status_code)

    def test_delete_store_manager_auth(self):
        url = (
            "http://127.0.0.1:8000/api/users/"
            + str(self.managerUser.pk)
            + "/delete_store/"
        )
        r = self.client.delete(
            url,
            {"user_id": self.managerUser.pk, "store_id": self.store3.pk},
            HTTP_AUTHORIZATION="Bearer " + self.manToken.token,
        )
        self.assertEqual(403, r.status_code)

    def test_delete_store_bad_store(self):
        url = (
            "http://127.0.0.1:8000/api/users/"
            + str(self.userMods.pk)
            + "/delete_store/"
        )
        r = self.client.delete(
            url,
            {"user_id": self.userMods.pk, "store_id": 100000000},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(403, r.status_code)

    def test_delete_store_bad_association(self):
        url = (
            "http://127.0.0.1:8000/api/users/"
            + str(self.userMods.pk)
            + "/delete_store/"
        )
        r = self.client.delete(
            url,
            {"user_id": self.userMods.pk, "store_id": self.store1.pk},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(404, r.status_code)
        self.assertEqual("The association does not exist.", r.data["message"])

    def test_delete_store_bad_role(self):
        url = (
            "http://127.0.0.1:8000/api/users/"
            + str(self.userMods.pk)
            + "/delete_store/"
        )
        r = self.client.delete(
            url,
            {"user_id": self.userMods.pk, "store_id": self.store3.pk},
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(503, r.status_code)
        self.assertEqual(
            "You don't have the permission to add an item", r.data["message"]
        )

    def test_change_role_no_association(self):
        url = "http://127.0.0.1:8000/api/users/change_role/"
        r = self.client.post(
            url,
            {
                "store_id": self.store2.pk,
                "role": Role.EMPLOYEE,
                "email": self.userMods.email,
            },
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual(
            1,
            Association.objects.filter(
                user=self.userMods, store=self.store2, role=Role.EMPLOYEE
            ).count(),
        )

    def test_change_role_pre_association(self):
        url = "http://127.0.0.1:8000/api/users/change_role/"
        r = self.client.post(
            url,
            {
                "store_id": self.store3.pk,
                "role": Role.MANAGER,
                "email": self.userMods.email,
            },
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual(
            1,
            Association.objects.filter(
                user=self.userMods, store=self.store3, role=Role.MANAGER
            ).count(),
        )

    def test_change_role_bad_user(self):
        url = "http://127.0.0.1:8000/api/users/change_role/"
        r = self.client.post(
            url,
            {
                "store_id": self.store2.pk,
                "role": Role.EMPLOYEE,
                "email": "bad@bad.com",
            },
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(404, r.status_code)
        self.assertEqual("The user does not exist.", r.data["message"])

    def test_change_role_bad_store(self):
        url = "http://127.0.0.1:8000/api/users/change_role/"
        r = self.client.post(
            url,
            {
                "store_id": 10000000,
                "role": Role.EMPLOYEE,
                "email": self.userMods.email,
            },
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(403, r.status_code)

    def test_change_role_bad_role(self):
        url = "http://127.0.0.1:8000/api/users/change_role/"
        r = self.client.post(
            url,
            {
                "store_id": self.store2.pk,
                "role": "Fake Role",
                "email": self.userMods.email,
            },
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(406, r.status_code)
        self.assertEqual("The role cannot be updated.", r.data["message"])

    def test_current_user(self):
        url = "http://127.0.0.1:8000/api/users/current_user/"
        r = self.client.get(
            url,
            HTTP_AUTHORIZATION="Bearer " + self.token.token,
        )
        self.assertEqual(200, r.status_code)
        self.assertEqual("superuserOAuth@email.com", r.data["email"])

    TEMP_EMAIL = "temp@email.com"
    TEMP_PASSWORD = "temp-password"

    def test_employee_add_user(self):
        token = self.token.token
        _ = Association.objects.create(
            user=self.employee_user, store=self.store1, role=Role.EMPLOYEE
        )
        url = f"http://127.0.0.1:8000/api/users/{self.employee_user.pk}/add_user_to_store/"
        r = self.client.post(
            url,
            {
                "store_id": self.store1.pk,
                "role": Role.EMPLOYEE,
                "email": self.TEMP_EMAIL,
                "password": self.TEMP_PASSWORD,
            },
            HTTP_AUTHORIZATION="Bearer " + token,
        )
        self.assertEqual(406, r.status_code)

    def test_manager_add_user(self):
        token = self.token.token
        _ = Association.objects.create(
            user=self.manager_user, store=self.store1, role=Role.MANAGER
        )
        url = (
            f"http://127.0.0.1:8000/api/users/{self.manager_user.pk}/add_user_to_store/"
        )
        r = self.client.post(
            url,
            {
                "store_id": self.store1.pk,
                "role": Role.EMPLOYEE,
                "email": self.TEMP_EMAIL+"1",
                "password": self.TEMP_PASSWORD,
            },
            HTTP_AUTHORIZATION="Bearer " + token,
        )
        self.assertEqual(406, r.status_code)

    def test_vendor_add_user(self):
        token = self.token.token
        _ = Association.objects.create(
            user=self.vendor_user, store=self.store1, role=Role.VENDOR
        )
        url = (
            f"http://127.0.0.1:8000/api/users/{self.vendor_user.pk}/add_user_to_store/"
        )
        r = self.client.post(
            url,
            {
                "store_id": self.store1.pk,
                "role": Role.EMPLOYEE,
                "email": self.TEMP_EMAIL+"1",
                "password": self.TEMP_PASSWORD,
            },
            HTTP_AUTHORIZATION="Bearer " + token,
        )
        self.assertEqual(201, r.status_code)
        r = self.client.post(
            url,
            {
                "store_id": self.store1.pk,
                "role": Role.MANAGER,
                "email": self.TEMP_EMAIL+"2",
                "password": self.TEMP_PASSWORD,
            },
            HTTP_AUTHORIZATION="Bearer " + token,
        )
        self.assertEqual(201, r.status_code)
        r = self.client.post(
            url,
            {
                "store_id": self.store1.pk,
                "role": Role.VENDOR,
                "email": self.TEMP_EMAIL+"3",
                "password": self.TEMP_PASSWORD,
            },
            HTTP_AUTHORIZATION="Bearer " + token,
        )
        self.assertEqual(201, r.status_code)

    def test_add_user_to_invalid_store(self):
        token = self.token.token
        _ = Association.objects.create(
            user=self.vendor_user, store=self.store1, role=Role.VENDOR
        )
        url = (
            f"http://127.0.0.1:8000/api/users/{self.vendor_user.pk}/add_user_to_store/"
        )
        r = self.client.post(
            url,
            {
                "store_id": self.store2.pk,
                "role": Role.EMPLOYEE,
                "email": self.TEMP_EMAIL,
                "password": self.TEMP_PASSWORD,
            },
            HTTP_AUTHORIZATION="Bearer " + token,
        )
        self.assertEqual(406, r.status_code)

    def test_invalid_user_adds_user(self):
        token = self.token.token
        # No association created
        url = (
            f"http://127.0.0.1:8000/api/users/{self.vendor_user.pk}/add_user_to_store/"
        )
        r = self.client.post(
            url,
            {
                "store_id": self.store1.pk,
                "role": Role.EMPLOYEE,
                "email": self.TEMP_EMAIL,
                "password": self.TEMP_PASSWORD,
            },
            HTTP_AUTHORIZATION="Bearer " + token,
        )
        self.assertEqual(406, r.status_code)

    def test_add_user_with_missing_fields(self):
        token = self.token.token
        _ = Association.objects.create(
            user=self.vendor_user, store=self.store1, role=Role.VENDOR
        )
        url = (
            f"http://127.0.0.1:8000/api/users/{self.vendor_user.pk}/add_user_to_store/"
        )
        r = self.client.post(
            url,
            {
                "store_id": self.store1.pk,
                "email": self.TEMP_EMAIL,
                "password": self.TEMP_PASSWORD,
            },
            HTTP_AUTHORIZATION="Bearer " + token,
        )
        self.assertEqual(406, r.status_code)
        r = self.client.post(
            url,
            {
                "store_id": self.store1.pk,
                "role": Role.EMPLOYEE,
                "password": self.TEMP_PASSWORD,
            },
            HTTP_AUTHORIZATION="Bearer " + token,
        )
        self.assertEqual(406, r.status_code)
        r = self.client.post(
            url,
            {
                "store_id": self.store1.pk,
                "role": Role.EMPLOYEE,
                "email": self.TEMP_EMAIL,
            },
            HTTP_AUTHORIZATION="Bearer " + token,
        )
        self.assertEqual(406, r.status_code)

    def test_adds_user_duplicate_email(self):
        token = self.token.token
        # No association created
        url = (
            f"http://127.0.0.1:8000/api/users/{self.vendor_user.pk}/add_user_to_store/"
        )
        r = self.client.post(
            url,
            {
                "store_id": self.store1.pk,
                "role": Role.EMPLOYEE,
                "email": self.userExists.email,
                "password": self.TEMP_PASSWORD,
            },
            HTTP_AUTHORIZATION="Bearer " + token,
        )
        self.assertEqual(406, r.status_code)
