from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.validators import MinValueValidator
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError


class OrderType(models.TextChoices):
    INDIVIDUAL = "Individual"
    BULK = "Bulk"
    BOTH = "Both"


class History_Category(models.TextChoices):
    UPDATE = "Update"
    PURCHASE = "Purchase"
    REMOVAL = "Removal"
    ADDITION = "Addition"


class History_of_Item(models.Model):
    category = models.CharField(
        choices=History_Category.choices, max_length=10, default=History_Category.UPDATE
    )
    before_image = models.TextField(null=True, blank=True)
    after_image = models.TextField(null=True, blank=True)
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
    before_orderType = models.CharField(
        choices=OrderType.choices, max_length=10, blank=True, null=True
    )
    after_orderType = models.CharField(
        choices=OrderType.choices, max_length=10, blank=True, null=True
    )
    before_bulkMinimum = models.IntegerField(
        validators=[MinValueValidator(limit_value=0)], blank=True, null=True
    )
    after_bulkMinimum = models.IntegerField(
        validators=[MinValueValidator(limit_value=0)], blank=True, null=True
    )
    before_bulkPrice = models.DecimalField(
        validators=[MinValueValidator(limit_value=0.0)],
        decimal_places=2,
        max_digits=12,
        blank=True,
        null=True,
    )
    after_bulkPrice = models.DecimalField(
        validators=[MinValueValidator(limit_value=0.0)],
        decimal_places=2,
        max_digits=12,
        blank=True,
        null=True,
    )
    before_description = models.TextField(blank=True, null=True)
    after_description = models.TextField(blank=True, null=True)
    datetime = models.DateTimeField(auto_now=True)


class Item(models.Model):
    image = models.TextField(null=True, blank=True)
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
    bulkMinimum = models.IntegerField(
        validators=[MinValueValidator(limit_value=0)], default=0
    )
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

    def clean(self):
        if self.orderType in [OrderType.INDIVIDUAL, OrderType.BOTH]:
            if self.price is None:
                raise ValidationError("Missing (Regular) Price for Item")

        if self.orderType == OrderType.INDIVIDUAL:
            if self.bulkPrice or self.bulkMinimum:
                raise ValidationError("Included Bulk attributes for Item")

        if self.orderType in [OrderType.BULK, OrderType.BOTH]:
            if self.bulkPrice is None or self.bulkMinimum is None:
                raise ValidationError("Missing Bulk attributes for Item")

        if self.orderType == OrderType.BOTH:
            if self.bulkPrice > self.price:
                raise ValidationError("Bulk Price cannot exceed (Regular) Price")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Item, self).save(*args, **kwargs)


class Category(models.TextChoices):
    FOOD = "Food"
    CLOTHING = "Clothing"
    OTHER = "Other"


class Store(models.Model):
    address = models.TextField()
    name = models.CharField(max_length=50)
    category = models.CharField(
        choices=Category.choices, max_length=20, default=Category.OTHER
    )
    items = models.ManyToManyField(Item)
    other_category = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name

    def clean(self):
        if self.category != Category.OTHER and self.other_category:
            raise ValidationError("Cannot have other_cateogry for non-other category")
        if self.category == Category.OTHER and self.other_category is None:
            raise ValidationError("Must define a category")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Store, self).save(*args, **kwargs)

    def validate_and_add_item(self, item):
        if item.name in self.items.values_list("name", flat=True):
            raise ValidationError(
                f"Item with same name '{item.name}' already part of store"
            )
        else:
            self.items.add(item)
            self.save()


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
        if password is None:
            raise ValueError("Users must have a password")
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
        if password is None:
            raise ValueError("Users must have a password")
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

    def can_add_user(self, user, store, new_user_role):
        try:
            assoc = Association.objects.get(user=user, store=store)
        except Association.DoesNotExist:
            return False
        if assoc.role == Role.EMPLOYEE:
            return False
        elif assoc.role == Role.MANAGER:
            return new_user_role in [Role.MANAGER, Role.EMPLOYEE]
        elif assoc.role == Role.VENDOR:
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
    role = models.CharField(choices=Role.choices, max_length=10, default=Role.MANAGER)

    def __str__(self):
        return f"[{self.role}] {self.user} --> {self.store.name}"
