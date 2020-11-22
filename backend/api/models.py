from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.validators import MinValueValidator
from django.contrib.auth.models import PermissionsMixin


class OrderType(models.TextChoices):
    INDIVIDUAL = "Individual"
    BULK = "Bulk"
    BOTH = "Both"


class History_of_Item(models.Model):
    before_name = models.CharField(max_length=50, blank=True, null=True)
    after_name = models.CharField(max_length=50, blank=True, null=True)
    before_price = models.DecimalField(
        validators=[MinValueValidator(limit_value=0.0)],
        decimal_places=2,
        max_digits=12,
        blank=True,
        null=True,
    )
    after_price = models.DecimalField(
        validators=[MinValueValidator(limit_value=0.0)],
        decimal_places=2,
        max_digits=12,
        blank=True,
        null=True,
    )
    before_stock = models.IntegerField(
        validators=[MinValueValidator(limit_value=0)], blank=True, null=True
    )
    after_stock = models.IntegerField(
        validators=[MinValueValidator(limit_value=0)], blank=True, null=True
    )
    before_description = models.TextField(blank=True, null=True)
    after_description = models.TextField(blank=True, null=True)
    datetime = models.DateTimeField(auto_now=True)


class Item(models.Model):
    image = models.ImageField(null=True, blank=True, upload_to="items")
    name = models.CharField(max_length=50)
    stock = models.IntegerField(validators=[MinValueValidator(limit_value=0)])
    price = models.DecimalField(
        null=True,
        blank=True,
        default=0.0,
        validators=[MinValueValidator(limit_value=0.0)],
        decimal_places=2,
        max_digits=12,
    )
    orderType = models.CharField(
        choices=OrderType.choices, max_length=10, default=OrderType.INDIVIDUAL
    )
    bulkMinimum = models.IntegerField(validators=[MinValueValidator(limit_value=0)], default=0)
    bulkPrice = models.DecimalField(
        null=True,
        blank=True,
        default=0.0,
        validators=[MinValueValidator(limit_value=0.0)],
        decimal_places=2,
        max_digits=12,
    )
    description = models.TextField()
    history = models.ManyToManyField(History_of_Item)

    def __str__(self):
        return self.name


class Category(models.TextChoices):
    FOOD = "Food"
    CLOTHING = "Clothing"
    OTHER = "Other"


class Store(models.Model):
    address = models.TextField()
    name = models.CharField(max_length=50)
    category = models.CharField(
        choices=Category.choices, max_length=10, default=Category.OTHER
    )
    items = models.ManyToManyField(Item)

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, is_superuser=False, stores=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            is_superuser=is_superuser,
        )
        user.set_password(password)
        user.save(using=self._db)
        if stores is not None:
            user.stores.set(stores)
            user.save()
        return user

    def create_staffuser(self, email, password, stores=None):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
            is_superuser=False,
            stores=stores,
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, stores=None):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
            is_superuser=True,
            stores=None,
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = None
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    # password is built-in
    stores = models.ManyToManyField(Store, through="Association")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    # email and password are required by default.

    objects = UserManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # return True for now
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.staff

    @property
    def is_admin(self):
        "Is the user a admin member?"
        return self.admin

    @property
    def is_active(self):
        "Is the user active?"
        return self.active


class Role(models.TextChoices):
    MANAGER = "Manager"
    VENDOR = "Vendor"
    EMPLOYEE = "Employee"


class Association(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    membership = models.DateField(auto_now=True)
    role = models.CharField(choices=Role.choices, max_length=10, default=Role.EMPLOYEE)

    def __str__(self):
        return f"[{self.role}] {self.user} --> {self.store.name}"
