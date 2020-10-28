from django.db import models
from jsonfield import JSONField

class Macros(models.Model):
    class Meta:
        verbose_name_plural = "Macros"
        verbose_name = "Macro"

    name = models.CharField(max_length=64, blank=False, unique=True)
    sequence = JSONField()

    def __str__(self):
        return self.name
