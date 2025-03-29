from django.db import models
from django.contrib.auth.models import AbstractUser

# custom user model with team id
class CustomUser(AbstractUser):
    team_id = models.CharField(max_length=5, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.username and self.first_name and self.last_name:
            self.username = (self.first_name[0] + self.last_name).lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} (Team: {self.team_id})"