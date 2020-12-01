from rest_framework import serializers

from os_api.models import OS


class OSListSerializer(serializers.ModelSerializer):
    class Meta:
        depth = 2
        model = OS
        fields = ("id", "name", "html_text", "photos", "ssh_enable", "vnc_enable", "version", "vendor")
