from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from api.models import User, Category, Store, Item, Association, Role
import pytest
from datetime import datetime
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.conf import settings

TEST_USER_EMAIL = "test@email.com"
TEST_USER_PASSWORD = "test@0987"


class Test_User_Model(TestCase):
    def test_user(self):
        user = User.objects.create_user(
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD,
            stores=None,
        )
        print(user.is_active)
        self.assertTrue(user.is_active)
        self.assertTrue(user.has_perm(perm=""))
        self.assertTrue(user.has_perm(perm="", obj=""))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_admin)
        self.assertEqual(user.email, user.__str__())
        self.assertEqual(1, User.objects.all().count())
        other_user = User.objects.get(email=TEST_USER_EMAIL)
        self.assertEqual(user.id, other_user.id)
        self.assertEqual(0, user.stores.count())

    # @pytest.mark.django_db
    def test_invalid_email(self):
        sample_email = f"{'abc'*100}@email.com"
        with self.assertRaises(ValidationError):
            user = User.objects.create(
                email=sample_email,
                password=TEST_USER_PASSWORD,
            )
            user.full_clean()

    # @pytest.mark.django_db
    def test_duplicate_email(self):
        _ = User.objects.create_user(
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD,
        )
        with self.assertRaises(IntegrityError):
            _ = User.objects.create_user(
                email=TEST_USER_EMAIL,
                password=TEST_USER_PASSWORD,
            )

    def test_staffuser(self):
        user = User.objects.create_staffuser(
            email=TEST_USER_EMAIL, password=TEST_USER_PASSWORD, stores=None
        )
        self.assertTrue(user.is_active)
        self.assertTrue(user.has_perm(perm=""))
        self.assertTrue(user.has_perm(perm="", obj=""))
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_admin)
        self.assertEqual(user.email, user.__str__())
        self.assertEqual(0, user.stores.count())

    def test_superuser(self):
        user = User.objects.create_superuser(
            email=TEST_USER_EMAIL, password=TEST_USER_PASSWORD, stores=None
        )
        self.assertTrue(user.is_active)
        self.assertTrue(user.has_perm(perm=""))
        self.assertTrue(user.has_perm(perm="", obj=""))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_admin)
        self.assertEqual(user.email, user.__str__())
        self.assertEqual(0, user.stores.count())


TEST_ITEM_NAME = "Item"
TEST_ITEM_DESCRIPTION = "Item Description"
TEST_ITEM_STOCK = 1
TEST_ITEM_PRICE = 1.0


class Test_Item_Model(TestCase):

    file_path = settings.BASE_DIR / "api/fixtures/food.jpeg"

    def test_item(self):
        with open(file=self.file_path, mode="rb") as infile:
            file = SimpleUploadedFile(self.file_path, infile.read())
            item = Item.objects.create(
                image=file,
                name=TEST_ITEM_NAME,
                stock=TEST_ITEM_STOCK,
                price=TEST_ITEM_PRICE,
                description=TEST_ITEM_DESCRIPTION,
            )
            self.assertEqual(item.name, item.__str__())
            self.assertEqual(item.stock, TEST_ITEM_STOCK)
            self.assertEqual(item.price, TEST_ITEM_PRICE)
            self.assertEqual(item.description, TEST_ITEM_DESCRIPTION)

    def test_price_default(self):
        with open(file=self.file_path, mode="rb") as infile:
            file = SimpleUploadedFile(self.file_path, infile.read())
            item = Item.objects.create(
                image=file,
                name=TEST_ITEM_NAME,
                stock=TEST_ITEM_STOCK,
                description=TEST_ITEM_DESCRIPTION,
            )
            self.assertEqual(item.price, 0.0)

    def test_invalid_name(self):
        sample_name = f"{'abc'*100}"
        with self.assertRaises(ValidationError):
            with open(file=self.file_path, mode="rb") as infile:
                file = SimpleUploadedFile(self.file_path, infile.read())
                item = Item.objects.create(
                    image=file,
                    name=sample_name,
                    stock=TEST_ITEM_STOCK,
                    price=TEST_ITEM_PRICE,
                    description=TEST_ITEM_DESCRIPTION,
                )
                item.full_clean()

    def test_invalid_stock(self):
        sample_stock = -1
        with self.assertRaises(ValidationError):
            with open(file=self.file_path, mode="rb") as infile:
                file = SimpleUploadedFile(self.file_path, infile.read())
                item = Item.objects.create(
                    image=file,
                    name=TEST_ITEM_NAME,
                    stock=sample_stock,
                    price=TEST_ITEM_PRICE,
                    description=TEST_ITEM_DESCRIPTION,
                )
                item.full_clean()

    def test_invalid_price(self):
        sample_price = -1.0
        with self.assertRaises(ValidationError):
            with open(file=self.file_path, mode="rb") as infile:
                file = SimpleUploadedFile(self.file_path, infile.read())
                item = Item.objects.create(
                    image=file,
                    name=TEST_ITEM_NAME,
                    stock=TEST_ITEM_STOCK,
                    price=sample_price,
                    description=TEST_ITEM_DESCRIPTION,
                )
                item.full_clean()

        sample_price = 1.123
        with self.assertRaises(ValidationError):
            with open(file=self.file_path, mode="rb") as infile:
                file = SimpleUploadedFile(self.file_path, infile.read())
                item = Item.objects.create(
                    image=file,
                    name=TEST_ITEM_NAME,
                    stock=TEST_ITEM_STOCK,
                    price=sample_price,
                    description=TEST_ITEM_DESCRIPTION,
                )
                item.full_clean()

        sample_price = 1234567.123456
        with self.assertRaises(ValidationError):
            with open(file=self.file_path, mode="rb") as infile:
                file = SimpleUploadedFile(self.file_path, infile.read())
                item = Item.objects.create(
                    image=file,
                    name=TEST_ITEM_NAME,
                    stock=TEST_ITEM_STOCK,
                    price=sample_price,
                    description=TEST_ITEM_DESCRIPTION,
                )
                item.full_clean()


