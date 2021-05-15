from django.db import models
from core.models import Photos


class EMULATIONCHOICE(models.IntegerChoices):
    NO = -1
    QEMU_KVM = 1


class SSHTYPECHOICE(models.IntegerChoices):
    SSH = 1
    RAW_CONSOLE = 2


class Permiss(models.Model): # TODO: rename this
    live_time = models.DurationField(verbose_name="Время жизни")

    class Meta:
        verbose_name = "Права"
        verbose_name_plural = "Права"


class OS(models.Model):
    name = models.CharField(verbose_name="Название OC", max_length=500)
    version = models.CharField(verbose_name="Версия ОС", max_length=500, null=True, blank=True)
    vendor = models.CharField(verbose_name="Создатель ОС", max_length=500, null=True, blank=True)
    html_text = models.TextField(verbose_name="HTML текст")
    photos = models.ForeignKey(Photos, verbose_name="Фото", on_delete=models.SET_NULL, null=True, blank=True)
    start_config = models.TextField(verbose_name="Конфигурация запуска", max_length=50000, null=True, blank=True)
    stop_config = models.TextField(verbose_name="Конфигурация остановки", max_length=50000, null=True, blank=True)
    ssh_enable = models.BooleanField(verbose_name="SSH активирован", default=False)
    vnc_enable = models.BooleanField(verbose_name="VNC активирован", default=False)
    permission = models.OneToOneField(Permiss, verbose_name="Права", on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(verbose_name="Активна", default=True)
    emulation_type = models.IntegerField(verbose_name="Тип эмуляции", choices=EMULATIONCHOICE.choices,
                                         default=EMULATIONCHOICE.NO)
    ssh_type = models.IntegerField(verbose_name="Тип консольного подключения", choices=SSHTYPECHOICE.choices, null=True)
    wait_time = models.IntegerField(verbose_name="Время ожидания", default=60)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "ОС"
        verbose_name_plural = "ОС"
