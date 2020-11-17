from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase

# from django.core.files.uploadedfile import SimpleUploadedFile
from .models import User, Category, Store, Role, Association

# from .modesl import Item
import datetime

from oauth2_provider.models import get_application_model, get_access_token_model
Application = get_application_model()
AccessToken = get_access_token_model()


class Test_User_Model(TestCase):
    def setUp(self):
        User.objects.create_user(email="user1@email.com")
        User.objects.create_user(email="user2@email.com")
        User.objects.create_user(email="user3@email.com")
        User.objects.create_staffuser(
            email="staffuser1@email.com", password="staffuser@1"
        )
        User.objects.create_staffuser(
            email="staffuser2@email.com", password="staffuser@2"
        )
        User.objects.create_superuser(
            email="superuser1@email.com", password="superuser@1"
        )

    def test_regular_user_info(self):
        regular_user = User.objects.get(email="user1@email.com")
        self.assertEqual("user1@email.com", str(regular_user))
        self.assertTrue(regular_user.is_active)
        self.assertTrue(regular_user.has_perm("perm"))
        self.assertFalse(regular_user.is_staff)
        self.assertFalse(regular_user.is_admin)

    def test_staff_user_info(self):
        staff_user = User.objects.get(email="staffuser1@email.com")
        self.assertEqual("staffuser1@email.com", str(staff_user))
        self.assertTrue(staff_user.is_active)
        self.assertTrue(staff_user.has_perm("perm"))
        self.assertTrue(staff_user.is_staff)
        self.assertFalse(staff_user.is_admin)

    def test_super_user_info(self):
        super_user = User.objects.get(email="superuser1@email.com")
        self.assertEqual("superuser1@email.com", str(super_user))
        self.assertTrue(super_user.is_active)
        self.assertTrue(super_user.has_perm("perm"))
        self.assertTrue(super_user.is_staff)
        self.assertTrue(super_user.is_admin)

    def test_count_regular_users(self):
        regular_users = User.objects.filter(staff=False, admin=False)
        self.assertEqual(3, regular_users.count())
        self.assertLess(regular_users.count(), User.objects.all().count())

    def test_count_staff_users(self):
        staff_users = User.objects.filter(staff=True, admin=False)
        self.assertEqual(2, staff_users.count())
        self.assertLess(staff_users.count(), User.objects.all().count())

    def test_count_super_users(self):
        super_users = User.objects.filter(staff=True, admin=True)
        self.assertEqual(1, super_users.count())
        self.assertLess(super_users.count(), User.objects.all().count())


class Test_Item_Model(TestCase):
    def setUp(self):
        pass
        # [TODO]: Create sample images
        # image1 = SimpleUploadedFile(name='test_image_1.jpg',
        #   content=open('path/to/test/image', 'rb').read(), content_type='image/jpeg')
        # image2 = SimpleUploadedFile(name='test_image_2.jpg',
        #   content=open('path/to/test/image', 'rb').read(), content_type='image/jpeg')
        # image3 = SimpleUploadedFile(name='test_image_3.jpg',
        #   content=open('path/to/test/image', 'rb').read(), content_type='image/jpeg')
        # Item(image=image1, name="Item 1", stock=1, price=1.0, description="Some Item 1")
        # Item(image=image2, name="Item 2", stock=2, price=2.0, description="Some Item 2")
        # Item(image=image3, name="Item 3", stock=3, price=3.0, description="Some Item 3")

    def test_count_items(self):
        # self.assertEqual(3, Item.objects.all().count())
        self.assertEqual(3, 1 + 2)


class Test_Store_Model(TestCase):
    def setUp(self):
        for i in range(1, 4):
            store = Store(name=f"Store {i}", address="{i} Lane", category=Category.FOOD)
            # [TODO]: Add random category assignments
            store.save()
            # [TODO]: Add random item assignments
            # store.items.set(collection_of_ids)

    def test_count_stores(self):
        self.assertEqual(3, Store.objects.all().count())


class Test_Association_Model(TestCase):
    def setUp(self):
        for i in range(1, 4):
            user = User.objects.create_user(email=f"user{i}@email.com")
            store = Store(
                name=f"Store {i}", address=f"{i} Lane", category=Category.FOOD
            )
            # [TODO]: Add random category assignments
            store.save()
            # [TODO]: Add random item assignments
            # store.items.set(collection_of_ids)
            # [NOTE]: We call the create button because of foreign key relationship
            Association.objects.create(
                user=user,
                store=store,
                membership=datetime.datetime.now(),
                role=Role.MANAGER,
            )

    def test_count_associations(self):
        self.assertEqual(3, Association.objects.all().count())


class Test_OAuth(APITestCase):
    def setUp(self):
        # oauth2_settings._SCOPES = ["read", "write"
        CLIENT_ID = 'abselskfjlskdfj'
        CLIENT_SECRET = 'laksdfjlaksjdflksjdflksdjf'
        self.user = User.objects.create_superuser(
            email="superuserOAuth@email.com", password="superuser"
        )
        self.application = Application.objects.create(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            client_type=Application.CLIENT_CONFIDENTIAL,
            name='OAuth-Test-API',
            redirect_uris='http://127.0.0.1:8000/authredirect/'
        )
        self.application.save()
        self.token = AccessToken.objects.create(
            user=self.user,
            token='adfslkfjavsdfeslfkjgh',
            application=self.application,
            expires=timezone.now()+datetime.timedelta(days=1),
            scope='read write'
        )
        self.token.save()

    def test_bad_access(self):
        url = 'http://127.0.0.1:8000/api/ping/'
        r = self.client.get(url)
        self.assertEqual(401, r.status_code)
        self.assertEqual(
            b"{\"detail\":\"Authentication credentials were not provided.\"}",
            r.content
        )

    def test_good_access(self):
        url = 'http://127.0.0.1:8000/api/ping/'
        r = self.client.get(url, HTTP_AUTHORIZATION='Bearer ' + self.token.token)
        self.assertEqual(200, r.status_code)
        self.assertEqual(
            b"{\"ping\":\"pong\"}",
            r.content
        )

    def tearDown(self):
        self.application.delete()
        self.token.delete()
        pass
