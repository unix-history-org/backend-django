from django.db import models

from core.models import Photos


class Permiss(models.Model):  # TODO: rename this
    live_time = models.DateTimeField(verbose_name="Время жизни")

    class Meta:
        verbose_name = "Права"
        verbose_name_plural = "Права"


class OS(models.Model):
    name = models.CharField(verbose_name="Название OC", max_length=500)
    version = models.CharField(verbose_name="Версия ОС", max_length=500, null=True, blank=True)
    vendor = models.CharField(verbose_name="Создатель ОС", max_length=500, null=True, blank=True)
    html_text = models.TextField(verbose_name="HTML текст")
    photos = models.ForeignKey(Photos, verbose_name="Фото", on_delete=models.SET_NULL, null=True, blank=True)
    config = models.TextField(verbose_name="Конфиг", max_length=50000, null=True, blank=True)
    ssh_enable = models.BooleanField(verbose_name="SSH активирован", default=False)
    vnc_enable = models.BooleanField(verbose_name="VNC активирован", default=False)
    permission = models.OneToOneField(Permiss, verbose_name="Права", on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(verbose_name="Активна", default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "ОС"
        verbose_name_plural = "ОС"
