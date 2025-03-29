from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    team_id = models.CharField(max_length=5, null=True, blank=True)
    
    def __str__(self):
        return f"{self.username} (Team: {self.team_id})"