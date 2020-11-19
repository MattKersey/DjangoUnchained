from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from api.models import User, Category, Store, Role, Association, Item
import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.conf import settings


# class Test_User_Model(TestCase):

#     def test_user(self):
#         user = User.objects.create_user(
#             email="test@email.com",
#             password="test@0987654321",
#             stores=None,
#         )
#         print(user.is_active)
#         self.assertTrue(user.is_active)
#         self.assertTrue(user.has_perm(perm=""))
#         self.assertTrue(user.has_perm(perm="", obj=""))
#         self.assertFalse(user.is_staff)
#         self.assertFalse(user.is_admin)
#         self.assertEqual(user.email, user.__str__())
#         self.assertEqual(1, User.objects.all().count())
#         other_user = User.objects.get(email="test@email.com")
#         self.assertEqual(user.id, other_user.id)
#         self.assertEqual(0, user.stores.count())

#     # @pytest.mark.django_db
#     def test_invalid_email(self):
#         sample_email = f"{'abc'*100}@email.com"
#         with self.assertRaises(ValidationError):
#             user = User.objects.create(
#                 email=sample_email,
#                 password="test@0987654321",
#             )
#             user.full_clean()

#     # @pytest.mark.django_db
#     def test_duplicate_email(self):
#         _ = User.objects.create_user(
#             email="test@email.com",
#             password="test@0987654321",
#         )
#         with self.assertRaises(IntegrityError):
#             _ = User.objects.create_user(
#                 email="test@email.com",
#                 password="test@0987654321",
#             )
    
#     def test_staffuser(self):
#         user = User.objects.create_staffuser(
#             email="test@email.com",
#             password="test@0987654321",
#             stores=None
#         )
#         self.assertTrue(user.is_active)
#         self.assertTrue(user.has_perm(perm=""))
#         self.assertTrue(user.has_perm(perm="", obj=""))
#         self.assertTrue(user.is_staff)
#         self.assertFalse(user.is_admin)
#         self.assertEqual(user.email, user.__str__())
#         self.assertEqual(0, user.stores.count())

#     def test_superuser(self):
#         user = User.objects.create_superuser(
#             email="test@email.com",
#             password="test@0987654321",
#             stores=None
#         )
#         self.assertTrue(user.is_active)
#         self.assertTrue(user.has_perm(perm=""))
#         self.assertTrue(user.has_perm(perm="", obj=""))
#         self.assertTrue(user.is_staff)
#         self.assertTrue(user.is_admin)
#         self.assertEqual(user.email, user.__str__())
#         self.assertEqual(0, user.stores.count())


# class Test_Item_Model(TestCase):

#     file_path = settings.BASE_DIR / "api/fixtures/food.jpeg"

#     def test_item(self):
#         with open(file=self.file_path, mode="rb") as infile:
#             file = SimpleUploadedFile(self.file_path, infile.read())
#             item = Item.objects.create(
#                 image=file,
#                 name="Item",
#                 stock=1,
#                 price=1.0,
#                 description="Item Description",
#             )
#             self.assertEqual(item.name, item.__str__())
#             self.assertEqual(item.stock, 1)
#             self.assertEqual(item.price, 1.0)
#             self.assertEqual(item.description, "Item Description")

#     def test_price_default(self):
#         with open(file=self.file_path, mode="rb") as infile:
#             file = SimpleUploadedFile(self.file_path, infile.read())
#             item = Item.objects.create(
#                 image=file,
#                 name="Item",
#                 stock=1,
#                 description="Item Description",
#             )
#             self.assertEqual(item.price, 0.0)
    
#     def test_invalid_name(self):
#         sample_name = f"{'abc'*100}"
#         with self.assertRaises(ValidationError):
#             with open(file=self.file_path, mode="rb") as infile:
#                 file = SimpleUploadedFile(self.file_path, infile.read())
#                 item = Item.objects.create(
#                     image=file,
#                     name=sample_name,
#                     stock=1,
#                     price=1.0,
#                     description="Item Description",
#                 )
#                 item.full_clean()
        
#     def test_invalid_stock(self):
#         sample_stock = -1
#         with self.assertRaises(ValidationError):
#             with open(file=self.file_path, mode="rb") as infile:
#                 file = SimpleUploadedFile(self.file_path, infile.read())
#                 item = Item.objects.create(
#                     image=file,
#                     name="Item",
#                     stock=sample_stock,
#                     price=1.0,
#                     description="Item Description",
#                 )
#                 item.full_clean()
        
#     def test_invalid_price(self):
#         sample_price = -1.0
#         with self.assertRaises(ValidationError):
#             with open(file=self.file_path, mode="rb") as infile:
#                 file = SimpleUploadedFile(self.file_path, infile.read())
#                 item = Item.objects.create(
#                     image=file,
#                     name="Item",
#                     stock=1,
#                     price=sample_price,
#                     description="Item Description",
#                 )
#                 item.full_clean()
        
#         sample_price = 1.123
#         with self.assertRaises(ValidationError):
#             with open(file=self.file_path, mode="rb") as infile:
#                 file = SimpleUploadedFile(self.file_path, infile.read())
#                 item = Item.objects.create(
#                     image=file,
#                     name="Item",
#                     stock=1,
#                     price=sample_price,
#                     description="Item Description",
#                 )
#                 item.full_clean()
        
#         sample_price = 1234567.123456
#         with self.assertRaises(ValidationError):
#             with open(file=self.file_path, mode="rb") as infile:
#                 file = SimpleUploadedFile(self.file_path, infile.read())
#                 item = Item.objects.create(
#                     image=file,
#                     name="Item",
#                     stock=1,
#                     price=sample_price,
#                     description="Item Description",
#                 )
#                 item.full_clean()

class Test_User_Model(TestCase):

    DEFAULT_NAME = "Store"
    DEFAULT_ADDRESS = "123 Lane"
    DEFAULT_CATEGORY = Category.FOOD
   
    def setup(self):
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
            stock=1,
            price=2.0,
            description="Item Description 2",
        )

    @pytest.mark.django_db
    def test_store(self):
        store = Store.objects.create(
            name=self.DEFAULT_NAME,
            address=self.DEFAULT_ADDRESS,
            category=self.DEFAULT_CATEGORY,
        )
        store.save()
        self.assertEqual(store.name, self.DEFAULT_NAME)
        self.assertEqual(store.address, self.DEFAULT_ADDRESS)
        self.assertEqual(store.category, self.DEFAULT_CATEGORY)
        self.assertEqual(2, Item.objects.all().count())
        # sample_item = Item.objects.get(name="Item 1")
        # store.items.set(sample_item)
        # print(store.items)