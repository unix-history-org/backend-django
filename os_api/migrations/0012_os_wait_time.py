# Generated by Django 3.1.4 on 2021-05-15 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('os_api', '0011_os_ssh_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='os',
            name='wait_time',
            field=models.IntegerField(default=60, verbose_name='Время ожидания'),
        ),
    ]