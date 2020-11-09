from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.validators import MinValueValidator


class Item(models.Model):
    image = models.ImageField(upload_to="items")
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
    description = models.TextField()


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


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
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
