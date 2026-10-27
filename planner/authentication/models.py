from django.db import models

from django.contrib.auth.models import AbstractUser

# Create your models here.

class RoleChoices(models.TextChoices):

    USER='Developer','Developer'
    
    ADMIN='Admin','Admin'

    PROJECT_COORDINATOR='Project_Coordinator','Project_Coordinator'


class Profile(AbstractUser):

    role=models.CharField(max_length=20,choices=RoleChoices.choices)

    class Meta:

        verbose_name='Profiles'

        verbose_name_plural='Profiles'

    def __str__(self):
       
        return self.username            