TEST_STORE_NAME = "Store"
TEST_STORE_ADDRESS = "123 Lane"
TEST_STORE_CATEGORY = Category.FOOD


class Test_Store_Model(TestCase):
    def setUp(self):
        file_path = settings.BASE_DIR / "api/fixtures/food.jpeg"
        file = None
        with open(file=file_path, mode="rb") as infile:
            file = SimpleUploadedFile(file_path, infile.read())
        _ = Item.objects.create(
            image=file,
            name="Item 1",
            stock=1,
            price=1.0,
            description="Item Description 1",
        )

        _ = Item.objects.create(
            image=file,
            name="Item 2",
            stock=2,
            price=2.0,
            description="Item Description 2",
        )

    @pytest.mark.django_db
    def test_store(self):
        store = Store.objects.create(
            name=TEST_STORE_NAME,
            address=TEST_STORE_ADDRESS,
            category=TEST_STORE_CATEGORY,
        )
        store.save()
        self.assertEqual(store.name, TEST_STORE_NAME)
        self.assertEqual(store.__str__(), TEST_STORE_NAME)
        self.assertEqual(store.address, TEST_STORE_ADDRESS)
        self.assertEqual(store.category, TEST_STORE_CATEGORY)
        self.assertEqual(2, Item.objects.all().count())
        sample_item = Item.objects.get(name="Item 1")
        store.items.add(sample_item)
        self.assertEqual(1, store.items.count())


TEST_ASSOCIATION_ROLE = Role.EMPLOYEE


class Test_Association_Model(TestCase):

    def setUp(self):
        file_path = settings.BASE_DIR / "api/fixtures/food.jpeg"
        file = None
        with open(file=file_path, mode="rb") as infile:
            file = SimpleUploadedFile(file_path, infile.read())
        self.item = Item.objects.create(
            image=file,
            name=TEST_ITEM_NAME,
            stock=TEST_ITEM_STOCK,
            price=TEST_ITEM_PRICE,
            description=TEST_ITEM_DESCRIPTION,
        )
        self.store = Store.objects.create(
            name=TEST_STORE_NAME,
            address=TEST_STORE_ADDRESS,
            category=TEST_STORE_CATEGORY,
        )
        self.store.save()
        self.store.items.add(self.item)
        self.store.save()
        self.user = User.objects.create_user(
            email=TEST_USER_EMAIL, password=TEST_USER_PASSWORD
        )

    def test_association(self):
        time = datetime.now().date()
        association = Association.objects.create(
            user=self.user,
            store=self.store,
            membership=time,
            role=TEST_ASSOCIATION_ROLE,
        )
        self.assertEqual(association.user, self.user)
        self.assertEqual(association.store, self.store)
        self.assertEqual(association.role, TEST_ASSOCIATION_ROLE)
        self.assertEqual(association.membership, time)
