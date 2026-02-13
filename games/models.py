from django.db import models

# Create your models here.

from django.db import models

class Game(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name
