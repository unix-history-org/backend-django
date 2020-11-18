from django.db import models


class Photos(models.Model):
    path = models.CharField("Путь", max_length=100)

    class Meta:
        verbose_name = "Фото"
        verbose_name_plural = "Фото"


class Permiss(models.Model):
    livetime = models.DateTimeField("Время жизни")

    class Meta:
        verbose_name = "Права"
        verbose_name_plural = "Права"


class OS(models.Model):
    name = models.CharField("Название OC", max_length=100)
    html_text = models.TextField("HTML текст")
    photos = models.ForeignKey(Photos, verbose_name="Фото", on_delete=models.SET_NULL, null=True)
    config = models.CharField("Конфиг", max_length=255)
    ssh_enable = models.BooleanField("SSH активирован", default=False)
    vnc_enable = models.BooleanField("VNC активирован", default=False)
    permission = models.OneToOneField(Permiss, verbose_name="Права", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "ОС"
        verbose_name_plural = "ОС"


class User(models.Model):
    login = models.CharField("Логин", max_length=100)
    password = models.CharField("Пороль", max_length=100)
    current_os = models.ForeignKey(OS, verbose_name="Текущая ОС", on_delete=models.SET_NULL, null=True)
    avatar = models.OneToOneField(Photos, verbose_name="Аватар", on_delete=models.SET_NULL, null=True)
    is_admin = models.BooleanField("Админ")

    def __str__(self):
        return self.login

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
