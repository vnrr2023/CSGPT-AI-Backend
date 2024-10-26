from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password.
        """
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


# Custom User Model
class CustomUser(AbstractUser):
    username = None  # Remove username field
    email = models.EmailField(_('email address'), unique=True)
    email_verified = models.BooleanField(_('email verified'), default=False)
    profile_pic_url = models.CharField(max_length=400, null=True, blank=True)
    
    # Custom related names to avoid reverse accessor conflicts
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',  # Change this to avoid clashes
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',  # Change this to avoid clashes
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    USERNAME_FIELD = 'email'  # Use email to log in
    REQUIRED_FIELDS = []  # No required fields except password

    objects = CustomUserManager()  # Use the custom manager

    def __str__(self):
        return self.email+"||"+str(self.id)


class Review(models.Model):
    name=models.CharField(max_length=200,null=True,blank=True)
    email=models.CharField(max_length=200,null=True,blank=True)
    feedback=models.TextField(null=True,blank=True)
    stars=models.CharField(max_length=5,null=True,blank=True)

    def __str__(self) -> str:
        return self.name
    
class Question(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_of_question=models.DateTimeField(null=True,blank=True)
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    text=models.TextField(null=True,blank=True)

    def __str__(self) -> str:
        return self.user.email
    

class UserInfo(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date=models.DateTimeField(null=True,blank=True)
    operating_system=models.CharField(max_length=100,null=True,blank=True)
    browser=models.CharField(max_length=100,null=True,blank=True)

    def __str__(self) -> str:
        return self.browser
    

class ResponseFeedback(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    like=models.IntegerField(default=0)
    dislike=models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.user.email+"   |  Like="+str(self.like)+"  |   dislike="+str(self.dislike)

    
