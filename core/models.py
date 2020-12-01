from django.db import models


class Photos(models.Model):
    path = models.CharField(verbose_name="Путь", max_length=100)

    class Meta:
        verbose_name = "Фото"
        verbose_name_plural = "Фото"
